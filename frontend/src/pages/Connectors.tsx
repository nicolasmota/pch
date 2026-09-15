import { FormEvent, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api, errorMessage } from "../api/client";
import type { ConnectorAccount } from "../api/types";
import Alert from "../components/Alert";
import Button from "../components/Button";
import Card from "../components/Card";
import ConfirmDialog from "../components/ConfirmDialog";
import Field from "../components/Field";
import Input from "../components/Input";
import PageHeader from "../components/PageHeader";
import Select from "../components/Select";

function csvList(value: unknown): string {
  if (!Array.isArray(value)) return "";
  return value.filter((item): item is string => typeof item === "string").join(", ");
}

function parseCsv(value: string): string[] {
  return value.split(",").map((item) => item.trim()).filter(Boolean);
}

function lastSyncLine(item: ConnectorAccount): string {
  const sync = item.last_sync;
  if (!sync?.at) return "Last sync: never";
  return (
    `Last sync: ${sync.at} (${sync.outcome || "—"}) · ` +
    `${sync.created ?? 0} created, ${sync.updated ?? 0} updated`
  );
}

function EmailFilter({
  item,
  busy,
  setBusy,
  onSaved,
  onError,
}: {
  item: ConnectorAccount;
  busy: boolean;
  setBusy: (value: boolean) => void;
  onSaved: (message: string) => Promise<void>;
  onError: (message: string) => void;
}) {
  const sel = item.selection || {};
  const [labels, setLabels] = useState(csvList(sel.labels));
  const [senders, setSenders] = useState(csvList(sel.senders));
  const [after, setAfter] = useState(typeof sel.after === "string" ? sel.after : "");

  async function save() {
    setBusy(true);
    try {
      await api(`/v1/connectors/${item.id}`, {
        method: "PATCH",
        body: JSON.stringify({
          selection: {
            labels: parseCsv(labels),
            senders: parseCsv(senders),
            after: after || undefined,
          },
        }),
      });
      await onSaved("Filter saved. Click Sync now to import matching mail.");
    } catch (err) {
      onError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-3">
      <Field
        id={`${item.id}-labels`}
        label="Labels"
        hint="Leave empty to import all mail since the date below (spam/trash excluded)."
      >
        <Input
          id={`${item.id}-labels`}
          value={labels}
          onChange={(e) => setLabels(e.target.value)}
          placeholder="optional"
        />
      </Field>
      <Field id={`${item.id}-senders`} label="Senders">
        <Input id={`${item.id}-senders`} value={senders} onChange={(e) => setSenders(e.target.value)} />
      </Field>
      <Field
        id={`${item.id}-after`}
        label="After date (YYYY-MM-DD)"
        hint="Required if labels and senders are empty. Example: 2026-01-01"
      >
        <Input id={`${item.id}-after`} value={after} onChange={(e) => setAfter(e.target.value)} />
      </Field>
      <Button variant="secondary" onClick={() => void save()} disabled={busy}>
        Save filter
      </Button>
    </div>
  );
}

export default function Connectors() {
  const [items, setItems] = useState<ConnectorAccount[]>([]);
  const [kind, setKind] = useState<"calendar" | "email">("calendar");
  const [labels, setLabels] = useState("");
  const [senders, setSenders] = useState("");
  const [after, setAfter] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);
  const [pendingDisconnect, setPendingDisconnect] = useState<ConnectorAccount | null>(null);
  const [purge, setPurge] = useState(false);
  const [oauthReady, setOauthReady] = useState<boolean | null>(null);
  const [clientId, setClientId] = useState("");
  const [clientSecret, setClientSecret] = useState("");
  const [params] = useSearchParams();
  const justConnected = params.get("connected") === "1";

  async function refresh() {
    setItems(await api<ConnectorAccount[]>("/v1/connectors"));
  }

  useEffect(() => {
    let cancelled = false;
    api<ConnectorAccount[]>("/v1/connectors")
      .then((rows) => {
        if (!cancelled) setItems(rows);
      })
      .catch(() => {
        if (!cancelled) setItems([]);
      });
    api<{ configured: boolean }>("/v1/connectors/oauth/status")
      .then((data) => {
        if (!cancelled) setOauthReady(data.configured);
      })
      .catch(() => {
        if (!cancelled) setOauthReady(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  async function connect(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    setMsg("");
    try {
      if (!oauthReady) {
        if (!clientId.trim()) {
          setError("Paste your Google Desktop OAuth client ID first.");
          return;
        }
        await api("/v1/connectors/oauth/credentials", {
          method: "PUT",
          body: JSON.stringify({ client_id: clientId.trim(), client_secret: clientSecret.trim() }),
        });
        setOauthReady(true);
      }
      const selection =
        kind === "email"
          ? {
              labels: labels.split(",").map((s) => s.trim()).filter(Boolean),
              senders: senders.split(",").map((s) => s.trim()).filter(Boolean),
              after: after || undefined,
            }
          : { calendar_ids: ["primary"] };
      const data = await api<{ consent_url: string; connector_id: string }>("/v1/connectors", {
        method: "POST",
        body: JSON.stringify({ provider: "google", kind, selection }),
      });
      setMsg("Consent started. Finish sign-in in the browser, then refresh this page.");
      window.open(data.consent_url, "_blank", "noopener");
      await refresh();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function syncNow(id: string) {
    setBusy(true);
    setError(null);
    try {
      const summary = await api<{ created?: number; updated?: number; outcome?: string }>(
        `/v1/connectors/${id}/sync`,
        { method: "POST", body: "{}" },
      );
      await refresh();
      setMsg(
        `Sync complete (${summary.outcome || "ok"}): ${summary.created ?? 0} created, ${summary.updated ?? 0} updated.`,
      );
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function pauseOrResume(item: ConnectorAccount) {
    const path = item.status === "paused" ? "resume" : "pause";
    setBusy(true);
    try {
      await api(`/v1/connectors/${item.id}/${path}`, { method: "POST", body: "{}" });
      await refresh();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function disconnect() {
    if (!pendingDisconnect) return;
    setBusy(true);
    try {
      await api(`/v1/connectors/${pendingDisconnect.id}?purge=${purge}`, { method: "DELETE" });
      setPendingDisconnect(null);
      await refresh();
      setMsg("Connector deleted.");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="space-y-6">
      <PageHeader
        title="Connectors"
        description="Legacy Google connect flow. Calendar and Gmail now live under Plugins after Hub upgrade."
      />
      <Alert tone="info">
        Prefer <a className="underline" href="/plugins">Plugins</a> for install, consent, pause, and removal. This
        page remains for leftover 002-style connections that have not migrated.
      </Alert>
      {error ? <Alert tone="error">{error}</Alert> : null}
      {justConnected ? (
        <Alert tone="success">
          Google is connected. Click Sync now on the card to import matching items.
        </Alert>
      ) : null}
      {msg ? <Alert tone="success">{msg}</Alert> : null}
      {oauthReady === false ? (
        <Alert tone="info">
          Paste a Google Desktop OAuth client ID below (from Google Cloud Console, with Calendar
          API and Gmail API enabled). Redirect URI:{" "}
          <code>http://127.0.0.1:8765/v1/connectors/oauth/callback</code>
        </Alert>
      ) : null}
      <Card>
        <form className="space-y-4" onSubmit={connect}>
          {oauthReady !== true ? (
            <>
              <Field
                id="cx-client-id"
                label="Google client ID"
                hint="Ends with .apps.googleusercontent.com"
              >
                <Input
                  id="cx-client-id"
                  value={clientId}
                  onChange={(e) => setClientId(e.target.value)}
                  autoComplete="off"
                />
              </Field>
              <Field id="cx-client-secret" label="Google client secret" hint="Shown next to the client ID for Desktop apps.">
                <Input
                  id="cx-client-secret"
                  value={clientSecret}
                  onChange={(e) => setClientSecret(e.target.value)}
                  autoComplete="off"
                />
              </Field>
            </>
          ) : null}
          <Field id="cx-kind" label="Source">
            <Select
              id="cx-kind"
              value={kind}
              onChange={(e) => setKind(e.target.value === "email" ? "email" : "calendar")}
            >
              <option value="calendar">Google Calendar</option>
              <option value="email">Gmail (selective)</option>
            </Select>
          </Field>
          {kind === "email" ? (
            <>
              <Field
                id="cx-labels"
                label="Labels"
                hint="Leave empty to import all mail since the date. Required unless you set senders or a date."
              >
                <Input
                  id="cx-labels"
                  value={labels}
                  onChange={(e) => setLabels(e.target.value)}
                  placeholder="optional"
                />
              </Field>
              <Field id="cx-senders" label="Senders">
                <Input id="cx-senders" value={senders} onChange={(e) => setSenders(e.target.value)} />
              </Field>
              <Field id="cx-after" label="After date (YYYY-MM-DD)" hint="Example: 2026-01-01">
                <Input id="cx-after" value={after} onChange={(e) => setAfter(e.target.value)} />
              </Field>
            </>
          ) : null}
          <Button type="submit" disabled={busy}>
            Connect
          </Button>
        </form>
      </Card>
      {items.map((item) => (
        <Card key={item.id} className="space-y-2">
          <p className="font-medium text-ink">
            {item.kind} · {item.status}
          </p>
          <p className="text-sm text-muted">{lastSyncLine(item)}</p>
          {item.kind === "email" &&
          item.last_sync?.outcome === "ok" &&
          (item.last_sync.created ?? 0) === 0 ? (
            <p className="text-sm text-muted">
              No messages matched this filter. Check the exact Gmail label name, then save and sync.
            </p>
          ) : null}
          {item.kind === "email" ? (
            <EmailFilter
              key={`${item.id}:${JSON.stringify(item.selection)}`}
              item={item}
              busy={busy}
              setBusy={setBusy}
              onSaved={async (message) => {
                setError(null);
                await refresh();
                setMsg(message);
              }}
              onError={(message) => {
                setMsg("");
                setError(message);
              }}
            />
          ) : null}
          <div className="flex flex-wrap gap-2">
            <Button
              onClick={() => syncNow(item.id)}
              disabled={busy || item.status !== "active"}
            >
              Sync now
            </Button>
            <Button variant="secondary" onClick={() => pauseOrResume(item)} disabled={busy}>
              {item.status === "paused" ? "Resume" : "Pause"}
            </Button>
            <Button variant="danger" onClick={() => setPendingDisconnect(item)} disabled={busy}>
              Delete
            </Button>
          </div>
        </Card>
      ))}
      <ConfirmDialog
        open={Boolean(pendingDisconnect)}
        title="Delete connector"
        message="This connection is removed from the Hub. Imported items stay unless you choose to delete them too."
        confirmLabel="Delete"
        danger
        busy={busy}
        onConfirm={disconnect}
        onCancel={() => {
          setPendingDisconnect(null);
          setPurge(false);
        }}
      >
        <label className="mt-3 flex items-center gap-2 text-sm text-ink">
          <input type="checkbox" checked={purge} onChange={(e) => setPurge(e.target.checked)} />
          Also delete imported calendar/email items
        </label>
      </ConfirmDialog>
    </section>
  );
}

import { useEffect, useState } from "react";
import { api, errorMessage } from "../api/client";
import Alert from "../components/Alert";
import Button from "../components/Button";
import Card from "../components/Card";
import ConfirmDialog from "../components/ConfirmDialog";
import PageHeader from "../components/PageHeader";

type PluginRow = {
  id: string | null;
  plugin_id: string;
  plugin_version?: string;
  state: string;
  origin?: string;
  isolation?: string;
  last_run?: { at?: string; outcome?: string; created?: number; updated?: number };
  manifest?: { name?: string; description?: string };
};

type ConsentPreview = {
  text: string;
  warnings?: string[];
  unverified?: boolean;
};

export default function Plugins() {
  const [items, setItems] = useState<PluginRow[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);
  const [consent, setConsent] = useState<{ id: string; preview: ConsentPreview } | null>(null);
  const [pending, setPending] = useState<PluginRow | null>(null);
  const [purge, setPurge] = useState(false);

  async function refresh() {
    const data = await api<PluginRow[]>("/v1/plugins");
    setItems(data);
  }

  useEffect(() => {
    refresh().catch((err) => setError(errorMessage(err)));
  }, []);

  async function installBundled(pluginId: string) {
    setBusy(true);
    setError(null);
    try {
      const inst = await api<PluginRow>("/v1/plugins", {
        method: "POST",
        body: JSON.stringify({ source: "bundled", plugin_id: pluginId }),
      });
      const preview = await api<ConsentPreview>(`/v1/plugins/${inst.id}/consent`);
      setConsent({ id: inst.id as string, preview });
      await refresh();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function approve() {
    if (!consent) return;
    setBusy(true);
    try {
      await api(`/v1/plugins/${consent.id}/consent`, { method: "POST", body: "{}" });
      setConsent(null);
      await refresh();
      setMsg("Plugin enabled.");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function syncNow(id: string) {
    setBusy(true);
    try {
      const summary = await api<{ created?: number; updated?: number; outcome?: string }>(
        `/v1/plugins/${id}/sync`,
        { method: "POST", body: "{}" },
      );
      await refresh();
      setMsg(`Sync ${summary.outcome || "ok"}: ${summary.created ?? 0} created, ${summary.updated ?? 0} updated.`);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function lifecycle(id: string, action: "pause" | "enable" | "disable") {
    setBusy(true);
    try {
      await api(`/v1/plugins/${id}/${action}`, { method: "POST", body: "{}" });
      await refresh();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function remove() {
    if (!pending?.id) return;
    setBusy(true);
    try {
      await api(`/v1/plugins/${pending.id}?purge_data=${purge}`, { method: "DELETE" });
      setPending(null);
      await refresh();
      setMsg("Plugin removed.");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="space-y-6">
      <PageHeader
        title="Plugins"
        description="Optional import capabilities run as permissioned plugins. Nothing starts until you consent."
      />
      {error ? <Alert tone="error">{error}</Alert> : null}
      {msg ? <Alert tone="success">{msg}</Alert> : null}
      {items.map((item) => (
        <Card key={item.id || item.plugin_id} className="space-y-2">
          <p className="font-medium text-ink">
            {item.manifest?.name || item.plugin_id} · {item.state}
          </p>
          <p className="text-sm text-muted">{item.manifest?.description}</p>
          {item.last_run?.at ? (
            <p className="text-sm text-muted">
              Last run: {item.last_run.at} ({item.last_run.outcome}) · {item.last_run.created ?? 0} created,{" "}
              {item.last_run.updated ?? 0} updated
            </p>
          ) : null}
          <div className="flex flex-wrap gap-2">
            {item.state === "available" || !item.id ? (
              <Button onClick={() => void installBundled(item.plugin_id)} disabled={busy}>
                Install
              </Button>
            ) : null}
            {item.state === "installed" && item.id ? (
              <Button
                onClick={() => {
                  void api<ConsentPreview>(`/v1/plugins/${item.id}/consent`).then((preview) =>
                    setConsent({ id: item.id as string, preview }),
                  );
                }}
                disabled={busy}
              >
                Review permissions
              </Button>
            ) : null}
            {item.state === "enabled" && item.id ? (
              <>
                <Button onClick={() => void syncNow(item.id as string)} disabled={busy}>
                  Sync now
                </Button>
                <Button variant="secondary" onClick={() => void lifecycle(item.id as string, "pause")} disabled={busy}>
                  Pause
                </Button>
              </>
            ) : null}
            {item.state === "paused" && item.id ? (
              <Button variant="secondary" onClick={() => void lifecycle(item.id as string, "enable")} disabled={busy}>
                Resume
              </Button>
            ) : null}
            {item.id ? (
              <Button variant="danger" onClick={() => setPending(item)} disabled={busy}>
                Remove
              </Button>
            ) : null}
          </div>
        </Card>
      ))}
      <ConfirmDialog
        open={Boolean(consent)}
        title="Enable plugin"
        message={consent?.preview.text || ""}
        confirmLabel="Allow"
        busy={busy}
        onConfirm={() => void approve()}
        onCancel={() => setConsent(null)}
      >
        {consent?.preview.warnings?.map((warning) => (
          <p key={warning} className="mt-2 text-sm text-muted">
            {warning}
          </p>
        ))}
      </ConfirmDialog>
      <ConfirmDialog
        open={Boolean(pending)}
        title="Remove plugin"
        message="The plugin stops immediately. Keep imported data or delete it."
        confirmLabel="Remove"
        danger
        busy={busy}
        onConfirm={() => void remove()}
        onCancel={() => {
          setPending(null);
          setPurge(false);
        }}
      >
        <label className="mt-3 flex items-center gap-2 text-sm text-ink">
          <input type="checkbox" checked={purge} onChange={(e) => setPurge(e.target.checked)} />
          Also delete data this plugin created
        </label>
      </ConfirmDialog>
    </section>
  );
}

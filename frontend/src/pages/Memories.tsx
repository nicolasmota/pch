import { FormEvent, useState } from "react";
import { api, errorMessage } from "../api/client";
import type { Memory, MemoryVersion, Preference } from "../api/types";
import Alert from "../components/Alert";
import Badge from "../components/Badge";
import Button from "../components/Button";
import Card from "../components/Card";
import DataList from "../components/DataList";
import Field from "../components/Field";
import Input from "../components/Input";
import JsonViewer from "../components/JsonViewer";
import Modal from "../components/Modal";
import PageHeader from "../components/PageHeader";
import Spinner from "../components/Spinner";
import { useApi } from "../hooks/useApi";

type ValidityFields = {
  created_at?: string | null;
  valid_from?: string | null;
  valid_until?: string | null;
  never_true?: boolean;
};

function isCurrent(item: ValidityFields): boolean {
  if (item.never_true) {
    return false;
  }
  const now = Date.now();
  const start = item.valid_from ?? item.created_at;
  if (start && Date.parse(start) > now) {
    return false;
  }
  if (!item.valid_until) {
    return true;
  }
  return Date.parse(item.valid_until) > now;
}

function intervalLabel(from: string | null | undefined, until: string | null | undefined): string {
  const start = from ?? "asserted";
  const end = until ?? "open";
  return `${start} → ${end}`;
}

export default function Memories() {
  const memories = useApi<Memory[]>(() => api("/v1/memories"));
  const prefs = useApi<Preference[]>(() => api("/v1/preferences"));
  const [statement, setStatement] = useState("");
  const [prefKey, setPrefKey] = useState("");
  const [prefValue, setPrefValue] = useState("");
  const [formError, setFormError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [versions, setVersions] = useState<MemoryVersion[] | null>(null);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [historyLoading, setHistoryLoading] = useState(false);

  function reloadAll() {
    memories.reload();
    prefs.reload();
  }

  async function createMemory(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setFormError(null);
    try {
      await api("/v1/memories", {
        method: "POST",
        body: JSON.stringify({ statement, kind: "semantic" }),
      });
      setStatement("");
      reloadAll();
    } catch (err) {
      setFormError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function createPref(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setFormError(null);
    try {
      await api("/v1/preferences", {
        method: "POST",
        body: JSON.stringify({ key: prefKey, value: prefValue }),
      });
      setPrefKey("");
      setPrefValue("");
      reloadAll();
    } catch (err) {
      setFormError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function history(id: string) {
    setHistoryLoading(true);
    setHistoryError(null);
    setVersions(null);
    try {
      setVersions(await api<MemoryVersion[]>(`/v1/memories/${id}/versions`));
    } catch (err) {
      setVersions(null);
      setHistoryError(errorMessage(err));
    } finally {
      setHistoryLoading(false);
    }
  }

  async function supersedePref(item: Preference) {
    const next = window.prompt("New value (change of mind)", String(item.value ?? ""));
    if (next == null) {
      return;
    }
    setBusy(true);
    setFormError(null);
    try {
      await api(`/v1/preferences/${item.id}/supersede`, {
        method: "POST",
        body: JSON.stringify({ value: next }),
      });
      reloadAll();
    } catch (err) {
      setFormError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function supersedeMem(item: Memory) {
    const next = window.prompt("New statement (change of mind)", item.statement);
    if (next == null) {
      return;
    }
    setBusy(true);
    setFormError(null);
    try {
      await api(`/v1/memories/${item.id}/supersede`, {
        method: "POST",
        body: JSON.stringify({ statement: next }),
      });
      reloadAll();
    } catch (err) {
      setFormError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function retract(kind: "preferences" | "memories", id: string) {
    if (!window.confirm("Mark this as never true? It will leave current and historical truth.")) {
      return;
    }
    setBusy(true);
    setFormError(null);
    try {
      await api(`/v1/${kind}/${id}/retract`, { method: "POST" });
      reloadAll();
    } catch (err) {
      setFormError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function editInterval(
    kind: "preferences" | "memories",
    id: string,
    from?: string | null,
    until?: string | null,
  ) {
    const nextFrom = window.prompt("Valid from (ISO-8601 UTC, empty = keep)", from ?? "");
    if (nextFrom == null) {
      return;
    }
    const nextUntil = window.prompt("Valid until (ISO-8601 UTC, empty = still current)", until ?? "");
    if (nextUntil == null) {
      return;
    }
    setBusy(true);
    setFormError(null);
    try {
      await api(`/v1/${kind}/${id}`, {
        method: "PATCH",
        body: JSON.stringify({
          valid_from: nextFrom.trim() || from,
          valid_until: nextUntil.trim() || null,
        }),
      });
      reloadAll();
    } catch (err) {
      setFormError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  const loading = memories.loading || prefs.loading;
  const error = memories.error || prefs.error;

  return (
    <section className="space-y-6">
      <PageHeader
        title="Memories"
        description="Facts and preferences. Current vs historical is validity, not object-version history."
      />
      {error ? <Alert tone="error">{error}</Alert> : null}
      {formError ? <Alert tone="error">{formError}</Alert> : null}
      <Card>
        <form className="space-y-4" onSubmit={createMemory}>
          <Field id="memory-statement" label="Statement">
            <Input
              id="memory-statement"
              value={statement}
              onChange={(e) => setStatement(e.target.value)}
              required
            />
          </Field>
          <Button type="submit" disabled={busy}>
            Save memory
          </Button>
        </form>
      </Card>
      <Card>
        <form className="space-y-4" onSubmit={createPref}>
          <Field id="pref-key" label="Preference key">
            <Input id="pref-key" value={prefKey} onChange={(e) => setPrefKey(e.target.value)} required />
          </Field>
          <Field id="pref-value" label="Value">
            <Input id="pref-value" value={prefValue} onChange={(e) => setPrefValue(e.target.value)} required />
          </Field>
          <Button type="submit" disabled={busy}>
            Save preference
          </Button>
        </form>
      </Card>
      {loading ? (
        <Spinner />
      ) : (
        <>
          <h2 className="text-sm font-medium text-ink">Preferences</h2>
          <DataList
            items={prefs.data ?? []}
            keyOf={(p) => p.id}
            empty="No preferences yet."
            render={(p) => {
              const current = isCurrent(p);
              return (
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <p className="text-ink">
                      {p.key} = {String(p.value)}
                    </p>
                    <p className="mt-1 text-xs text-muted">{intervalLabel(p.valid_from, p.valid_until)}</p>
                    <div className="mt-1 flex flex-wrap gap-1">
                      <Badge tone={current ? "success" : "neutral"}>{current ? "current" : "historical"}</Badge>
                      <Badge>{p.authority}</Badge>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {current ? (
                      <Button variant="secondary" onClick={() => void supersedePref(p)} disabled={busy}>
                        Supersede
                      </Button>
                    ) : null}
                    <Button
                      variant="secondary"
                      onClick={() => void editInterval("preferences", p.id, p.valid_from, p.valid_until)}
                      disabled={busy}
                    >
                      Edit interval
                    </Button>
                    <Button variant="secondary" onClick={() => void retract("preferences", p.id)} disabled={busy}>
                      Retract
                    </Button>
                  </div>
                </div>
              );
            }}
          />
          <h2 className="text-sm font-medium text-ink">Memories</h2>
          <DataList
            items={memories.data ?? []}
            keyOf={(m) => m.id}
            empty="No memories yet."
            render={(m) => {
              const current = isCurrent(m);
              return (
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <p className="text-ink">{m.statement}</p>
                    <p className="mt-1 text-xs text-muted">{intervalLabel(m.valid_from, m.valid_until)}</p>
                    <div className="mt-1 flex flex-wrap gap-1">
                      <Badge tone={current ? "success" : "neutral"}>{current ? "current" : "historical"}</Badge>
                      <Badge>{m.authority}</Badge>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {current ? (
                      <Button variant="secondary" onClick={() => void supersedeMem(m)} disabled={busy}>
                        Supersede
                      </Button>
                    ) : null}
                    <Button
                      variant="secondary"
                      onClick={() => void editInterval("memories", m.id, m.valid_from, m.valid_until)}
                      disabled={busy}
                    >
                      Edit interval
                    </Button>
                    <Button variant="secondary" onClick={() => void retract("memories", m.id)} disabled={busy}>
                      Retract
                    </Button>
                    <Button variant="secondary" onClick={() => void history(m.id)}>
                      Versions
                    </Button>
                  </div>
                </div>
              );
            }}
          />
        </>
      )}
      <Modal
        open={versions !== null || historyError !== null || historyLoading}
        title="Object versions (edits, not validity)"
        onClose={() => {
          setVersions(null);
          setHistoryError(null);
        }}
      >
        {historyLoading ? <Spinner /> : null}
        {historyError ? <Alert tone="error">{historyError}</Alert> : null}
        {!historyLoading && versions ? <JsonViewer value={versions} /> : null}
      </Modal>
    </section>
  );
}

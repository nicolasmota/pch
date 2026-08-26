import { useState } from "react";
import { api, errorMessage } from "../api/client";
import type { AuditEvent } from "../api/types";
import Alert from "../components/Alert";
import Button from "../components/Button";
import JsonViewer from "../components/JsonViewer";
import PageHeader from "../components/PageHeader";
import Spinner from "../components/Spinner";
import { useApi } from "../hooks/useApi";

function ContractIssuance({ event }: { event: AuditEvent }) {
  const extra = event.extra ?? {};
  const refs = extra.item_refs ?? [];
  const omissions = extra.omission_categories ?? [];
  return (
    <div className="space-y-1">
      <p className="text-ink">
        Context contract {extra.status ?? "issued"}
        {extra.purpose ? ` · ${extra.purpose}` : ""}
      </p>
      {refs.length > 0 ? (
        <p className="text-xs text-muted">
          Items: {refs.map((r) => `${r.type}:${r.id}`).join(", ")}
        </p>
      ) : null}
      {omissions.length > 0 ? (
        <p className="text-xs text-muted">
          Omitted: {omissions.map((o) => `${o.category} (${o.count})`).join(", ")}
        </p>
      ) : null}
    </div>
  );
}

export default function Audit() {
  const { data, loading, error } = useApi<AuditEvent[]>(() => api("/v1/events"));
  const [verify, setVerify] = useState<unknown>(null);
  const [verifyError, setVerifyError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function verifyChain() {
    setBusy(true);
    setVerifyError(null);
    try {
      setVerify(await api("/v1/events/verify"));
    } catch (err) {
      setVerifyError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="space-y-6">
      <PageHeader title="Audit timeline" description="What happened in this personal space." />
      {error ? <Alert tone="error">{error}</Alert> : null}
      {verifyError ? <Alert tone="error">{verifyError}</Alert> : null}
      <Button onClick={verifyChain} disabled={busy}>
        Verify chain
      </Button>
      {verify !== null ? <JsonViewer value={verify} /> : null}
      {loading ? (
        <Spinner />
      ) : (data ?? []).length === 0 ? (
        <p className="text-sm text-muted">No events yet.</p>
      ) : (
        <ol className="space-y-2 border-l border-line pl-4">
          {(data ?? []).map((e) => (
            <li key={e.seq} className="text-sm">
              <p className="text-xs text-muted">
                {e.created_at} · {e.actor}
                {e.kind === "context.contract" ? " · context.contract" : ""}
              </p>
              {e.kind === "context.contract" ? (
                <ContractIssuance event={e} />
              ) : (
                <p className="text-ink">{e.summary_human}</p>
              )}
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}

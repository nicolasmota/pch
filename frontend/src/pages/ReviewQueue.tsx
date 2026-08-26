import { useState } from "react";
import { api, errorMessage } from "../api/client";
import type { MemoryProposal } from "../api/types";
import Alert from "../components/Alert";
import Button from "../components/Button";
import Card from "../components/Card";
import ConfirmDialog from "../components/ConfirmDialog";
import EmptyState from "../components/EmptyState";
import PageHeader from "../components/PageHeader";
import Spinner from "../components/Spinner";
import { useApi } from "../hooks/useApi";

export default function ReviewQueue() {
  const { data, loading, error, reload } = useApi<MemoryProposal[]>(() =>
    api("/v1/memories/proposals?status=pending"),
  );
  const [actionError, setActionError] = useState<string | null>(null);
  const [rejectId, setRejectId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function accept(id: string) {
    setBusy(true);
    setActionError(null);
    try {
      await api(`/v1/memories/proposals/${id}/accept`, { method: "POST", body: "{}" });
      reload();
    } catch (err) {
      setActionError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function reject(id: string) {
    setBusy(true);
    setActionError(null);
    try {
      await api(`/v1/memories/proposals/${id}/reject`, { method: "POST", body: "{}" });
      setRejectId(null);
      reload();
    } catch (err) {
      setActionError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  const items = data ?? [];

  return (
    <section className="space-y-6">
      <PageHeader title="Memory review" description="Accept or reject proposed memories." />
      {error ? <Alert tone="error">{error}</Alert> : null}
      {actionError ? <Alert tone="error">{actionError}</Alert> : null}
      {loading ? <Spinner /> : null}
      {!loading && items.length === 0 ? (
        <EmptyState message="No pending memory proposals." />
      ) : null}
      {items.map((p) => (
        <Card key={p.id} className="space-y-3">
          <p className="text-ink">{p.proposed_memory?.statement || p.statement}</p>
          <p className="text-xs text-muted">
            Evidence: {(p.evidence_refs || []).join(", ") || "none"} · confidence {p.confidence}
          </p>
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => accept(p.id)} disabled={busy}>
              Accept
            </Button>
            <Button variant="danger" onClick={() => setRejectId(p.id)} disabled={busy}>
              Reject
            </Button>
          </div>
        </Card>
      ))}
      <ConfirmDialog
        open={rejectId !== null}
        title="Reject proposal"
        message="This proposed memory will be discarded."
        confirmLabel="Reject"
        danger
        busy={busy}
        onConfirm={() => {
          if (rejectId) void reject(rejectId);
        }}
        onCancel={() => setRejectId(null)}
      />
    </section>
  );
}

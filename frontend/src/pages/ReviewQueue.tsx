import { useState } from "react";
import { api, errorMessage } from "../api/client";
import type { MemoryProposal, OperationalProposal, RelationProposal } from "../api/types";
import Alert from "../components/Alert";
import Button from "../components/Button";
import Card from "../components/Card";
import ConfirmDialog from "../components/ConfirmDialog";
import EmptyState from "../components/EmptyState";
import PageHeader from "../components/PageHeader";
import Spinner from "../components/Spinner";
import { useApi } from "../hooks/useApi";

export default function ReviewQueue() {
  const memories = useApi<MemoryProposal[]>(() => api("/v1/memories/proposals?status=pending"));
  const operational = useApi<OperationalProposal[]>(() =>
    api("/v1/operational-proposals?status=pending"),
  );
  const relationProposals = useApi<RelationProposal[]>(() =>
    api("/v1/relation-proposals?status=pending"),
  );
  const [actionError, setActionError] = useState<string | null>(null);
  const [rejectMemoryId, setRejectMemoryId] = useState<string | null>(null);
  const [rejectOperationalId, setRejectOperationalId] = useState<string | null>(null);
  const [rejectRelationId, setRejectRelationId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  function reloadAll() {
    memories.reload();
    operational.reload();
    relationProposals.reload();
  }

  async function acceptMemory(id: string) {
    setBusy(true);
    setActionError(null);
    try {
      await api(`/v1/memories/proposals/${id}/accept`, { method: "POST", body: "{}" });
      reloadAll();
    } catch (err) {
      setActionError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function rejectMemory(id: string) {
    setBusy(true);
    setActionError(null);
    try {
      await api(`/v1/memories/proposals/${id}/reject`, { method: "POST", body: "{}" });
      setRejectMemoryId(null);
      reloadAll();
    } catch (err) {
      setActionError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function acceptOperational(id: string) {
    setBusy(true);
    setActionError(null);
    try {
      await api(`/v1/operational-proposals/${id}/accept`, { method: "POST", body: "{}" });
      reloadAll();
    } catch (err) {
      setActionError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function rejectOperational(id: string) {
    setBusy(true);
    setActionError(null);
    try {
      await api(`/v1/operational-proposals/${id}/reject`, { method: "POST", body: "{}" });
      setRejectOperationalId(null);
      reloadAll();
    } catch (err) {
      setActionError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function acceptRelation(id: string) {
    setBusy(true);
    setActionError(null);
    try {
      await api(`/v1/relation-proposals/${id}/accept`, { method: "POST", body: "{}" });
      reloadAll();
    } catch (err) {
      setActionError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function rejectRelation(id: string) {
    setBusy(true);
    setActionError(null);
    try {
      await api(`/v1/relation-proposals/${id}/reject`, { method: "POST", body: "{}" });
      setRejectRelationId(null);
      reloadAll();
    } catch (err) {
      setActionError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  const memoryItems = memories.data ?? [];
  const operationalItems = operational.data ?? [];
  const relationItems = relationProposals.data ?? [];
  const loading = memories.loading || operational.loading || relationProposals.loading;

  return (
    <section className="space-y-6">
      <PageHeader
        title="Review"
        description="Accept or reject proposed memories, operational state, and relations."
      />
      {memories.error ? <Alert tone="error">{memories.error}</Alert> : null}
      {operational.error ? <Alert tone="error">{operational.error}</Alert> : null}
      {relationProposals.error ? <Alert tone="error">{relationProposals.error}</Alert> : null}
      {actionError ? <Alert tone="error">{actionError}</Alert> : null}
      {loading ? <Spinner /> : null}

      <h2 className="text-sm font-medium text-ink">Memory proposals</h2>
      {!loading && memoryItems.length === 0 ? (
        <EmptyState message="No pending memory proposals." />
      ) : null}
      {memoryItems.map((p) => (
        <Card key={p.id} className="space-y-3">
          <p className="text-ink">{p.proposed_memory?.statement || p.statement}</p>
          <p className="text-xs text-muted">
            Evidence: {(p.evidence_refs || []).join(", ") || "none"} · confidence {p.confidence}
          </p>
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => acceptMemory(p.id)} disabled={busy}>
              Accept
            </Button>
            <Button variant="danger" onClick={() => setRejectMemoryId(p.id)} disabled={busy}>
              Reject
            </Button>
          </div>
        </Card>
      ))}

      <h2 className="text-sm font-medium text-ink">Operational state proposals</h2>
      {!loading && operationalItems.length === 0 ? (
        <EmptyState message="No pending operational proposals." />
      ) : null}
      {operationalItems.map((p) => (
        <Card key={p.id} className="space-y-3">
          <p className="text-ink">
            {p.operational_phase || "no phase"} · {p.situation_intent || "no intent"}
          </p>
          <p className="text-xs text-muted">
            Target {p.target_id}
            {p.current_step ? ` · step ${p.current_step}` : ""}
            {p.submitted_by ? ` · from ${p.submitted_by}` : ""}
          </p>
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => acceptOperational(p.id)} disabled={busy}>
              Accept
            </Button>
            <Button variant="danger" onClick={() => setRejectOperationalId(p.id)} disabled={busy}>
              Reject
            </Button>
          </div>
        </Card>
      ))}

      <h2 className="text-sm font-medium text-ink">Relation proposals</h2>
      {!loading && relationItems.length === 0 ? (
        <EmptyState message="No pending relation proposals." />
      ) : null}
      {relationItems.map((p) => (
        <Card key={p.id} className="space-y-3">
          <p className="text-ink">
            {p.relation_type} · {p.from_id} → {p.to_id}
          </p>
          <p className="text-xs text-muted">{p.submitted_by ? `from ${p.submitted_by}` : p.id}</p>
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => acceptRelation(p.id)} disabled={busy}>
              Accept
            </Button>
            <Button variant="danger" onClick={() => setRejectRelationId(p.id)} disabled={busy}>
              Reject
            </Button>
          </div>
        </Card>
      ))}

      <ConfirmDialog
        open={rejectMemoryId !== null}
        title="Reject proposal"
        message="This proposed memory will be discarded."
        confirmLabel="Reject"
        danger
        busy={busy}
        onConfirm={() => {
          if (rejectMemoryId) void rejectMemory(rejectMemoryId);
        }}
        onCancel={() => setRejectMemoryId(null)}
      />
      <ConfirmDialog
        open={rejectOperationalId !== null}
        title="Reject operational proposal"
        message="Live phase and intent will stay unchanged."
        confirmLabel="Reject"
        danger
        busy={busy}
        onConfirm={() => {
          if (rejectOperationalId) void rejectOperational(rejectOperationalId);
        }}
        onCancel={() => setRejectOperationalId(null)}
      />
      <ConfirmDialog
        open={rejectRelationId !== null}
        title="Reject relation proposal"
        message="This typed link will not be created."
        confirmLabel="Reject"
        danger
        busy={busy}
        onConfirm={() => {
          if (rejectRelationId) void rejectRelation(rejectRelationId);
        }}
        onCancel={() => setRejectRelationId(null)}
      />
    </section>
  );
}

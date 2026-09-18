import { useState } from "react";
import { api, errorMessage } from "../api/client";
import type { Approval } from "../api/types";
import Alert from "../components/Alert";
import Button from "../components/Button";
import Card from "../components/Card";
import ConfirmDialog from "../components/ConfirmDialog";
import EmptyState from "../components/EmptyState";
import PageHeader from "../components/PageHeader";
import Spinner from "../components/Spinner";
import { useApi } from "../hooks/useApi";

type Props = {
  embedded?: boolean;
};

export default function Approvals({ embedded = false }: Props) {
  const { data, loading, error, reload } = useApi<Approval[]>(() =>
    api("/v1/approvals?status=pending"),
  );
  const [actionError, setActionError] = useState<string | null>(null);
  const [declineId, setDeclineId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function decide(id: string, decision: "approved" | "declined") {
    setBusy(true);
    setActionError(null);
    try {
      await api(`/v1/approvals/${id}/decide`, {
        method: "POST",
        body: JSON.stringify({ decision }),
      });
      setDeclineId(null);
      reload();
    } catch (err) {
      setActionError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  const items = data ?? [];

  const queue = (
    <>
      {items.map((a) => (
        <Card key={a.id} className="space-y-2">
          <p className="text-sm text-ink">
            <span className="font-medium">Who:</span> {a.connection_id}
          </p>
          <p className="text-sm text-ink">
            <span className="font-medium">What:</span> {a.summary_human}
          </p>
          <p className="text-sm text-muted">
            <span className="font-medium text-ink">Based on:</span>{" "}
            {(a.basis_refs || []).join(", ") || "none"}
          </p>
          <div className="flex flex-wrap gap-2 pt-2">
            <Button onClick={() => decide(a.id, "approved")} disabled={busy}>
              Approve
            </Button>
            <Button variant="danger" onClick={() => setDeclineId(a.id)} disabled={busy}>
              Decline
            </Button>
          </div>
        </Card>
      ))}
      <ConfirmDialog
        open={declineId !== null}
        title="Decline action"
        message="The agent will not be allowed to take this action."
        confirmLabel="Decline"
        danger
        busy={busy}
        onConfirm={() => {
          if (declineId) void decide(declineId, "declined");
        }}
        onCancel={() => setDeclineId(null)}
      />
    </>
  );

  if (embedded) {
    if (loading || items.length === 0) {
      return null;
    }
    return (
      <div className="space-y-3">
        <h2 className="text-sm font-medium text-ink">Approvals</h2>
        {error ? <Alert tone="error">{error}</Alert> : null}
        {actionError ? <Alert tone="error">{actionError}</Alert> : null}
        {queue}
      </div>
    );
  }

  return (
    <section className="space-y-6">
      <PageHeader title="Approvals" description="Decide on actions agents want to take." />
      {error ? <Alert tone="error">{error}</Alert> : null}
      {actionError ? <Alert tone="error">{actionError}</Alert> : null}
      {loading ? <Spinner /> : null}
      {!loading && items.length === 0 ? <EmptyState message="No pending approvals." /> : null}
      {queue}
    </section>
  );
}

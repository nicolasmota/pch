import { useState } from "react";
import { api, errorMessage } from "../api/client";
import type { Conflict } from "../api/types";
import Alert from "../components/Alert";
import Badge from "../components/Badge";
import Button from "../components/Button";
import DataList from "../components/DataList";
import PageHeader from "../components/PageHeader";
import Spinner from "../components/Spinner";
import { useApi } from "../hooks/useApi";

export default function Conflicts() {
  const { data, loading, error, reload } = useApi<Conflict[]>(() => api("/v1/conflicts"));
  const [actionError, setActionError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);

  async function keepExisting(id: string) {
    setBusyId(id);
    setActionError(null);
    try {
      await api(`/v1/conflicts/${id}/resolve`, {
        method: "POST",
        body: JSON.stringify({ status: "resolved_keep_existing" }),
      });
      reload();
    } catch (err) {
      setActionError(errorMessage(err));
    } finally {
      setBusyId(null);
    }
  }

  return (
    <section className="space-y-6">
      <PageHeader title="Conflicts" description="Resolve overlapping or contradictory memories." />
      {error ? <Alert tone="error">{error}</Alert> : null}
      {actionError ? <Alert tone="error">{actionError}</Alert> : null}
      {loading ? (
        <Spinner />
      ) : (
        <DataList
          items={data ?? []}
          keyOf={(c) => c.id}
          empty="No open conflicts."
          render={(c) => (
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <Badge tone="warning">{c.kind}</Badge>
                  <Badge>{c.status}</Badge>
                </div>
                <p className="mt-1 text-ink">{c.detail}</p>
              </div>
              <Button
                variant="secondary"
                onClick={() => keepExisting(c.id)}
                disabled={busyId === c.id}
              >
                Keep existing
              </Button>
            </div>
          )}
        />
      )}
    </section>
  );
}

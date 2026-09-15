import { api } from "../api/client";
import type { Grant } from "../api/types";
import Alert from "../components/Alert";
import Badge from "../components/Badge";
import DataList from "../components/DataList";
import PageHeader from "../components/PageHeader";
import Spinner from "../components/Spinner";
import { useApi } from "../hooks/useApi";

export default function Access() {
  const { data, loading, error } = useApi<Grant[]>(() => api("/v1/grants"));

  return (
    <section className="space-y-6">
      <PageHeader
        title="Access"
        description="What each connected agent may see or do, in plain language."
      />
      {error ? <Alert tone="error">{error}</Alert> : null}
      {loading ? (
        <Spinner />
      ) : (
        <DataList
          items={data ?? []}
          keyOf={(g) => g.id}
          empty="No grants yet."
          render={(g) => (
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <p className="text-ink">{g.summary_human}</p>
              <Badge tone={g.status === "active" ? "success" : "neutral"}>{g.status}</Badge>
            </div>
          )}
        />
      )}
    </section>
  );
}

import { FormEvent, useState } from "react";
import { api, errorMessage } from "../api/client";
import type { SearchHit, SearchResponse } from "../api/types";
import Alert from "../components/Alert";
import Badge from "../components/Badge";
import Button from "../components/Button";
import Card from "../components/Card";
import DataList from "../components/DataList";
import Field from "../components/Field";
import Input from "../components/Input";
import PageHeader from "../components/PageHeader";
import Spinner from "../components/Spinner";

export default function Search() {
  const [q, setQ] = useState("");
  const [results, setResults] = useState<SearchHit[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function run(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const data = await api<SearchResponse>(`/v1/search?q=${encodeURIComponent(q)}`);
      setResults(data.results || []);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="space-y-6">
      <PageHeader title="Search" description="Find projects, memories, and other records." />
      {error ? <Alert tone="error">{error}</Alert> : null}
      <Card>
        <form className="flex flex-col gap-3 sm:flex-row sm:items-end" onSubmit={run}>
          <div className="flex-1">
            <Field id="search-query" label="Query">
              <Input id="search-query" value={q} onChange={(e) => setQ(e.target.value)} />
            </Field>
          </div>
          <Button type="submit" disabled={busy}>
            Search
          </Button>
        </form>
      </Card>
      {busy ? <Spinner /> : null}
      {results && !busy ? (
        <DataList
          items={results}
          keyOf={(r) => r.id}
          empty="No matching records."
          render={(r) => (
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <Badge>{r.type}</Badge>
                {r.classification ? <Badge tone="warning">{r.classification}</Badge> : null}
              </div>
              <p className="mt-1 text-ink">{r.title || r.statement}</p>
              {r.citations?.length ? (
                <p className="mt-1 text-xs text-muted">
                  sources: {r.citations.map((c) => c.id).join(", ")}
                </p>
              ) : null}
            </div>
          )}
        />
      ) : null}
    </section>
  );
}

import { FormEvent, useState } from "react";
import { api, errorMessage } from "../api/client";
import type { Memory, MemoryVersion } from "../api/types";
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

export default function Memories() {
  const { data, loading, error, reload } = useApi<Memory[]>(() => api("/v1/memories"));
  const [statement, setStatement] = useState("");
  const [formError, setFormError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [versions, setVersions] = useState<MemoryVersion[] | null>(null);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [historyLoading, setHistoryLoading] = useState(false);

  async function create(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setFormError(null);
    try {
      await api("/v1/memories", {
        method: "POST",
        body: JSON.stringify({ statement, kind: "semantic" }),
      });
      setStatement("");
      reload();
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

  return (
    <section className="space-y-6">
      <PageHeader title="Memories" description="Facts and notes the hub should remember." />
      {error ? <Alert tone="error">{error}</Alert> : null}
      {formError ? <Alert tone="error">{formError}</Alert> : null}
      <Card>
        <form className="space-y-4" onSubmit={create}>
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
      {loading ? (
        <Spinner />
      ) : (
        <DataList
          items={data ?? []}
          keyOf={(m) => m.id}
          empty="No memories yet."
          render={(m) => (
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div className="min-w-0 flex-1">
                <p className="text-ink">{m.statement}</p>
                <div className="mt-1">
                  <Badge>{m.authority}</Badge>
                </div>
              </div>
              <Button variant="secondary" onClick={() => history(m.id)}>
                History
              </Button>
            </div>
          )}
        />
      )}
      <Modal
        open={versions !== null || historyError !== null || historyLoading}
        title="Memory history"
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

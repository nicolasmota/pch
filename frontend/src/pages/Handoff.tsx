import { FormEvent, useState } from "react";
import { api, errorMessage } from "../api/client";
import type { SharedState } from "../api/types";
import Alert from "../components/Alert";
import Button from "../components/Button";
import Card from "../components/Card";
import Field from "../components/Field";
import Input from "../components/Input";
import JsonViewer from "../components/JsonViewer";
import PageHeader from "../components/PageHeader";

export default function Handoff() {
  const [key, setKey] = useState("focus");
  const [value, setValue] = useState("");
  const [got, setGot] = useState<unknown>(null);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function save(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    setMsg("");
    try {
      await api(`/v1/state/${key}`, {
        method: "PUT",
        body: JSON.stringify({ value, ttl_seconds: 900, visibility: "shared" }),
      });
      setMsg("Shared state saved.");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function load() {
    setBusy(true);
    setError(null);
    try {
      const data = await api<SharedState>(`/v1/state/${key}`);
      setGot(data.value);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="space-y-6">
      <PageHeader title="Shared handoff state" description="Pass a short note between agents." />
      {error ? <Alert tone="error">{error}</Alert> : null}
      {msg ? <Alert tone="success">{msg}</Alert> : null}
      <Card>
        <form className="space-y-4" onSubmit={save}>
          <Field id="handoff-key" label="Key">
            <Input id="handoff-key" value={key} onChange={(e) => setKey(e.target.value)} required />
          </Field>
          <Field id="handoff-value" label="Value">
            <Input id="handoff-value" value={value} onChange={(e) => setValue(e.target.value)} />
          </Field>
          <div className="flex flex-wrap gap-2">
            <Button type="submit" disabled={busy}>
              Save shared
            </Button>
            <Button variant="secondary" onClick={load} disabled={busy}>
              Load
            </Button>
          </div>
        </form>
      </Card>
      {got !== null ? <JsonViewer value={got} /> : null}
    </section>
  );
}

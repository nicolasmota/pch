import { FormEvent, useState } from "react";
import { api, errorMessage } from "../api/client";
import type { ExportResult } from "../api/types";
import Alert from "../components/Alert";
import Button from "../components/Button";
import Card from "../components/Card";
import Field from "../components/Field";
import Input from "../components/Input";
import PageHeader from "../components/PageHeader";

export default function ExportPage() {
  const [pass, setPass] = useState("");
  const [result, setResult] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function run(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    setResult("");
    try {
      const data = await api<ExportResult>("/v1/export", {
        method: "POST",
        body: JSON.stringify({ passphrase: pass, filters: {} }),
      });
      setResult(data.path);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="space-y-6">
      <PageHeader title="Export" description="Write an encrypted archive of this personal space." />
      {error ? <Alert tone="error">{error}</Alert> : null}
      {result ? <Alert tone="success">Exported to {result}</Alert> : null}
      <Card>
        <form className="space-y-4" onSubmit={run}>
          <Field id="export-pass" label="Passphrase">
            <Input
              id="export-pass"
              type="password"
              value={pass}
              onChange={(e) => setPass(e.target.value)}
              required
            />
          </Field>
          <Button type="submit" disabled={busy}>
            Export space
          </Button>
        </form>
      </Card>
    </section>
  );
}

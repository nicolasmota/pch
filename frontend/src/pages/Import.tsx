import { FormEvent, useState } from "react";
import { api, errorMessage } from "../api/client";
import type { ImportApplyResult, StagingImport } from "../api/types";
import Alert from "../components/Alert";
import Button from "../components/Button";
import Card from "../components/Card";
import ConfirmDialog from "../components/ConfirmDialog";
import Field from "../components/Field";
import Input from "../components/Input";
import PageHeader from "../components/PageHeader";

export default function ImportPage() {
  const [path, setPath] = useState("");
  const [pass, setPass] = useState("");
  const [staging, setStaging] = useState<StagingImport | null>(null);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [confirmApply, setConfirmApply] = useState(false);

  async function stage(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    setMsg("");
    try {
      setStaging(
        await api<StagingImport>("/v1/import/stage", {
          method: "POST",
          body: JSON.stringify({ path, passphrase: pass }),
        }),
      );
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function apply() {
    if (!staging) return;
    setBusy(true);
    setError(null);
    try {
      const result = await api<ImportApplyResult>(`/v1/import/staging/${staging.id}/apply`, {
        method: "POST",
        body: JSON.stringify({ resolutions: [] }),
      });
      setConfirmApply(false);
      setMsg(`Imported ${result.applied} records.`);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="space-y-6">
      <PageHeader title="Import" description="Stage an archive, review conflicts, then apply." />
      {error ? <Alert tone="error">{error}</Alert> : null}
      {msg ? <Alert tone="success">{msg}</Alert> : null}
      <Card>
        <form className="space-y-4" onSubmit={stage}>
          <Field id="import-path" label="Archive path">
            <Input
              id="import-path"
              value={path}
              onChange={(e) => setPath(e.target.value)}
              required
            />
          </Field>
          <Field id="import-pass" label="Passphrase">
            <Input
              id="import-pass"
              type="password"
              value={pass}
              onChange={(e) => setPass(e.target.value)}
              required
            />
          </Field>
          <Button type="submit" disabled={busy}>
            Stage
          </Button>
        </form>
      </Card>
      {staging ? (
        <Card className="space-y-3">
          <p className="text-sm text-ink">Conflicts: {(staging.conflicts || []).length}</p>
          <Button onClick={() => setConfirmApply(true)} disabled={busy}>
            Apply
          </Button>
        </Card>
      ) : null}
      <ConfirmDialog
        open={confirmApply}
        title="Apply import"
        message="Staged records will be written into this personal space."
        confirmLabel="Apply"
        busy={busy}
        onConfirm={apply}
        onCancel={() => setConfirmApply(false)}
      />
    </section>
  );
}

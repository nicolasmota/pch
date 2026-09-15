import { FormEvent, useState } from "react";
import { api, errorMessage } from "../api/client";
import type { ImportApplyResult, StagingImport, VendorImportBatch } from "../api/types";
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
  const [vendorPath, setVendorPath] = useState("");
  const [staging, setStaging] = useState<StagingImport | null>(null);
  const [vendor, setVendor] = useState<VendorImportBatch | null>(null);
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

  async function importVendor(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    setMsg("");
    try {
      const batch = await api<VendorImportBatch>("/v1/import/vendor", {
        method: "POST",
        body: JSON.stringify({ path: vendorPath }),
      });
      setVendor(batch);
      setMsg(
        `Queued ${batch.enqueued} memories from ${batch.source} as proposals. Nothing is live until you accept them in Review.`,
      );
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function decideArchive(admit: boolean) {
    if (!vendor) return;
    setBusy(true);
    setError(null);
    try {
      const next = await api<VendorImportBatch>(`/v1/import/vendor/${vendor.id}/archive`, {
        method: "POST",
        body: JSON.stringify({ admit }),
      });
      setVendor({ ...vendor, archive_status: next.archive_status });
      setMsg(
        admit
          ? "Conversations stored as untrusted archive data."
          : "Conversation archive discarded. Memory proposals are unchanged.",
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
      <PageHeader
        title="Import"
        description="Bring a ChatGPT, Claude, or Gemini export into the review queue, or stage a Hub archive."
      />
      {error ? <Alert tone="error">{error}</Alert> : null}
      {msg ? <Alert tone="success">{msg}</Alert> : null}
      <Card>
        <form className="space-y-4" onSubmit={importVendor}>
          <Field id="vendor-path" label="Vendor or interchange file">
            <Input
              id="vendor-path"
              value={vendorPath}
              onChange={(e) => setVendorPath(e.target.value)}
              required
            />
          </Field>
          <p className="text-sm text-muted">
            ChatGPT, Claude, Gemini, PAM, or UMP. No passphrase. Items land as proposals, not live
            truth.
          </p>
          <Button type="submit" disabled={busy}>
            Import as proposals
          </Button>
        </form>
      </Card>
      {vendor ? (
        <Card className="space-y-3">
          <p className="text-sm text-ink">
            {vendor.source}: {vendor.enqueued} queued, {vendor.skipped} skipped,{" "}
            {vendor.conversation_count} conversations ({vendor.archive_status}).
          </p>
          {vendor.archive_status === "pending" ? (
            <div className="flex gap-2">
              <Button onClick={() => void decideArchive(true)} disabled={busy}>
                Keep chats as untrusted data
              </Button>
              <Button onClick={() => void decideArchive(false)} disabled={busy}>
                Discard chats
              </Button>
            </div>
          ) : null}
        </Card>
      ) : null}
      <Card>
        <form className="space-y-4" onSubmit={stage}>
          <Field id="import-path" label="Hub archive path">
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

import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, errorMessage } from "../api/client";
import type { SetupResponse, SetupStatus } from "../api/types";
import Alert from "../components/Alert";
import Button from "../components/Button";
import Card from "../components/Card";
import ConfirmDialog from "../components/ConfirmDialog";
import Field from "../components/Field";
import Input from "../components/Input";
import PageHeader from "../components/PageHeader";
import Spinner from "../components/Spinner";
import { useApi } from "../hooks/useApi";

export default function Setup() {
  const navigate = useNavigate();
  const { data: status, loading, error: loadError, reload } = useApi<SetupStatus>(() =>
    api("/v1/setup"),
  );
  const [name, setName] = useState("");
  const [msg, setMsg] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [confirmRestart, setConfirmRestart] = useState(false);

  async function start(restart: boolean) {
    const trimmed = name.trim() || status?.name?.trim() || "";
    if (!restart && !trimmed) {
      setError("Enter the name you want this space to belong to.");
      return;
    }
    setBusy(true);
    setError(null);
    setMsg("");
    try {
      const data = await api<SetupResponse>("/v1/setup", {
        method: "POST",
        body: JSON.stringify({ name: trimmed || "Me", restart }),
      });
      if (data.owner_token) localStorage.setItem("pch_token", data.owner_token);
      setMsg(restart ? "Personal space restarted." : "Personal space is ready on this device.");
      reload();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
      setConfirmRestart(false);
    }
  }

  if (loading) {
    return (
      <section className="space-y-6">
        <PageHeader title="Home" description="Your personal space on this device." />
        <Spinner label="Loading setup" />
      </section>
    );
  }

  const initialized = Boolean(status?.initialized);
  const ownerName = status?.name?.trim() || "";

  return (
    <section className="space-y-6">
      <PageHeader
        title={initialized ? "Your space" : "Guided setup"}
        description={
          initialized
            ? "This Hub already has a private personal space on this device. No cloud account."
            : "Creates a private personal space on this device. No cloud account. This is a one-time first run."
        }
      />
      {loadError ? <Alert tone="error">{loadError}</Alert> : null}
      {error ? <Alert tone="error">{error}</Alert> : null}
      {msg ? <Alert tone="success">{msg}</Alert> : null}

      {initialized ? (
        <Card className="space-y-4">
          <p className="text-sm text-ink">
            Owner on this device: <strong>{ownerName || "unset"}</strong>
          </p>
          <p className="text-sm text-muted">
            Add projects, memories, and connections from the menu. Come back here only if you need
            to start over.
          </p>
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => navigate("/projects")}>Go to projects</Button>
            <Button variant="secondary" onClick={() => navigate("/search")}>
              Search
            </Button>
            <Button variant="danger" onClick={() => setConfirmRestart(true)} disabled={busy}>
              Restart setup
            </Button>
          </div>
        </Card>
      ) : (
        <Card className="space-y-4">
          <Field id="setup-name" label="Your name">
            <Input
              id="setup-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoComplete="name"
              placeholder="How you want to appear as owner"
            />
          </Field>
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => start(false)} disabled={busy}>
              Create space
            </Button>
          </div>
        </Card>
      )}

      <ConfirmDialog
        open={confirmRestart}
        title="Restart setup"
        message="This deletes the current personal space on this device and starts over."
        confirmLabel="Restart"
        danger
        busy={busy}
        onConfirm={() => start(true)}
        onCancel={() => setConfirmRestart(false)}
      />
    </section>
  );
}

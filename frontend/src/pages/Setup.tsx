import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, errorMessage } from "../api/client";
import type { SetupResponse, SetupStatus, SituationResponse } from "../api/types";
import Alert from "../components/Alert";
import Button from "../components/Button";
import Card from "../components/Card";
import ConfirmDialog from "../components/ConfirmDialog";
import Field from "../components/Field";
import Input from "../components/Input";
import PageHeader from "../components/PageHeader";
import SituationBoard from "../components/SituationBoard";
import Spinner from "../components/Spinner";
import { useApi } from "../hooks/useApi";

function keyStorageLine(storage: SetupStatus["key_storage"]): string | null {
  switch (storage) {
    case "keychain":
      return "Key stored in your system keychain";
    case "file":
      return "Key stored in a private file in ~/.pch";
    case undefined:
      return null;
    default: {
      const _never: never = storage;
      return _never;
    }
  }
}

export default function Setup() {
  const navigate = useNavigate();
  const {
    data: status,
    loading,
    error: loadError,
    reload,
  } = useApi<SetupStatus>(() => api("/v1/setup"));
  const {
    data: situation,
    loading: situationLoading,
    error: situationError,
    reload: reloadSituation,
  } = useApi<SituationResponse>(() => api("/v1/situation"));
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
      reloadSituation();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
      setConfirmRestart(false);
    }
  }

  async function capture(input: { title?: string; statement: string }) {
    setBusy(true);
    setError(null);
    setMsg("");
    try {
      await api("/v1/situation/capture", {
        method: "POST",
        body: JSON.stringify({
          title: input.title || null,
          statement: input.statement,
        }),
      });
      reloadSituation();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
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
  const keyLine = keyStorageLine(status?.key_storage);

  return (
    <section className="space-y-6">
      {loadError ? <Alert tone="error">{loadError}</Alert> : null}
      {error ? <Alert tone="error">{error}</Alert> : null}
      {msg ? <Alert tone="success">{msg}</Alert> : null}

      {initialized ? (
        <SituationBoard
          ownerName={ownerName}
          keyLine={keyLine}
          data={situation}
          loading={situationLoading}
          error={situationError}
          busy={busy}
          onRestart={() => setConfirmRestart(true)}
          onOpen={(path) => navigate(path)}
          onCapture={capture}
        />
      ) : (
        <>
          <PageHeader
            title="Guided setup"
            description="Creates a private personal space on this device. No cloud account. This is a one-time first run."
          />
          {keyLine ? <p className="text-sm text-muted">{keyLine}</p> : null}
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
        </>
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

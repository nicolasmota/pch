import { FormEvent, useEffect, useState } from "react";
import { api, errorMessage } from "../api/client";
import type { AssistantCatalogEntry, AssistantRecipe, GrantPreset, PairingLink } from "../api/types";
import Alert from "../components/Alert";
import Button from "../components/Button";
import Card from "../components/Card";
import ConfirmDialog from "../components/ConfirmDialog";
import Field from "../components/Field";
import Input from "../components/Input";
import PageHeader from "../components/PageHeader";
import Select from "../components/Select";

function presetHelp(preset: GrantPreset): string {
  switch (preset) {
    case "always_ask_before_sending":
      return "This agent must ask before sending.";
    case "read_active_projects":
      return "This agent can read your active project context.";
    case "read_project":
      return "This agent can read the selected project context.";
    default: {
      const _exhaustive: never = preset;
      return _exhaustive;
    }
  }
}

function asGrantPreset(value: string): GrantPreset {
  switch (value) {
    case "read_active_projects":
    case "read_project":
    case "always_ask_before_sending":
      return value;
    default:
      return "read_project";
  }
}

export default function Connections() {
  const [link, setLink] = useState("");
  const [preset, setPreset] = useState<GrantPreset>("read_project");
  const [conn, setConn] = useState("");
  const [project, setProject] = useState("");
  const [msg, setMsg] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [confirmRevoke, setConfirmRevoke] = useState(false);
  const [assistants, setAssistants] = useState<AssistantCatalogEntry[]>([]);
  const [assistant, setAssistant] = useState("cursor");
  const [recipe, setRecipe] = useState<AssistantRecipe | null>(null);

  useEffect(() => {
    api<AssistantCatalogEntry[]>("/v1/catalog/assistants")
      .then(setAssistants)
      .catch(() => setAssistants([]));
  }, []);

  async function mint() {
    setBusy(true);
    setError(null);
    setMsg("");
    try {
      const data = await api<PairingLink>("/v1/connections/links", {
        method: "POST",
        body: JSON.stringify({ name: "agent" }),
      });
      setLink(data.code);
      setConn(data.connection_id);
      setMsg("Pairing link created.");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function grant(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    setMsg("");
    try {
      await api("/v1/grants", {
        method: "POST",
        body: JSON.stringify({
          connection_id: conn,
          preset,
          selectors: project ? { project } : {},
        }),
      });
      setMsg("Grant confirmed.");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function loadRecipe() {
    if (!conn) {
      setError("Create a pairing link first.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const data = await api<AssistantRecipe>(`/v1/connections/${conn}/recipe`, {
        method: "POST",
        body: JSON.stringify({ assistant }),
      });
      setRecipe(data);
      setMsg("Recipe ready — paste into the assistant config.");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function copyRecipe() {
    if (!recipe) return;
    await navigator.clipboard.writeText(JSON.stringify(recipe.snippet, null, 2));
    setMsg("Copied to clipboard.");
  }

  async function revoke() {
    setBusy(true);
    setError(null);
    setMsg("");
    try {
      await api(`/v1/connections/${conn}/revoke`, { method: "POST", body: "{}" });
      setConfirmRevoke(false);
      setMsg("Access revoked.");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="space-y-6">
      <PageHeader
        title="Connections"
        description="Connect an agent from a catalog entry or a one-time link. No developer configuration."
      />
      {error ? <Alert tone="error">{error}</Alert> : null}
      {msg ? <Alert tone="success">{msg}</Alert> : null}
      <Card className="space-y-4">
        <Button onClick={mint} disabled={busy}>
          Create pairing link
        </Button>
        {link ? (
          <p className="text-sm text-ink">
            Code: <code className="rounded bg-canvas px-1.5 py-0.5">{link}</code>
          </p>
        ) : null}
        <form className="space-y-4" onSubmit={grant}>
          <Field id="conn-id" label="Connection id">
            <Input id="conn-id" value={conn} onChange={(e) => setConn(e.target.value)} required />
          </Field>
          <Field id="conn-preset" label="Permission preset">
            <Select
              id="conn-preset"
              value={preset}
              onChange={(e) => setPreset(asGrantPreset(e.target.value))}
            >
              <option value="read_active_projects">Can read my active projects</option>
              <option value="read_project">Can read a specific project</option>
              <option value="always_ask_before_sending">Always ask before sending</option>
            </Select>
          </Field>
          <Field
            id="conn-project"
            label="Project id"
            hint="Optional, used with a specific project grant."
          >
            <Input id="conn-project" value={project} onChange={(e) => setProject(e.target.value)} />
          </Field>
          <p className="text-sm text-muted">{presetHelp(preset)}</p>
          <div className="flex flex-wrap gap-2">
            <Button type="submit" disabled={busy}>
              Confirm grant
            </Button>
            <Button
              variant="danger"
              onClick={() => setConfirmRevoke(true)}
              disabled={busy || !conn}
            >
              Revoke access
            </Button>
          </div>
        </form>
      </Card>
      <Card className="space-y-4">
        <h2 className="text-lg font-semibold text-ink">Assistant catalog</h2>
        <Field id="assistant" label="Assistant">
          <Select id="assistant" value={assistant} onChange={(e) => setAssistant(e.target.value)}>
            {(assistants.length ? assistants : [{ id: "cursor", name: "Cursor", supported: true, notes: "" }]).map(
              (item) => (
                <option key={item.id} value={item.id} disabled={!item.supported}>
                  {item.name}
                </option>
              )
            )}
          </Select>
        </Field>
        <div className="flex flex-wrap gap-2">
          <Button onClick={loadRecipe} disabled={busy || !conn}>
            Generate recipe
          </Button>
          <Button variant="secondary" onClick={copyRecipe} disabled={!recipe}>
            Copy config
          </Button>
        </div>
        {recipe ? (
          <div className="space-y-2">
            <p className="text-sm text-muted">{recipe.instructions}</p>
            <pre className="overflow-x-auto rounded bg-canvas p-3 text-xs text-ink">
              {JSON.stringify(recipe.snippet, null, 2)}
            </pre>
          </div>
        ) : null}
      </Card>
      <ConfirmDialog
        open={confirmRevoke}
        title="Revoke access"
        message="This connection will no longer be able to read or act on your space."
        confirmLabel="Revoke"
        danger
        busy={busy}
        onConfirm={revoke}
        onCancel={() => setConfirmRevoke(false)}
      />
    </section>
  );
}

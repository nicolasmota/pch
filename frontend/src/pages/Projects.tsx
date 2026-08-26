import { FormEvent, useState } from "react";
import { api, errorMessage } from "../api/client";
import type { Project } from "../api/types";
import Alert from "../components/Alert";
import Badge from "../components/Badge";
import Button from "../components/Button";
import Card from "../components/Card";
import DataList from "../components/DataList";
import Field from "../components/Field";
import Input from "../components/Input";
import PageHeader from "../components/PageHeader";
import Spinner from "../components/Spinner";
import Textarea from "../components/Textarea";
import { useApi } from "../hooks/useApi";

function statusTone(status: string) {
  switch (status) {
    case "active":
      return "success" as const;
    case "paused":
      return "warning" as const;
    case "done":
      return "neutral" as const;
    case "archived":
      return "neutral" as const;
    default:
      return "neutral" as const;
  }
}

export default function Projects() {
  const { data, loading, error, reload } = useApi<Project[]>(() => api("/v1/projects"));
  const [title, setTitle] = useState("Atlas");
  const [charter, setCharter] = useState("");
  const [formError, setFormError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function create(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setFormError(null);
    try {
      await api("/v1/projects", {
        method: "POST",
        body: JSON.stringify({ title, charter, status: "active" }),
      });
      setTitle("");
      setCharter("");
      reload();
    } catch (err) {
      setFormError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="space-y-6">
      <PageHeader title="Projects" description="Active work you want agents to understand." />
      {error ? <Alert tone="error">{error}</Alert> : null}
      {formError ? <Alert tone="error">{formError}</Alert> : null}
      <Card>
        <form className="space-y-4" onSubmit={create}>
          <Field id="project-title" label="Title">
            <Input
              id="project-title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </Field>
          <Field id="project-charter" label="Charter">
            <Textarea
              id="project-charter"
              value={charter}
              onChange={(e) => setCharter(e.target.value)}
            />
          </Field>
          <Button type="submit" disabled={busy}>
            Create project
          </Button>
        </form>
      </Card>
      {loading ? (
        <Spinner />
      ) : (
        <DataList
          items={data ?? []}
          keyOf={(p) => p.id}
          empty="No projects yet. Create one to get started."
          render={(p) => (
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <div>
                <p className="font-medium text-ink">{p.title}</p>
                <p className="text-xs text-muted">{p.id}</p>
              </div>
              <Badge tone={statusTone(p.status)}>{p.status}</Badge>
            </div>
          )}
        />
      )}
    </section>
  );
}

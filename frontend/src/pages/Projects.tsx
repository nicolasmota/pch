import { FormEvent, useEffect, useState } from "react";
import { api, errorMessage } from "../api/client";
import type { Project, Relation } from "../api/types";
import Alert from "../components/Alert";
import Badge from "../components/Badge";
import Button from "../components/Button";
import Card from "../components/Card";
import Field from "../components/Field";
import Input from "../components/Input";
import PageHeader from "../components/PageHeader";
import Select from "../components/Select";
import Spinner from "../components/Spinner";
import Textarea from "../components/Textarea";
import { useApi } from "../hooks/useApi";

type ProjectStatus = "active" | "paused" | "done" | "archived";
type OperationalPhase =
  | "planning"
  | "comparing_itineraries"
  | "waiting_for_approval"
  | "choosing_hotel"
  | "other";

function asProjectStatus(status: string): ProjectStatus {
  switch (status) {
    case "active":
    case "paused":
    case "done":
    case "archived":
      return status;
    default:
      return "archived";
  }
}

function statusTone(status: ProjectStatus) {
  switch (status) {
    case "active":
      return "success" as const;
    case "paused":
      return "warning" as const;
    case "done":
      return "neutral" as const;
    case "archived":
      return "neutral" as const;
    default: {
      const _exhaustive: never = status;
      return _exhaustive;
    }
  }
}

function phaseLabel(phase: OperationalPhase): string {
  switch (phase) {
    case "planning":
      return "Planning";
    case "comparing_itineraries":
      return "Comparing itineraries";
    case "waiting_for_approval":
      return "Waiting for approval";
    case "choosing_hotel":
      return "Choosing hotel";
    case "other":
      return "Other";
    default: {
      const _exhaustive: never = phase;
      return _exhaustive;
    }
  }
}

const PHASES: OperationalPhase[] = [
  "planning",
  "comparing_itineraries",
  "waiting_for_approval",
  "choosing_hotel",
  "other",
];

type RelationKind = "owned_by" | "depends_on" | "blocked_by" | "related_to";

function asRelationKind(value: string): RelationKind {
  switch (value) {
    case "owned_by":
    case "depends_on":
    case "blocked_by":
    case "related_to":
      return value;
    default:
      return "related_to";
  }
}

function relationLabel(kind: RelationKind): string {
  switch (kind) {
    case "owned_by":
      return "owned by";
    case "depends_on":
      return "depends on";
    case "blocked_by":
      return "blocked by";
    case "related_to":
      return "related to";
    default: {
      const _exhaustive: never = kind;
      return _exhaustive;
    }
  }
}

const RELATION_KINDS: RelationKind[] = ["owned_by", "depends_on", "blocked_by", "related_to"];

function ProjectRow({
  project,
  relations,
  onSaved,
  onRelationsChanged,
  onError,
}: {
  project: Project;
  relations: Relation[];
  onSaved: () => void;
  onRelationsChanged: () => void;
  onError: (message: string | null) => void;
}) {
  const [phase, setPhase] = useState(project.operational_phase ?? "");
  const [step, setStep] = useState(project.current_step ?? "");
  const [intent, setIntent] = useState(project.situation_intent ?? "");
  const [busy, setBusy] = useState(false);
  const [newType, setNewType] = useState<RelationKind>("depends_on");
  const [newTarget, setNewTarget] = useState("");

  useEffect(() => {
    setPhase(project.operational_phase ?? "");
    setStep(project.current_step ?? "");
    setIntent(project.situation_intent ?? "");
  }, [project.operational_phase, project.current_step, project.situation_intent]);

  const mine = relations.filter(
    (row) => row.from_id === project.id || row.to_id === project.id,
  );

  async function save() {
    setBusy(true);
    onError(null);
    try {
      await api(`/v1/projects/${project.id}`, {
        method: "PATCH",
        body: JSON.stringify({
          operational_phase: phase || null,
          current_step: step.trim() || null,
          situation_intent: intent.trim() || null,
        }),
      });
      onSaved();
    } catch (err) {
      onError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function addRelation() {
    const target = newTarget.trim();
    if (!target) {
      return;
    }
    setBusy(true);
    onError(null);
    try {
      await api("/v1/relations", {
        method: "POST",
        body: JSON.stringify({
          from_id: project.id,
          to_id: target,
          relation_type: newType,
        }),
      });
      setNewTarget("");
      onRelationsChanged();
    } catch (err) {
      onError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function changeType(relationId: string, relationType: RelationKind) {
    setBusy(true);
    onError(null);
    try {
      await api(`/v1/relations/${relationId}`, {
        method: "PATCH",
        body: JSON.stringify({ relation_type: relationType }),
      });
      onRelationsChanged();
    } catch (err) {
      onError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function removeRelation(relationId: string) {
    setBusy(true);
    onError(null);
    try {
      await api(`/v1/relations/${relationId}`, { method: "DELETE" });
      onRelationsChanged();
    } catch (err) {
      onError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <Card className="space-y-3">
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <div>
          <p className="font-medium text-ink">{project.title}</p>
          <p className="text-xs text-muted">{project.id}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Badge tone={statusTone(asProjectStatus(project.status))}>{project.status}</Badge>
          {phase ? <Badge>{phaseLabel(phase as OperationalPhase)}</Badge> : null}
        </div>
      </div>
      <div className="grid gap-3 md:grid-cols-3">
        <Field id={`${project.id}-phase`} label="Operational phase" hint="Not project status. Not SharedState.">
          <Select
            id={`${project.id}-phase`}
            value={phase}
            onChange={(e) => setPhase(e.target.value)}
          >
            <option value="">Unset</option>
            {PHASES.map((value) => (
              <option key={value} value={value}>
                {phaseLabel(value)}
              </option>
            ))}
          </Select>
        </Field>
        <Field id={`${project.id}-step`} label="Current step">
          <Input
            id={`${project.id}-step`}
            value={step}
            maxLength={200}
            onChange={(e) => setStep(e.target.value)}
          />
        </Field>
        <Field id={`${project.id}-intent`} label="Situation intent" hint="Not an ActionIntent approval.">
          <Input
            id={`${project.id}-intent`}
            value={intent}
            maxLength={200}
            onChange={(e) => setIntent(e.target.value)}
          />
        </Field>
      </div>
      <Button type="button" onClick={() => void save()} disabled={busy}>
        Save operational state
      </Button>
      <div className="space-y-2 border-t border-line pt-3">
        <p className="text-sm font-medium text-ink">Relations</p>
        {mine.length === 0 ? (
          <p className="text-xs text-muted">No typed links yet. Goal membership is not owned_by.</p>
        ) : null}
        {mine.map((row) => {
          const kind = asRelationKind(row.relation_type);
          const other = row.from_id === project.id ? row.to_id : row.from_id;
          return (
            <div key={row.id} className="flex flex-wrap items-center gap-2">
              <Select
                aria-label={`Relation type for ${row.id}`}
                value={kind}
                onChange={(e) => void changeType(row.id, asRelationKind(e.target.value))}
                disabled={busy}
              >
                {RELATION_KINDS.map((value) => (
                  <option key={value} value={value}>
                    {relationLabel(value)}
                  </option>
                ))}
              </Select>
              <span className="text-sm text-ink">{other}</span>
              <Button
                type="button"
                variant="danger"
                onClick={() => void removeRelation(row.id)}
                disabled={busy}
              >
                Remove
              </Button>
            </div>
          );
        })}
        <div className="flex flex-wrap items-end gap-2">
          <Field id={`${project.id}-rel-type`} label="Link type">
            <Select
              id={`${project.id}-rel-type`}
              value={newType}
              onChange={(e) => setNewType(asRelationKind(e.target.value))}
            >
              {RELATION_KINDS.map((value) => (
                <option key={value} value={value}>
                  {relationLabel(value)}
                </option>
              ))}
            </Select>
          </Field>
          <Field id={`${project.id}-rel-to`} label="Other end id">
            <Input
              id={`${project.id}-rel-to`}
              value={newTarget}
              onChange={(e) => setNewTarget(e.target.value)}
              placeholder="prj_… or per_…"
            />
          </Field>
          <Button type="button" onClick={() => void addRelation()} disabled={busy || !newTarget.trim()}>
            Add relation
          </Button>
        </div>
      </div>
    </Card>
  );
}

export default function Projects() {
  const { data, loading, error, reload } = useApi<Project[]>(() => api("/v1/projects"));
  const relations = useApi<Relation[]>(() => api("/v1/relations"));
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
      <PageHeader
        title="Projects"
        description="Active work you want agents to understand — including operational phase, situation intent, and typed relations."
      />
      {error ? <Alert tone="error">{error}</Alert> : null}
      {relations.error ? <Alert tone="error">{relations.error}</Alert> : null}
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
      {loading || relations.loading ? <Spinner /> : null}
      {!loading && (data ?? []).length === 0 ? (
        <p className="text-sm text-muted">No projects yet. Create one to get started.</p>
      ) : null}
      {(data ?? []).map((project) => (
        <ProjectRow
          key={project.id}
          project={project}
          relations={relations.data ?? []}
          onSaved={reload}
          onRelationsChanged={relations.reload}
          onError={setFormError}
        />
      ))}
    </section>
  );
}

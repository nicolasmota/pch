import { FormEvent, useState } from "react";
import type { ContractItem, SituationResponse } from "../api/types";
import Alert from "./Alert";
import Badge from "./Badge";
import Button from "./Button";
import Card from "./Card";
import Field from "./Field";
import Input from "./Input";
import PageHeader from "./PageHeader";
import Spinner from "./Spinner";
import Textarea from "./Textarea";

type Props = {
  ownerName: string;
  keyLine: string | null;
  data: SituationResponse | undefined;
  loading: boolean;
  error: string | null;
  busy: boolean;
  onRestart: () => void;
  onOpen: (path: string) => void;
  onCapture: (input: { title?: string; statement: string }) => Promise<void>;
};

function formatPhase(phase: string | null | undefined): string | null {
  if (!phase) return null;
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
    default:
      return phase.replaceAll("_", " ");
  }
}

function contractItemText(item: ContractItem): string {
  const title = item.body.title;
  if (typeof title === "string" && title.trim()) return title;
  const statement = item.body.statement;
  if (typeof statement === "string" && statement.trim()) return statement;
  const key = item.body.key;
  if (typeof key === "string" && key.trim()) {
    return `${key}: ${String(item.body.value ?? "")}`;
  }
  return item.ref.summary;
}

function ItemList({ heading, items }: { heading: string; items: ContractItem[] }) {
  if (!items.length) return null;
  return (
    <Card>
      <h2 className="text-sm font-semibold text-ink">{heading}</h2>
      <ul className="mt-2 list-disc space-y-1 pl-5">
        {items.map((item) => (
          <li key={item.ref.id} className="text-sm text-ink">
            {contractItemText(item)}
          </li>
        ))}
      </ul>
    </Card>
  );
}

export default function SituationBoard({
  ownerName,
  keyLine,
  data,
  loading,
  error,
  busy,
  onRestart,
  onOpen,
  onCapture,
}: Props) {
  const [title, setTitle] = useState("");
  const [fact, setFact] = useState("");

  if (loading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Home" description="What matters now on this device." />
        <Spinner label="Loading situation" />
      </div>
    );
  }

  const contract = data?.contract ?? null;
  const situation = contract?.situation ?? null;
  const heading = situation?.title || data?.project?.title || "Home";
  const phase = formatPhase(situation?.operational_phase);
  const step = situation?.current_step?.trim() || null;
  const intent = situation?.situation_intent?.trim() || null;
  const empty = !data?.project;

  async function submit(event: FormEvent) {
    event.preventDefault();
    await onCapture(empty ? { title: title.trim(), statement: fact } : { statement: fact });
    setFact("");
    if (empty) {
      setTitle("");
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={empty ? "Home" : heading}
        description={
          empty
            ? "Name what's in play and one fact you want agents to start from."
            : intent || "What matters now on this device."
        }
      />
      {error ? <Alert tone="error">{error}</Alert> : null}
      {keyLine ? <p className="text-sm text-muted">{keyLine}</p> : null}
      <p className="text-sm text-muted">
        Owner on this device: <strong className="text-ink">{ownerName || "unset"}</strong>
      </p>

      {empty ? null : (
        <>
          {phase || step || typeof contract?.sufficient === "boolean" ? (
            <div className="flex flex-wrap gap-2">
              {phase ? <Badge tone="success">{phase}</Badge> : null}
              {step ? <Badge>{step}</Badge> : null}
              {typeof contract?.sufficient === "boolean" ? (
                <Badge tone={contract.sufficient ? "success" : "warning"}>
                  {contract.sufficient ? "Package sufficient" : "Package not sufficient"}
                </Badge>
              ) : null}
            </div>
          ) : null}
          <ItemList heading="Goals" items={contract?.goals ?? []} />
          <ItemList heading="Preferences" items={contract?.preferences ?? []} />
          <ItemList heading="Memories" items={contract?.memories ?? []} />
          <ItemList heading="Decisions" items={contract?.decisions ?? []} />
          {contract?.candidates.length ? (
            <Card>
              <h2 className="text-sm font-semibold text-ink">Also plausible</h2>
              <ul className="mt-2 list-disc space-y-1 pl-5">
                {contract.candidates.map((candidate) => (
                  <li key={candidate.project_id} className="text-sm text-ink">
                    {candidate.title}
                  </li>
                ))}
              </ul>
            </Card>
          ) : null}
          {contract?.omissions.length ? (
            <Card>
              <h2 className="text-sm font-semibold text-ink">Withheld</h2>
              <ul className="mt-2 list-disc space-y-1 pl-5">
                {contract.omissions.map((note) => (
                  <li key={`${note.category}-${note.label}`} className="text-sm text-muted">
                    {note.label} ({note.count})
                  </li>
                ))}
              </ul>
            </Card>
          ) : null}
        </>
      )}

      <Card>
        <form className="space-y-4" onSubmit={submit}>
          {empty ? (
            <Field id="capture-title" label="What's in play">
              <Input
                id="capture-title"
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                placeholder="Europe trip"
                autoComplete="off"
              />
            </Field>
          ) : null}
          <Field id="capture-fact" label="A durable fact">
            <Textarea
              id="capture-fact"
              value={fact}
              onChange={(event) => setFact(event.target.value)}
              placeholder="Ten-day trip for two"
            />
          </Field>
          <Button type="submit" disabled={busy}>
            {empty ? "Put this in the vault" : "Add this fact"}
          </Button>
        </form>
      </Card>

      <div className="flex flex-wrap gap-2">
        {empty ? null : (
          <>
            <Button variant="secondary" onClick={() => onOpen("/projects")}>
              Projects
            </Button>
            <Button variant="secondary" onClick={() => onOpen("/connections")}>
              Agents
            </Button>
            <Button variant="secondary" onClick={() => onOpen("/review")}>
              Review
            </Button>
          </>
        )}
        <Button variant="danger" onClick={onRestart} disabled={busy}>
          Restart setup
        </Button>
      </div>
    </div>
  );
}

import { useCallback, useEffect, useState } from "react";
import { api, errorMessage } from "../api/client";
import type { SimRun, SimTick } from "../api/types";
import Alert from "../components/Alert";
import Button from "../components/Button";
import Card from "../components/Card";
import JsonViewer from "../components/JsonViewer";
import PageHeader from "../components/PageHeader";
import Spinner from "../components/Spinner";
import { useApi } from "../hooks/useApi";

async function fetchRun(): Promise<SimRun | null> {
  try {
    const data = await api<SimRun>("/v1/sim/runs");
    const ticks = await api<SimTick[]>(`/v1/sim/runs/${data.id}/ticks`);
    return { ...data, ticks };
  } catch {
    return null;
  }
}

export default function Sim() {
  const load = useCallback(() => fetchRun(), []);
  const { data: run, loading, error, reload } = useApi(load);
  const [detail, setDetail] = useState<SimTick | null>(null);
  const [objectView, setObjectView] = useState<unknown>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [paired, setPaired] = useState(false);

  useEffect(() => {
    if (run?.status !== "running" && run?.status !== "paused") {
      return;
    }
    const handle = window.setInterval(() => {
      reload();
    }, 1000);
    return () => window.clearInterval(handle);
  }, [run?.status, reload]);

  async function start() {
    setBusy(true);
    setActionError(null);
    setDetail(null);
    setObjectView(null);
    try {
      await api<SimRun>("/v1/sim/runs", {
        method: "POST",
        body: JSON.stringify({
          persona_id: "lived-stretch",
          paired_assistant: paired,
          auto_accept: true,
        }),
      });
      reload();
    } catch (err) {
      setActionError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function command(kind: "pause" | "resume" | "stop") {
    if (!run) return;
    setBusy(true);
    try {
      await api<SimRun>(`/v1/sim/runs/${run.id}/${kind}`, { method: "POST" });
      reload();
    } catch (err) {
      setActionError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function openTick(seq: number) {
    if (!run) return;
    setBusy(true);
    try {
      const tick = await api<SimTick>(`/v1/sim/runs/${run.id}/ticks/${seq}`);
      setDetail(tick);
      setObjectView(null);
      const objectId = tick.result?.object_id;
      if (typeof objectId === "string" && objectId) {
        const obj = await api(`/v1/sim/objects/${objectId}`);
        setObjectView(obj);
      }
    } catch (err) {
      setActionError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  const shownError = actionError || error;

  return (
    <section className="space-y-6">
      <PageHeader
        title="Simulator"
        description="Watch a scripted person fill an isolated Hub and then ask it questions."
      />
      {shownError ? <Alert tone="error">{shownError}</Alert> : null}
      <Card>
        <div className="flex flex-wrap items-center gap-2">
          <Button onClick={() => void start()} disabled={busy}>
            Start lived-stretch
          </Button>
          <Button variant="secondary" onClick={() => void command("pause")} disabled={busy || !run}>
            Pause
          </Button>
          <Button variant="secondary" onClick={() => void command("resume")} disabled={busy || !run}>
            Resume
          </Button>
          <Button variant="secondary" onClick={() => void command("stop")} disabled={busy || !run}>
            Stop
          </Button>
          <label className="ml-2 flex items-center gap-2 text-sm text-ink">
            <input
              type="checkbox"
              checked={paired}
              onChange={(event) => setPaired(event.target.checked)}
            />
            Paired assistant path
          </label>
        </div>
        {run ? (
          <p className="mt-3 text-sm text-muted">
            {run.status} · seq {run.current_seq} · objects {run.object_count ?? 0} · queries{" "}
            {run.query_count ?? 0}
          </p>
        ) : (
          <p className="mt-3 text-sm text-muted">
            No run yet. Isolated space only — not your everyday vault.
          </p>
        )}
      </Card>
      {loading ? <Spinner /> : null}
      {run?.ticks?.length ? (
        <Card>
          <ul className="space-y-1">
            {run.ticks.map((tick) => (
              <li key={tick.seq}>
                <button
                  type="button"
                  className="w-full rounded-md px-2 py-1.5 text-left text-sm text-ink hover:bg-sidebar-active/20"
                  onClick={() => void openTick(tick.seq)}
                >
                  #{tick.seq} {tick.role} {tick.action} · {tick.status}
                  {tick.via ? ` · ${tick.via}` : ""}
                </button>
              </li>
            ))}
          </ul>
        </Card>
      ) : null}
      {detail ? (
        <Card>
          <p className="mb-2 text-sm font-medium text-ink">
            Tick #{detail.seq} input and result
          </p>
          <JsonViewer value={{ input: detail.input, result: detail.result }} />
        </Card>
      ) : null}
      {objectView ? (
        <Card>
          <p className="mb-2 text-sm font-medium text-ink">Hub object</p>
          <JsonViewer value={objectView} />
        </Card>
      ) : null}
    </section>
  );
}

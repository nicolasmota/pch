import { useEffect, useState } from "react";
import { Route, Routes } from "react-router-dom";
import { bootstrap, errorMessage } from "./api/client";
import Alert from "./components/Alert";
import Button from "./components/Button";
import Sidebar from "./components/Sidebar";
import Spinner from "./components/Spinner";
import Access from "./pages/Access";
import Approvals from "./pages/Approvals";
import Audit from "./pages/Audit";
import Conflicts from "./pages/Conflicts";
import Connections from "./pages/Connections";
import Connectors from "./pages/Connectors";
import Marketplace from "./pages/Marketplace";
import Plugins from "./pages/Plugins";
import ExportPage from "./pages/Export";
import Handoff from "./pages/Handoff";
import ImportPage from "./pages/Import";
import Memories from "./pages/Memories";
import Projects from "./pages/Projects";
import ReviewQueue from "./pages/ReviewQueue";
import Search from "./pages/Search";
import Setup from "./pages/Setup";
import Sim from "./pages/Sim";

type BootStatus = "loading" | "ready" | "error";

export default function App() {
  const [status, setStatus] = useState<BootStatus>("loading");
  const [error, setError] = useState<string | null>(null);
  const [navOpen, setNavOpen] = useState(false);
  const [attempt, setAttempt] = useState(0);

  const [simEnabled, setSimEnabled] = useState(false);

  useEffect(() => {
    let cancelled = false;
    bootstrap()
      .then((data) => {
        if (!cancelled) {
          setSimEnabled(Boolean(data.sim_enabled));
          setStatus("ready");
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(errorMessage(err));
          setStatus("error");
        }
      });
    return () => {
      cancelled = true;
    };
  }, [attempt]);

  if (status === "loading") {
    return (
      <div className="flex min-h-screen items-center justify-center bg-canvas">
        <Spinner label="Starting hub" />
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="flex min-h-screen items-center justify-center bg-canvas p-6">
        <div className="w-full max-w-md space-y-4">
          <h1 className="text-xl font-semibold text-ink">Could not start the hub</h1>
          <Alert tone="error">{error}</Alert>
          <Button
            onClick={() => {
              setStatus("loading");
              setError(null);
              setAttempt((n) => n + 1);
            }}
          >
            Try again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-canvas lg:flex">
      <div className="hidden w-60 shrink-0 lg:block">
        <div className="fixed inset-y-0 left-0 w-60">
          <Sidebar simEnabled={simEnabled} />
        </div>
      </div>
      {navOpen ? (
        <div className="fixed inset-0 z-40 lg:hidden">
          <button
            type="button"
            className="absolute inset-0 bg-black/40"
            aria-label="Close navigation"
            onClick={() => setNavOpen(false)}
          />
          <div className="relative h-full w-60">
            <Sidebar simEnabled={simEnabled} onNavigate={() => setNavOpen(false)} />
          </div>
        </div>
      ) : null}
      <div className="flex min-h-screen min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-line bg-surface px-4 py-3 lg:hidden">
          <p className="font-semibold text-ink">Context Hub</p>
          <Button variant="secondary" onClick={() => setNavOpen(true)}>
            Menu
          </Button>
        </header>
        <main className="mx-auto w-full max-w-3xl flex-1 px-4 py-8 sm:px-6">
          <Routes>
            <Route path="/" element={<Setup />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/memories" element={<Memories />} />
            <Route path="/search" element={<Search />} />
            <Route path="/sim" element={<Sim />} />
            <Route path="/connections" element={<Connections />} />
            <Route path="/connectors" element={<Connectors />} />
            <Route path="/plugins" element={<Plugins />} />
            <Route path="/marketplace" element={<Marketplace />} />
            <Route path="/access" element={<Access />} />
            <Route path="/handoff" element={<Handoff />} />
            <Route path="/review" element={<ReviewQueue />} />
            <Route path="/conflicts" element={<Conflicts />} />
            <Route path="/approvals" element={<Approvals />} />
            <Route path="/audit" element={<Audit />} />
            <Route path="/export" element={<ExportPage />} />
            <Route path="/import" element={<ImportPage />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

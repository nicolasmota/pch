import { useEffect, useState } from "react";
import { api, errorMessage } from "../api/client";
import Alert from "../components/Alert";
import Button from "../components/Button";
import Card from "../components/Card";
import PageHeader from "../components/PageHeader";

type Listing = {
  plugin_id: string;
  name: string;
  description: string;
  publisher: string;
  origin?: string;
  installed?: boolean;
  installed_state?: string;
  withdrawn?: { reason?: string } | null;
  versions?: { version: string; permissions_summary?: { hosts?: string[] } }[];
};

type Catalog = {
  listings?: Listing[];
  publishers?: Record<string, { name: string; verification?: string }>;
  offline?: boolean;
  stale?: boolean;
  source?: string;
};

export default function Marketplace() {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);

  async function load() {
    const data = await api<Catalog>("/v1/marketplace/catalog");
    setCatalog(data);
  }

  useEffect(() => {
    load().catch((err) => setError(errorMessage(err)));
  }, []);

  async function install(pluginId: string) {
    setBusy(true);
    setError(null);
    try {
      const inst = await api<{ id: string }>("/v1/marketplace/install", {
        method: "POST",
        body: JSON.stringify({ plugin_id: pluginId }),
      });
      setMsg(`Installed ${pluginId}. Open Plugins to review permissions (${inst.id}).`);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  const publishers = catalog?.publishers || {};

  return (
    <section className="space-y-6">
      <PageHeader
        title="Marketplace"
        description="Browse available plugins. Install still requires the same consent screen."
      />
      {catalog?.source === "bundled" ? (
        <Alert tone="info">Showing first-party plugins shipped with this Hub. A remote catalog is optional.</Alert>
      ) : null}
      {catalog?.offline ? <Alert tone="info">Remote catalog is unreachable. Showing a cached or empty list. Installed plugins keep working.</Alert> : null}
      {catalog?.stale ? <Alert tone="info">Catalog copy is stale.</Alert> : null}
      {error ? <Alert tone="error">{error}</Alert> : null}
      {msg ? <Alert tone="success">{msg}</Alert> : null}
      <div className="flex gap-2">
        <Button
          variant="secondary"
          disabled={busy}
          onClick={() => {
            void api("/v1/marketplace/refresh", { method: "POST", body: "{}" })
              .then(() => load())
              .catch((err) => setError(errorMessage(err)));
          }}
        >
          Refresh catalog
        </Button>
      </div>
      {(catalog?.listings || []).map((listing) => {
        const pub = publishers[listing.publisher];
        const perms = listing.versions?.[listing.versions.length - 1]?.permissions_summary;
        return (
          <Card key={listing.plugin_id} className="space-y-2">
            <p className="font-medium text-ink">{listing.name}</p>
            <p className="text-sm text-muted">{listing.description}</p>
            <p className="text-sm text-muted">
              Publisher: {pub?.name || listing.publisher} · {pub?.verification || "community"}
            </p>
            {perms?.hosts ? <p className="text-sm text-muted">Hosts: {perms.hosts.join(", ")}</p> : null}
            {listing.withdrawn ? (
              <Alert tone="error">Withdrawn: {listing.withdrawn.reason || "removed from catalog"}</Alert>
            ) : listing.installed ? (
              <p className="text-sm text-muted">
                Already installed{listing.installed_state ? ` · ${listing.installed_state}` : ""}. Manage it in Plugins.
              </p>
            ) : (
              <Button onClick={() => void install(listing.plugin_id)} disabled={busy}>
                Install
              </Button>
            )}
          </Card>
        );
      })}
    </section>
  );
}

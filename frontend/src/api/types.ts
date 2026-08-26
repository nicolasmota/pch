export type SetupStatus = {
  initialized: boolean;
  in_progress: boolean;
  name: string | null;
};

export type BootstrapResponse = {
  owner_token: string;
  setup: SetupStatus;
};

export type SetupResponse = {
  person: { id: string; name: string };
  space_id: string;
  owner_token: string;
};

export type Project = {
  id: string;
  title: string;
  status: string;
  charter: string;
};

export type Memory = {
  id: string;
  statement: string;
  authority: string;
  kind: string;
};

export type MemoryVersion = Memory & {
  version: number;
  _recorded_at?: string;
};

export type Citation = {
  id: string;
  role?: string;
};

export type SearchHit = {
  id: string;
  type: string;
  title?: string;
  statement?: string;
  classification?: string;
  citations?: Citation[];
};

export type SearchResponse = {
  results: SearchHit[];
  redactions?: string[];
};

export type PairingLink = {
  link: string;
  code: string;
  connection_id: string;
};

export type GrantPreset = "read_active_projects" | "read_project" | "always_ask_before_sending";

export type Grant = {
  id: string;
  connection_id: string;
  status: string;
  summary_human: string;
  preset?: string | null;
};

export type MemoryProposal = {
  id: string;
  status: string;
  confidence?: number;
  evidence_refs?: string[];
  proposed_memory?: { statement: string };
  statement?: string;
};

export type Conflict = {
  id: string;
  kind: string;
  detail: string;
  status: string;
};

export type Approval = {
  id: string;
  connection_id: string;
  summary_human: string;
  basis_refs?: string[];
  status: string;
};

export type AuditEvent = {
  seq: number;
  actor: string;
  summary_human: string;
  created_at: string;
  kind: string;
  extra?: {
    contract_id?: string | null;
    purpose?: string;
    status?: string;
    situation?: string | null;
    item_refs?: { id: string; type: string }[];
    omission_categories?: { category: string; count: number }[];
  };
};

export type SharedState = {
  key: string;
  value: unknown;
  ttl_seconds: number;
  visibility: string;
};

export type ExportResult = {
  path: string;
  manifest_hash?: string;
  pca_version?: string;
};

export type StagingImport = {
  id: string;
  status: string;
  conflicts?: unknown[];
};

export type ImportApplyResult = {
  applied: number;
  staging_id: string;
};

export type AssistantCatalogEntry = {
  id: string;
  name: string;
  supported: boolean;
  notes: string;
};

export type AssistantRecipe = {
  assistant: string;
  instructions: string;
  snippet: { mcpServers: Record<string, unknown> };
};

export type ConnectorAccount = {
  id: string;
  kind: string;
  provider: string;
  status: string;
  account_label?: string;
  selection?: Record<string, unknown>;
  cadence_minutes?: number;
  last_sync?: {
    at?: string;
    outcome?: string;
    created?: number;
    updated?: number;
    tombstoned?: number;
    error?: string;
  } | null;
};

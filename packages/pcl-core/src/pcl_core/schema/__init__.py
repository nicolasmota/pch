from pcl_core.schema.action import ActionIntent, IntentStatus
from pcl_core.schema.approval import Approval, DecisionKind
from pcl_core.schema.artifact import Artifact, ArtifactKind
from pcl_core.schema.audit import AuditEvent, EventKind
from pcl_core.schema.conflict import Conflict, ConflictKind, ConflictStatus
from pcl_core.schema.connection import AgentConnection, ConnectionStatus
from pcl_core.schema.connector import (
    ConnectorAccount,
    ConnectorKind,
    ConnectorProvider,
    ConnectorStatus,
)
from pcl_core.schema.contract import (
    Citation,
    ConflictPair,
    ContextContract,
    ContextQuery,
    ContractItem,
    ItemRef,
    OmissionCategory,
    OmissionNote,
    RelationRef,
    ScopeSummary,
    SituationRef,
)
from pcl_core.schema.event import CalendarEvent, CalendarEventStatus
from pcl_core.schema.grant import PRESETS, Capability, Grant, GrantStatus
from pcl_core.schema.manifest import ContextManifest, DisclosedRef, ManifestStatus
from pcl_core.schema.memory import Memory, MemoryKind, SensitivityFlag
from pcl_core.schema.metadata import (
    Authority,
    Classification,
    EntityType,
    Retention,
    RetentionMode,
    UniversalMetadata,
)
from pcl_core.schema.person import Person
from pcl_core.schema.plugin import (
    Isolation,
    PluginInstallation,
    PluginManifest,
    PluginOrigin,
    PluginPermissions,
    PluginState,
    ProducesPermission,
)
from pcl_core.schema.portability import ExportRecord, ImportStaging, ResolutionChoice, StagingStatus
from pcl_core.schema.preference import Preference
from pcl_core.schema.profile import Profile
from pcl_core.schema.project import (
    Commitment,
    Decision,
    Goal,
    OperationalPhase,
    Project,
    ProjectStatus,
)
from pcl_core.schema.proposal import MemoryProposal, OperationalProposal, ProposalStatus
from pcl_core.schema.relation import Relation, RelationProposal, RelationType
from pcl_core.schema.space import ContextSpace
from pcl_core.schema.state import SharedState, StateVisibility

TYPE_MODELS = {
    EntityType.PERSON: Person,
    EntityType.SPACE: ContextSpace,
    EntityType.PROFILE: Profile,
    EntityType.PREFERENCE: Preference,
    EntityType.PROJECT: Project,
    EntityType.GOAL: Goal,
    EntityType.COMMITMENT: Commitment,
    EntityType.DECISION: Decision,
    EntityType.ARTIFACT: Artifact,
    EntityType.MEMORY: Memory,
    EntityType.CONNECTOR_ACCOUNT: ConnectorAccount,
    EntityType.EVENT: CalendarEvent,
    EntityType.PLUGIN: PluginInstallation,
    EntityType.RELATION: Relation,
}

__all__ = [
    "ActionIntent",
    "AgentConnection",
    "Approval",
    "Artifact",
    "ArtifactKind",
    "AuditEvent",
    "Authority",
    "CalendarEvent",
    "CalendarEventStatus",
    "Capability",
    "Classification",
    "Commitment",
    "Conflict",
    "ConflictKind",
    "ConflictStatus",
    "ConnectionStatus",
    "ConnectorAccount",
    "ConnectorKind",
    "ConnectorProvider",
    "ConnectorStatus",
    "Citation",
    "ConflictPair",
    "ContextContract",
    "ContextManifest",
    "ContextQuery",
    "ContextSpace",
    "ContractItem",
    "Decision",
    "DecisionKind",
    "DisclosedRef",
    "EntityType",
    "EventKind",
    "ExportRecord",
    "Goal",
    "Grant",
    "GrantStatus",
    "ImportStaging",
    "Isolation",
    "PluginInstallation",
    "PluginManifest",
    "PluginOrigin",
    "PluginPermissions",
    "PluginState",
    "ProducesPermission",
    "IntentStatus",
    "ItemRef",
    "ManifestStatus",
    "Memory",
    "MemoryKind",
    "MemoryProposal",
    "OmissionCategory",
    "OmissionNote",
    "OperationalPhase",
    "OperationalProposal",
    "PRESETS",
    "Person",
    "Preference",
    "Profile",
    "Project",
    "ProjectStatus",
    "ProposalStatus",
    "Relation",
    "RelationProposal",
    "RelationRef",
    "RelationType",
    "ResolutionChoice",
    "Retention",
    "RetentionMode",
    "ScopeSummary",
    "SensitivityFlag",
    "SituationRef",
    "SharedState",
    "StagingStatus",
    "StateVisibility",
    "TYPE_MODELS",
    "UniversalMetadata",
]

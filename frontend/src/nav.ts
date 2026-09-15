export type NavItem = { to: string; label: string; end?: boolean };
export type NavGroup = { heading: string; items: NavItem[] };

export const NAV_GROUPS: NavGroup[] = [
  {
    heading: "Start",
    items: [
      { to: "/", label: "Home", end: true },
      { to: "/sim", label: "Simulator" },
    ],
  },
  {
    heading: "Content",
    items: [
      { to: "/projects", label: "Projects" },
      { to: "/memories", label: "Memories" },
      { to: "/search", label: "Search" },
    ],
  },
  {
    heading: "Governance",
    items: [
      { to: "/review", label: "Review" },
      { to: "/conflicts", label: "Conflicts" },
      { to: "/approvals", label: "Approvals" },
      { to: "/access", label: "Access" },
      { to: "/audit", label: "Audit" },
    ],
  },
  {
    heading: "Connections",
    items: [
      { to: "/connections", label: "Agents" },
      { to: "/plugins", label: "Plugins" },
      { to: "/marketplace", label: "Marketplace" },
      { to: "/connectors", label: "Connectors" },
    ],
  },
  {
    heading: "Data",
    items: [
      { to: "/handoff", label: "Handoff" },
      { to: "/export", label: "Export" },
      { to: "/import", label: "Import" },
    ],
  },
];

export function visibleNavGroups(simEnabled: boolean): NavGroup[] {
  return NAV_GROUPS.map((group) => ({
    ...group,
    items: group.items.filter((item) => {
      if (item.to === "/sim") return simEnabled;
      if (item.to === "/marketplace") return false;
      return true;
    }),
  })).filter((group) => group.items.length > 0);
}

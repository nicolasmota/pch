export type NavItem = { to: string; label: string; end?: boolean };
export type NavGroup = {
  heading: string;
  items: NavItem[];
  collapsible?: boolean;
};

export const PRIMARY_NAV: NavItem[] = [
  { to: "/", label: "Home", end: true },
  { to: "/connections", label: "Agents" },
  { to: "/review", label: "Review" },
];

export const ADVANCED_NAV: NavItem[] = [
  { to: "/search", label: "Search" },
  { to: "/projects", label: "Projects" },
  { to: "/memories", label: "Memories" },
  { to: "/plugins", label: "Plugins" },
  { to: "/connectors", label: "Connectors" },
  { to: "/export", label: "Export" },
  { to: "/import", label: "Import" },
  { to: "/audit", label: "Audit" },
];

export function visibleNavGroups(simEnabled: boolean): NavGroup[] {
  const advanced = [...ADVANCED_NAV];
  if (simEnabled) {
    advanced.unshift({ to: "/sim", label: "Simulator" });
  }
  return [
    { heading: "Hub", items: PRIMARY_NAV },
    { heading: "Advanced", items: advanced, collapsible: true },
  ];
}

import { useMemo, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { visibleNavGroups, type NavItem } from "../nav";
import ThemeToggle from "./ThemeToggle";

type Props = {
  onNavigate?: () => void;
  simEnabled?: boolean;
};

function itemIsActive(item: NavItem, pathname: string): boolean {
  if (item.end) {
    return pathname === item.to;
  }
  return pathname === item.to || pathname.startsWith(`${item.to}/`);
}

function NavLinks({ items, onNavigate }: { items: NavItem[]; onNavigate?: () => void }) {
  return (
    <ul className="space-y-0.5">
      {items.map((item) => (
        <li key={item.to}>
          <NavLink
            to={item.to}
            end={item.end}
            onClick={onNavigate}
            className={({ isActive }) =>
              `block rounded-md px-2 py-1.5 text-sm ${
                isActive
                  ? "bg-sidebar-active text-white shadow-[inset_2px_0_0_0_var(--accent)]"
                  : "text-sidebar-ink hover:bg-sidebar-active/70"
              }`
            }
          >
            {item.label}
          </NavLink>
        </li>
      ))}
    </ul>
  );
}

export default function Sidebar({ onNavigate, simEnabled = false }: Props) {
  const groups = visibleNavGroups(simEnabled);
  const location = useLocation();
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const advancedItems = useMemo(
    () => groups.find((group) => group.collapsible)?.items ?? [],
    [groups],
  );
  const onAdvancedRoute = advancedItems.some((item) => itemIsActive(item, location.pathname));
  const showAdvanced = advancedOpen || onAdvancedRoute;

  return (
    <div className="flex h-full flex-col bg-sidebar text-sidebar-ink">
      <div className="border-b border-white/10 px-4 py-5">
        <p className="text-xs font-medium uppercase tracking-wider text-sidebar-muted">Personal</p>
        <h1 className="mt-1 text-lg font-semibold leading-tight">Context Hub</h1>
      </div>
      <nav aria-label="Main" className="flex-1 overflow-y-auto px-3 py-4">
        {groups.map((group) => {
          if (group.collapsible) {
            return (
              <div key={group.heading} className="mb-5">
                <button
                  type="button"
                  className="flex w-full items-center justify-between px-2 pb-1 text-left text-[11px] font-semibold uppercase tracking-wider text-sidebar-muted"
                  aria-expanded={showAdvanced}
                  onClick={() => {
                    if (onAdvancedRoute) {
                      return;
                    }
                    setAdvancedOpen((open) => !open);
                  }}
                >
                  {group.heading}
                  <span aria-hidden="true">{showAdvanced ? "−" : "+"}</span>
                </button>
                {showAdvanced ? <NavLinks items={group.items} onNavigate={onNavigate} /> : null}
              </div>
            );
          }
          return (
            <div key={group.heading} className="mb-5">
              <p className="px-2 pb-1 text-[11px] font-semibold uppercase tracking-wider text-sidebar-muted">
                {group.heading}
              </p>
              <NavLinks items={group.items} onNavigate={onNavigate} />
            </div>
          );
        })}
      </nav>
      <div className="border-t border-white/10 p-3">
        <ThemeToggle />
      </div>
    </div>
  );
}

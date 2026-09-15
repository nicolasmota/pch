import { NavLink } from "react-router-dom";
import { visibleNavGroups } from "../nav";
import ThemeToggle from "./ThemeToggle";

type Props = {
  onNavigate?: () => void;
  simEnabled?: boolean;
};

export default function Sidebar({ onNavigate, simEnabled = false }: Props) {
  const groups = visibleNavGroups(simEnabled);
  return (
    <div className="flex h-full flex-col bg-sidebar text-sidebar-ink">
      <div className="border-b border-white/10 px-4 py-5">
        <p className="text-xs font-medium uppercase tracking-wider text-sidebar-muted">Personal</p>
        <h1 className="mt-1 text-lg font-semibold leading-tight">Context Hub</h1>
      </div>
      <nav aria-label="Main" className="flex-1 overflow-y-auto px-3 py-4">
        {groups.map((group) => (
          <div key={group.heading} className="mb-5">
            <p className="px-2 pb-1 text-[11px] font-semibold uppercase tracking-wider text-sidebar-muted">
              {group.heading}
            </p>
            <ul className="space-y-0.5">
              {group.items.map((item) => (
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
          </div>
        ))}
      </nav>
      <div className="border-t border-white/10 p-3">
        <ThemeToggle />
      </div>
    </div>
  );
}

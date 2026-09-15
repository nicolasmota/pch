import { useTheme } from "../hooks/theme";

export default function ThemeToggle() {
  const { theme, toggle } = useTheme();
  const next = theme === "dark" ? "light" : "dark";
  return (
    <button
      type="button"
      onClick={toggle}
      className="flex w-full items-center justify-between rounded-md px-2 py-2 text-left text-sm text-sidebar-ink hover:bg-sidebar-active"
      aria-label={`Switch to ${next} theme`}
    >
      <span>Theme</span>
      <span className="text-sidebar-muted capitalize">{theme}</span>
    </button>
  );
}

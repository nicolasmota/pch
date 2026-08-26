import type { ReactNode } from "react";

type Tone = "error" | "success" | "info";

type Props = {
  tone?: Tone;
  children: ReactNode;
};

function toneClass(tone: Tone): string {
  switch (tone) {
    case "error":
      return "border-danger/40 bg-red-50 text-danger dark:bg-red-950/30";
    case "success":
      return "border-emerald-300 bg-emerald-50 text-emerald-800 dark:border-emerald-800 dark:bg-emerald-950/30 dark:text-emerald-200";
    case "info":
      return "border-line bg-canvas text-ink";
    default: {
      const _exhaustive: never = tone;
      return _exhaustive;
    }
  }
}

export default function Alert({ tone = "info", children }: Props) {
  return (
    <div
      role={tone === "error" ? "alert" : "status"}
      className={`rounded-md border px-3 py-2 text-sm ${toneClass(tone)}`}
    >
      {children}
    </div>
  );
}

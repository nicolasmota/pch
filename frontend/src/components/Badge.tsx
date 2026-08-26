import type { ReactNode } from "react";

type Tone = "neutral" | "success" | "warning" | "danger";

type Props = {
  tone?: Tone;
  children: ReactNode;
};

function toneClass(tone: Tone): string {
  switch (tone) {
    case "neutral":
      return "bg-canvas text-muted border-line";
    case "success":
      return "bg-emerald-50 text-emerald-800 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-200 dark:border-emerald-800";
    case "warning":
      return "bg-amber-50 text-amber-900 border-amber-200 dark:bg-amber-950/40 dark:text-amber-100 dark:border-amber-800";
    case "danger":
      return "bg-red-50 text-danger border-red-200 dark:bg-red-950/40 dark:border-red-900";
    default: {
      const _exhaustive: never = tone;
      return _exhaustive;
    }
  }
}

export default function Badge({ tone = "neutral", children }: Props) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium ${toneClass(tone)}`}
    >
      {children}
    </span>
  );
}

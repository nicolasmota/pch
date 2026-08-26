import type { ReactNode } from "react";

type Props = {
  id: string;
  label: string;
  children: ReactNode;
  hint?: string;
};

export default function Field({ id, label, children, hint }: Props) {
  return (
    <div className="flex flex-col gap-1.5">
      <label htmlFor={id} className="text-sm font-medium text-ink">
        {label}
      </label>
      {children}
      {hint ? <p className="text-xs text-muted">{hint}</p> : null}
    </div>
  );
}

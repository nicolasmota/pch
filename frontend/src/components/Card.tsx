import type { HTMLAttributes } from "react";

type Props = HTMLAttributes<HTMLDivElement>;

export default function Card({ className = "", ...props }: Props) {
  return (
    <div
      className={`rounded-lg border border-line bg-surface p-4 shadow-sm ${className}`}
      {...props}
    />
  );
}

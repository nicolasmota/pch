import type { ButtonHTMLAttributes } from "react";

type Variant = "primary" | "secondary" | "danger" | "ghost";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
};

function variantClass(variant: Variant): string {
  switch (variant) {
    case "primary":
      return "bg-ink text-canvas hover:opacity-90 dark:bg-accent dark:text-accent-fg";
    case "secondary":
      return "border border-line bg-surface text-ink hover:bg-canvas";
    case "danger":
      return "bg-danger text-white hover:opacity-90";
    case "ghost":
      return "bg-transparent text-ink hover:bg-line/60";
    default: {
      const _exhaustive: never = variant;
      return _exhaustive;
    }
  }
}

export default function Button({
  variant = "primary",
  className = "",
  type = "button",
  ...props
}: Props) {
  return (
    <button
      type={type}
      className={`inline-flex items-center justify-center rounded-md px-3 py-2 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-50 ${variantClass(variant)} ${className}`}
      {...props}
    />
  );
}

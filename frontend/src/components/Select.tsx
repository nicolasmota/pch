import type { SelectHTMLAttributes } from "react";
import { controlClass } from "./controlClass";

type Props = SelectHTMLAttributes<HTMLSelectElement>;

export default function Select({ className = "", children, ...props }: Props) {
  return (
    <select className={`${controlClass} ${className}`} {...props}>
      {children}
    </select>
  );
}

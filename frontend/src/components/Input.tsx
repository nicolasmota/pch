import type { InputHTMLAttributes } from "react";
import { controlClass } from "./controlClass";

type Props = InputHTMLAttributes<HTMLInputElement>;

export default function Input({ className = "", ...props }: Props) {
  return <input className={`${controlClass} ${className}`} {...props} />;
}

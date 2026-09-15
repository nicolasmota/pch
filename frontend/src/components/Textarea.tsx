import type { TextareaHTMLAttributes } from "react";
import { controlClass } from "./controlClass";

type Props = TextareaHTMLAttributes<HTMLTextAreaElement>;

export default function Textarea({ className = "", ...props }: Props) {
  return <textarea className={`${controlClass} min-h-24 ${className}`} {...props} />;
}

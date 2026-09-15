import { useEffect, useRef } from "react";
import type { ReactNode } from "react";
import Button from "./Button";

type Props = {
  open: boolean;
  title: string;
  onClose: () => void;
  children: ReactNode;
};

export default function Modal({ open, title, onClose, children }: Props) {
  const ref = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (open && !el.open) el.showModal();
    if (!open && el.open) el.close();
  }, [open]);

  return (
    <dialog
      ref={ref}
      onClose={onClose}
      className="w-full max-w-lg rounded-lg border border-line bg-surface p-0 text-ink shadow-xl backdrop:bg-black/40"
    >
      <div className="flex items-start justify-between gap-4 border-b border-line px-4 py-3">
        <h2 className="text-base font-semibold">{title}</h2>
        <Button variant="ghost" className="px-2 py-1" onClick={onClose} aria-label="Close">
          Close
        </Button>
      </div>
      <div className="px-4 py-4">{children}</div>
    </dialog>
  );
}

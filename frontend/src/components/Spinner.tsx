export default function Spinner({ label = "Loading" }: { label?: string }) {
  return (
    <div className="flex items-center gap-2 text-sm text-muted" role="status">
      <span className="inline-block size-4 animate-spin rounded-full border-2 border-line border-t-accent" />
      <span>{label}…</span>
    </div>
  );
}

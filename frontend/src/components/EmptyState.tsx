type Props = {
  title?: string;
  message: string;
};

export default function EmptyState({ title = "Nothing here yet", message }: Props) {
  return (
    <div className="rounded-lg border border-dashed border-line bg-surface px-4 py-8 text-center">
      <p className="text-sm font-medium text-ink">{title}</p>
      <p className="mt-1 text-sm text-muted">{message}</p>
    </div>
  );
}

type Props = {
  title: string;
  description?: string;
};

export default function PageHeader({ title, description }: Props) {
  return (
    <header className="space-y-1">
      <h1 className="text-2xl font-semibold tracking-tight text-ink">{title}</h1>
      {description ? <p className="max-w-2xl text-sm text-muted">{description}</p> : null}
    </header>
  );
}

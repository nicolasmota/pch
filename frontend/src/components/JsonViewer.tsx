type Props = {
  value: unknown;
};

export default function JsonViewer({ value }: Props) {
  return (
    <pre className="max-h-96 overflow-auto rounded-md border border-line bg-canvas p-3 text-xs leading-relaxed text-ink">
      {JSON.stringify(value, null, 2)}
    </pre>
  );
}

import type { ReactNode } from "react";
import EmptyState from "./EmptyState";

type Props<T> = {
  items: T[];
  keyOf: (item: T) => string;
  render: (item: T) => ReactNode;
  empty: string;
};

export default function DataList<T>({ items, keyOf, render, empty }: Props<T>) {
  if (items.length === 0) return <EmptyState message={empty} />;
  return (
    <ul className="divide-y divide-line overflow-hidden rounded-lg border border-line bg-surface">
      {items.map((item) => (
        <li key={keyOf(item)} className="px-4 py-3 text-sm">
          {render(item)}
        </li>
      ))}
    </ul>
  );
}

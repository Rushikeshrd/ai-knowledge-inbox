function formatTimestamp(iso) {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

export function ItemList({ items, isLoading }) {
  if (isLoading) {
    return <p className="text-sm text-neutral-500">Loading saved items...</p>;
  }

  if (items.length === 0) {
    return <p className="text-sm text-neutral-500">Nothing saved yet. Add a note or URL above.</p>;
  }

  return (
    <ul className="space-y-2">
      {items.map((item) => (
        <li key={item.id} className="rounded-lg border border-neutral-200 dark:border-neutral-800 p-3">
          <div className="flex items-center justify-between gap-2">
            <span className="text-xs font-medium uppercase tracking-wide text-neutral-500">
              {item.source_type}
            </span>
            <span className="text-xs text-neutral-400">{formatTimestamp(item.created_at)}</span>
          </div>
          <p className="mt-1 text-sm font-medium">{item.title}</p>
          {item.source_url && (
            <a
              href={item.source_url}
              target="_blank"
              rel="noreferrer"
              className="text-xs text-blue-600 dark:text-blue-400 break-all"
            >
              {item.source_url}
            </a>
          )}
          <p className="mt-1 text-xs text-neutral-500 line-clamp-2">{item.preview}</p>
          <p className="mt-1 text-xs text-neutral-400">{item.chunk_count} chunk{item.chunk_count === 1 ? "" : "s"} indexed</p>
        </li>
      ))}
    </ul>
  );
}

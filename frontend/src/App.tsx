import { IngestForm } from "./components/IngestForm";
import { ItemList } from "./components/ItemList";
import { QueryPanel } from "./components/QueryPanel";
import { useAskQuestion } from "./hooks/useAskQuestion";
import { useItems } from "./hooks/useItems";

function App() {
  const { items, isLoading, isSubmitting, error: itemsError, submit } = useItems();
  const { result, isLoading: isAsking, error: queryError, ask } = useAskQuestion();

  return (
    <div className="min-h-screen bg-white dark:bg-neutral-950 text-neutral-900 dark:text-neutral-100">
      <div className="mx-auto max-w-3xl px-4 py-8 space-y-8">
        <header>
          <h1 className="text-xl font-semibold">AI Knowledge Inbox</h1>
          <p className="text-sm text-neutral-500">Save notes and links, then ask questions over them.</p>
        </header>

        <section className="space-y-3">
          <h2 className="text-sm font-medium text-neutral-500 uppercase tracking-wide">Add content</h2>
          <IngestForm isSubmitting={isSubmitting} onSubmit={submit} />
          {itemsError && <p className="text-sm text-red-600 dark:text-red-400">{itemsError}</p>}
        </section>

        <section className="space-y-3">
          <h2 className="text-sm font-medium text-neutral-500 uppercase tracking-wide">
            Saved items {items.length > 0 && `(${items.length})`}
          </h2>
          <ItemList items={items} isLoading={isLoading} />
        </section>

        <section className="space-y-3">
          <h2 className="text-sm font-medium text-neutral-500 uppercase tracking-wide">Ask a question</h2>
          <QueryPanel isLoading={isAsking} error={queryError} result={result} onAsk={ask} />
        </section>
      </div>
    </div>
  );
}

export default App;

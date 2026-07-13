import { useState } from "react";

export function QueryPanel({ isLoading, error, result, onAsk }) {
  const [question, setQuestion] = useState("");

  const handleSubmit = (event) => {
    event.preventDefault();
    onAsk(question);
  };

  return (
    <div className="space-y-3">
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about your saved content..."
          className="flex-1 rounded-md border border-neutral-300 dark:border-neutral-700 bg-transparent p-2 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-400"
        />
        <button
          type="submit"
          disabled={isLoading || !question.trim()}
          className="px-4 py-1.5 text-sm rounded-md bg-neutral-900 text-white dark:bg-white dark:text-neutral-900 disabled:opacity-40 disabled:cursor-not-allowed hover:opacity-90 transition-opacity"
        >
          {isLoading ? "Thinking..." : "Ask"}
        </button>
      </form>

      {error && (
        <p className="text-sm text-red-600 dark:text-red-400 rounded-md border border-red-200 dark:border-red-900 bg-red-50 dark:bg-red-950/30 p-2">
          {error}
        </p>
      )}

      {result && (
        <div className="space-y-3 rounded-lg border border-neutral-200 dark:border-neutral-800 p-4">
          <p className="text-sm whitespace-pre-wrap">{result.answer}</p>

          {result.sources.length > 0 && (
            <div className="space-y-2 border-t border-neutral-200 dark:border-neutral-800 pt-3">
              <p className="text-xs font-medium uppercase tracking-wide text-neutral-500">
                Sources ({result.sources.length})
              </p>
              <ul className="space-y-2">
                {result.sources.map((source, idx) => (
                  <li key={`${source.item_id}-${idx}`} className="text-xs rounded-md bg-neutral-100 dark:bg-neutral-900 p-2">
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-medium">
                        [{idx + 1}] {source.title}
                      </span>
                      <span className="text-neutral-400">{(source.similarity * 100).toFixed(0)}% match</span>
                    </div>
                    <p className="mt-1 text-neutral-500">{source.snippet}</p>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

import { useState } from "react";
import type { FormEvent } from "react";
import type { IngestPayload, SourceType } from "../types/api";

interface IngestFormProps {
  isSubmitting: boolean;
  onSubmit: (payload: IngestPayload) => Promise<boolean>;
}

export function IngestForm({ isSubmitting, onSubmit }: IngestFormProps) {
  const [sourceType, setSourceType] = useState<SourceType>("note");
  const [text, setText] = useState("");
  const [url, setUrl] = useState("");
  const [feedback, setFeedback] = useState<string | null>(null);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setFeedback(null);

    const payload: IngestPayload =
      sourceType === "note" ? { source_type: "note", text } : { source_type: "url", url };

    const ok = await onSubmit(payload);
    if (ok) {
      setText("");
      setUrl("");
      setFeedback("Saved.");
    }
  };

  const isValid = sourceType === "note" ? text.trim().length > 0 : url.trim().length > 0;

  return (
    <form onSubmit={handleSubmit} className="space-y-3 rounded-lg border border-neutral-200 dark:border-neutral-800 p-4">
      <div className="flex gap-2">
        {(["note", "url"] as SourceType[]).map((type) => (
          <button
            key={type}
            type="button"
            onClick={() => setSourceType(type)}
            className={`px-3 py-1.5 text-sm rounded-md border transition-colors ${
              sourceType === type
                ? "bg-neutral-900 text-white border-neutral-900 dark:bg-white dark:text-neutral-900 dark:border-white"
                : "bg-transparent border-neutral-300 dark:border-neutral-700 text-neutral-600 dark:text-neutral-300"
            }`}
          >
            {type === "note" ? "Text note" : "URL"}
          </button>
        ))}
      </div>

      {sourceType === "note" ? (
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste or write a note..."
          rows={4}
          className="w-full rounded-md border border-neutral-300 dark:border-neutral-700 bg-transparent p-2 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-400"
        />
      ) : (
        <input
          type="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://example.com/article"
          className="w-full rounded-md border border-neutral-300 dark:border-neutral-700 bg-transparent p-2 text-sm focus:outline-none focus:ring-2 focus:ring-neutral-400"
        />
      )}

      <div className="flex items-center gap-3">
        <button
          type="submit"
          disabled={!isValid || isSubmitting}
          className="px-4 py-1.5 text-sm rounded-md bg-blue-600 text-white disabled:opacity-40 disabled:cursor-not-allowed hover:bg-blue-700 transition-colors"
        >
          {isSubmitting ? "Saving..." : "Save"}
        </button>
        {feedback && <span className="text-sm text-green-600 dark:text-green-400">{feedback}</span>}
      </div>
    </form>
  );
}

import { useCallback, useState } from "react";
import { ApiError, askQuestion } from "../api/client";

export function useAskQuestion() {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const ask = useCallback(async (question) => {
    if (!question.trim()) {
      setError("Enter a question first.");
      return;
    }
    setIsLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await askQuestion(question.trim());
      setResult(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to get an answer.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { result, isLoading, error, ask };
}

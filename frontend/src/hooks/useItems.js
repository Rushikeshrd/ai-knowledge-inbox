import { useCallback, useEffect, useState } from "react";
import { ApiError, fetchItems, ingestItem } from "../api/client";

export function useItems() {
  const [items, setItems] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const refresh = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchItems();
      setItems(data.items);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Failed to load saved items.");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const submit = useCallback(
    async (payload) => {
      setIsSubmitting(true);
      setError(null);
      try {
        await ingestItem(payload);
        await refresh();
        return true;
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "Failed to save item.");
        return false;
      } finally {
        setIsSubmitting(false);
      }
    },
    [refresh]
  );

  return { items, isLoading, isSubmitting, error, refresh, submit };
}

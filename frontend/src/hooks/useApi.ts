import { useCallback, useEffect, useRef, useState } from "react";
import { errorMessage } from "../api/client";

type UseApiState<T> = {
  data: T | undefined;
  loading: boolean;
  error: string | null;
  reload: () => void;
};

export function useApi<T>(loader: () => Promise<T>): UseApiState<T> {
  const loaderRef = useRef(loader);
  const [data, setData] = useState<T | undefined>(undefined);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [tick, setTick] = useState(0);

  const reload = useCallback(() => {
    setLoading(true);
    setError(null);
    setTick((n) => n + 1);
  }, []);

  useEffect(() => {
    loaderRef.current = loader;
  });

  useEffect(() => {
    let cancelled = false;
    loaderRef
      .current()
      .then((value) => {
        if (!cancelled) {
          setData(value);
          setLoading(false);
          setError(null);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(errorMessage(err));
          setLoading(false);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [tick]);

  return { data, loading, error, reload };
}

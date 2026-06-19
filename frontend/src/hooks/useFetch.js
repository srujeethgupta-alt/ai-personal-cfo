import { useState, useEffect, useCallback } from 'react';
import API from '../services/api';

export function useFetch(url, options = {}) {
  const { immediate = true, transform = (d) => d } = options;
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(immediate);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await API.get(url);
      const payload = response.data?.data || response.data;
      setData(transform(payload));
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  }, [url, transform]);

  const refetch = useCallback(() => fetchData(), [fetchData]);

  useEffect(() => {
    if (immediate) fetchData();
  }, [fetchData, immediate]);

  return { data, loading, error, refetch };
}

export function usePost(url) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const post = useCallback(async (payload) => {
    setLoading(true);
    setError(null);
    try {
      const response = await API.post(url, payload);
      return { success: true, data: response.data?.data || response.data };
    } catch (err) {
      const msg = err.response?.data?.error || err.message || 'Failed to submit';
      setError(msg);
      return { success: false, error: msg };
    } finally {
      setLoading(false);
    }
  }, [url]);

  return { post, loading, error };
}

export function useDelete(url) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const remove = useCallback(async (id) => {
    setLoading(true);
    setError(null);
    try {
      await API.delete(`${url}/${id}`);
      return { success: true };
    } catch (err) {
      const msg = err.response?.data?.error || err.message || 'Failed to delete';
      setError(msg);
      return { success: false, error: msg };
    } finally {
      setLoading(false);
    }
  }, [url]);

  return { remove, loading, error };
}

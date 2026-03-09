import { useState, useEffect } from "react";
import apiService from "../services/api.service";

/**
 * Custom hook for managing user history
 */
export const useHistory = (autoFetch = false) => {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.getHistory();
      setHistory(data.history || []);
    } catch (err) {
      setError(err.message || "Failed to fetch history");
    } finally {
      setLoading(false);
    }
  };

  const deleteItem = async (id) => {
    try {
      await apiService.deleteHistory(id);
      setHistory((prev) => prev.filter((item) => item._id !== id));
      return true;
    } catch (err) {
      setError(err.message || "Failed to delete item");
      return false;
    }
  };

  const clearHistory = () => {
    setHistory([]);
  };

  useEffect(() => {
    if (autoFetch) {
      fetchHistory();
    }
  }, [autoFetch]);

  return {
    history,
    loading,
    error,
    fetchHistory,
    deleteItem,
    clearHistory,
  };
};

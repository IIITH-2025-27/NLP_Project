import { useState } from "react";
import apiService from "../services/api.service";

/**
 * Custom hook for analysis (emotion detection → lyrics generation)
 * Supports both text and image inputs
 */
export const useAnalysis = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const analyze = async (text) => {
    if (!text || !text.trim()) {
      setError("Please enter some text");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await apiService.analyze(text);
      setResult(data);
      return data;
    } catch (err) {
      setError(err.message || "Failed to analyze text");
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const analyzeImage = async (imageFile) => {
    if (!imageFile) {
      setError("Please select an image");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await apiService.analyzeImage(imageFile);
      setResult(data);
      return data;
    } catch (err) {
      setError(err.message || "Failed to analyze image");
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setResult(null);
    setError(null);
    setLoading(false);
  };

  return {
    analyze,
    analyzeImage,
    loading,
    result,
    error,
    reset,
  };
};

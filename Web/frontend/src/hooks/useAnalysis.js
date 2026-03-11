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
      // Step 1: Get emotion from text
      const emotionData = await apiService.getEmotionFromText(text);
      
      // Step 2: Get lyrics for the detected emotion
      const lyricsData = await apiService.getLyricsForEmotion(
        emotionData.emotion_detection.emotion
      );
      
      // Combine the results in the format expected by the frontend
      const combinedResult = {
        input_text: emotionData.input_text,
        input_type: emotionData.input_type,
        emotion_detection: emotionData.emotion_detection,
        lyric_generation: lyricsData.lyric_generation,
      };
      
      setResult(combinedResult);
      return combinedResult;
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
      // Step 1: Get emotion from image
      const emotionData = await apiService.getEmotionFromImage(imageFile);
      
      // Step 2: Get lyrics for the detected emotion
      const lyricsData = await apiService.getLyricsForEmotion(
        emotionData.emotion_detection.emotion
      );
      
      // Combine the results in the format expected by the frontend
      const combinedResult = {
        input_type: emotionData.input_type,
        input_filename: emotionData.input_filename,
        emotion_detection: emotionData.emotion_detection,
        lyric_generation: lyricsData.lyric_generation,
      };
      
      setResult(combinedResult);
      return combinedResult;
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

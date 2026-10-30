import { useState, useRef } from "react";
import apiService from "../services/api.service";

// Free-tier servers sleep when idle; after this long we tell the user why it's slow.
const SLOW_NOTICE_MS = 8000;

const STAGE_TEXT = {
  "emotion-text": "Detecting emotion...",
  "emotion-image": "Detecting face and emotion...",
  lyrics: "Writing and scoring lyrics...",
};

/**
 * Custom hook for analysis (emotion detection → lyrics generation)
 * Supports both text and image inputs
 */
export const useAnalysis = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [stage, setStage] = useState(null); // key of STAGE_TEXT while loading
  const [slow, setSlow] = useState(false);
  const slowTimerRef = useRef(null);

  const startLoading = (firstStage) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setStage(firstStage);
    setSlow(false);
    clearTimeout(slowTimerRef.current);
    slowTimerRef.current = setTimeout(() => setSlow(true), SLOW_NOTICE_MS);
  };

  const stopLoading = () => {
    clearTimeout(slowTimerRef.current);
    setLoading(false);
    setStage(null);
    setSlow(false);
  };

  const analyze = async (text) => {
    if (!text || !text.trim()) {
      setError("Please enter some text");
      return;
    }

    startLoading("emotion-text");

    try {
      // Step 1: Get emotion from text
      const emotionData = await apiService.getEmotionFromText(text);

      // Step 2: Get lyrics for the detected emotion
      setStage("lyrics");
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
      stopLoading();
    }
  };

  const analyzeImage = async (imageFile) => {
    if (!imageFile) {
      setError("Please select an image");
      return;
    }

    startLoading("emotion-image");

    try {
      // Step 1: Get emotion from image
      const emotionData = await apiService.getEmotionFromImage(imageFile);

      // Step 2: Get lyrics for the detected emotion
      setStage("lyrics");
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
      stopLoading();
    }
  };

  const reset = () => {
    setResult(null);
    setError(null);
    stopLoading();
  };

  return {
    analyze,
    analyzeImage,
    loading,
    result,
    error,
    reset,
    progressText: stage ? STAGE_TEXT[stage] : null,
    slow,
  };
};

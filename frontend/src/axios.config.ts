import axios, { type AxiosError, type AxiosResponse } from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    if (error.response) {
      const message =
        (error.response.data as { detail?: string; message?: string })
          ?.detail ||
        (error.response.data as { detail?: string; message?: string })
          ?.message ||
        error.message;
      const status = error.response.status;
      return Promise.reject(new Error(`API Error (${status}): ${message}`));
    }
    if (error.request) {
      return Promise.reject(
        new Error("Network error: No response from server")
      );
    }
    return Promise.reject(error);
  }
);

const FALLBACK_API_BASE_URL = "http://localhost:8000";

const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL as string | undefined;

export const apiClient = {
  baseUrl: configuredBaseUrl?.trim() || FALLBACK_API_BASE_URL,
};

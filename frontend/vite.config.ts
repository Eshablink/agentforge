import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  // The API client uses same-origin by default. Production cross-origin URLs
  // are checked in the browser at startup; proxy /health and API paths when
  // no explicit VITE_API_BASE_URL is provided.
  const api = (process.env.VITE_API_BASE_URL || "").trim();
  if (mode === "production" && api && !api.startsWith("https://")) {
    throw new Error("Production VITE_API_BASE_URL must be HTTPS; omit it for same-origin proxying");
  }
  return { plugins: [react()], server: { host: "0.0.0.0", port: 5173 } };
});

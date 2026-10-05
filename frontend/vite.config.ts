import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(({ mode }) => {
  const api = (loadEnv(mode, ".", "VITE_").VITE_API_BASE_URL || "").trim();
  if (mode === "production" && api && !api.startsWith("https://")) {
    throw new Error("Production VITE_API_BASE_URL must be HTTPS; omit it for same-origin proxying");
  }
  return { plugins: [react()], server: { host: "0.0.0.0", port: 5173 } };
});

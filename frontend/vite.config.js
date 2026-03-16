import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Proxy REST calls to FastAPI backend in dev
      "/audit": "http://localhost:8000",
      "/health": "http://localhost:8000",
      // WebSocket proxy
      "/ws": {
        target: "ws://localhost:8000",
        ws: true,
      },
    },
  },
});
import path from "path";
import react from "@vitejs/plugin-react";
import svgr from "vite-plugin-svgr";
import basicSsl from "@vitejs/plugin-basic-ssl";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [svgr(), react(), basicSsl()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  optimizeDeps: {
    exclude: ["@capacitor/app"],
  },
  server: {
    host: true, // expose on local network so other devices can connect
    // Proxy OTLP traces to Jaeger so the browser doesn't hit CORS.
    // When frontend runs in Docker, set OTEL_PROXY_TARGET=http://host.docker.internal:4318 so the container can reach Jaeger on the host.
    proxy: {
      "/otel": {
        target: process.env.OTEL_PROXY_TARGET || "http://localhost:4318",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/otel/, ""),
      },
    },
  },
});

import "dotenv/config";
import { defineConfig } from "orval";

export default defineConfig({
  api: {
    input: {
      target: `${process.env.VITE_API_URL}/openapi.json`,
    },
    output: {
      mode: "tags-split",

      // IMPORTANT:
      // Since this config lives in src/config/,
      // paths must be relative to that directory.
      target: "../hooks",
      schemas: "../types",

      client: "react-query",
      override: {
        mutator: {
          path: "./axios.config.ts",
          name: "apiClient",
        },
      },
    },
  },
});

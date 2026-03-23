export const config = {
  apiUrl: import.meta.env.VITE_API_URL,

  development: {
    bypassAuth: import.meta.env.VITE_ENVIRONMENT === "development",
    devTokenKey: "dev-token",
  },

  observability: {
    otelExporterOtlpEndpoint:
      import.meta.env.VITE_OTEL_EXPORTER_OTLP_ENDPOINT ?? undefined,
  },
} as const;

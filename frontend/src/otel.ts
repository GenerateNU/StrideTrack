/**
 * OpenTelemetry browser tracing. Only runs when VITE_OTEL_EXPORTER_OTLP_ENDPOINT is set.
 * Traces fetch/XHR (including axios) and sends them to Jaeger or another OTLP endpoint.
 */
const endpoint = import.meta.env.VITE_OTEL_EXPORTER_OTLP_ENDPOINT as
  | string
  | undefined;

if (endpoint?.trim()) {
  const url =
    endpoint.trim().replace(/\/$/, "") +
    (endpoint.includes("/v1/traces") ? "" : "/v1/traces");

  const { BatchSpanProcessor, WebTracerProvider } =
    await import("@opentelemetry/sdk-trace-web");
  const { OTLPTraceExporter } =
    await import("@opentelemetry/exporter-trace-otlp-http");
  const { registerInstrumentations } =
    await import("@opentelemetry/instrumentation");
  const { FetchInstrumentation } =
    await import("@opentelemetry/instrumentation-fetch");
  const { XMLHttpRequestInstrumentation } =
    await import("@opentelemetry/instrumentation-xml-http-request");
  const { Resource } = await import("@opentelemetry/resources");

  const resource = new Resource({
    "service.name": "stridetrack-frontend",
    "service.namespace": "stridetrack",
    "service.version": "0.1.0",
  });

  const provider = new WebTracerProvider({
    resource,
    spanProcessors: [
      new BatchSpanProcessor(
        new OTLPTraceExporter({
          url,
          headers: {},
        })
      ),
    ],
  });

  provider.register();

  registerInstrumentations({
    instrumentations: [
      new FetchInstrumentation({
        propagateTraceHeaderCorsUrls: [/localhost/, /127\.0\.0\.1/],
        clearTimingResources: true,
      }),
      new XMLHttpRequestInstrumentation({
        propagateTraceHeaderCorsUrls: [/localhost/, /127\.0\.0\.1/],
      }),
    ],
  });
}

import { config } from "./config";

const endpoint = config.observability.otelExporterOtlpEndpoint;

if (endpoint && endpoint.trim()) {
  const base = endpoint.trim().replace(/\/$/, "");
  const url = base.includes("/v1/traces") ? base : `${base}/v1/traces`;

  const { BatchSpanProcessor, WebTracerProvider } = await import(
    "@opentelemetry/sdk-trace-web"
  );
  const { OTLPTraceExporter } = await import(
    "@opentelemetry/exporter-trace-otlp-http"
  );
  const { registerInstrumentations } = await import(
    "@opentelemetry/instrumentation"
  );
  const { FetchInstrumentation } = await import(
    "@opentelemetry/instrumentation-fetch"
  );
  const { XMLHttpRequestInstrumentation } = await import(
    "@opentelemetry/instrumentation-xml-http-request"
  );
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
        }),
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


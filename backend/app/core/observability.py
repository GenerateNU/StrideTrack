import json
import logging
import sys
from typing import Any

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.core.config import settings

# To add custom context to spans:
# from opentelemetry import trace
# current_span = trace.get_current_span()
# current_span.set_attribute("user_id", user_id)
# current_span.set_attribute("tenant_id", tenant_id)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "otelTraceID"):
            log_obj["trace_id"] = record.otelTraceID
        if hasattr(record, "otelSpanID"):
            log_obj["span_id"] = record.otelSpanID
        return json.dumps(log_obj)


def setup_observability() -> tuple[
    type[FastAPIInstrumentor], type[HTTPXClientInstrumentor]
]:
    """Configure OpenTelemetry + logging together.

    Returns:
        Tuple of (FastAPIInstrumentor, HTTPXInstrumentor) to instrument app in main.py
    """

    if settings.otel_endpoint:
        resource = Resource.create(
            {
                "service.name": settings.app_name,
                "service.version": "0.1.0",
                "deployment.environment": settings.environment,
            }
        )

        # Setup tracing
        trace_provider = TracerProvider(resource=resource)
        trace_provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.otel_endpoint))
        )
        trace.set_tracer_provider(trace_provider)

        # Setup metrics
        metric_reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=settings.otel_endpoint)
        )
        meter_provider = MeterProvider(
            resource=resource, metric_readers=[metric_reader]
        )
        metrics.set_meter_provider(meter_provider)

        # Setup log correlation (automatically injects trace_id/span_id)
        LoggingInstrumentor().instrument(set_logging_format=True)

        # Instrument HTTPX (for Supabase SDK calls)
        HTTPXClientInstrumentor().instrument()

    # Configure standard logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)

    handler = logging.StreamHandler(sys.stdout)

    if settings.environment == "development":
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        )
    else:
        formatter = JsonFormatter()

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return FastAPIInstrumentor, HTTPXClientInstrumentor

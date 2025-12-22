import json
import logging
import sys
from contextvars import ContextVar
from typing import Any
from uuid import UUID

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.core.config import settings

# brand_context: ContextVar[int | None] = ContextVar("brand_id", default=None)
# analysis_context: ContextVar[UUID | None] = ContextVar("analysis_id", default=None)


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        # record.brand_id = brand_context.get()
        # record.analysis_id = analysis_context.get()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            # "brand_id": record.brand_id,
            # "analysis_id": str(record.analysis_id) if record.analysis_id else None,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "otelTraceID"):
            log_obj["trace_id"] = record.otelTraceID
        if hasattr(record, "otelSpanID"):
            log_obj["span_id"] = record.otelSpanID
        return json.dumps(log_obj)


def setup_observability() -> None:
    """Configure OpenTelemetry + logging together."""

    if settings.otel_endpoint:
        resource = Resource.create(
            {
                "service.name": settings.app_name,
                "service.version": "0.1.0",
                "deployment.environment": "dev" if settings.debug else "prod",
            }
        )

        trace_provider = TracerProvider(resource=resource)
        trace_provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=settings.otel_endpoint))
        )
        trace.set_tracer_provider(trace_provider)

        metric_reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=settings.otel_endpoint)
        )
        meter_provider = MeterProvider(
            resource=resource, metric_readers=[metric_reader]
        )
        metrics.set_meter_provider(meter_provider)

        LoggingInstrumentor().instrument(set_logging_format=True)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if settings.debug else logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(ContextFilter())

    if settings.debug:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
        )
    else:
        formatter = JsonFormatter()

    handler.setFormatter(formatter)
    logger.addHandler(handler)

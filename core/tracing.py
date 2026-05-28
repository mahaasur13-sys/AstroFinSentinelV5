"""core/tracing.py -- OpenTelemetry setup for distributed tracing."""
import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.aiohttp import AioHttpInstrumentor

tracer = None


def setup_tracing():
    global tracer
    service_name = os.getenv("OTEL_SERVICE_NAME", "astrofin-sentinel")
    resource = Resource(attributes={SERVICE_NAME: service_name})
    provider = TracerProvider(resource=resource)
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer(__name__)
    AioHttpInstrumentor().instrument()
    return tracer


def get_tracer():
    global tracer
    if tracer is None:
        tracer = setup_tracing()
    return tracer
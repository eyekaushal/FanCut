"""Tracing for every agent call, via Microsoft Agent Framework's OpenTelemetry support.

Each Narrator, Fact Checker and Profile Compiler call becomes a span named after its agent.
Locally the spans can be printed to the console; in Azure they go to Application Insights.
"""

from agent_framework.observability import configure_otel_providers, enable_instrumentation

from fancut.config import Settings


def setup_tracing(settings: Settings) -> None:
    if settings.trace_console:
        configure_otel_providers(service_name="fancut", enable_console_exporters=True)
    else:
        enable_instrumentation()

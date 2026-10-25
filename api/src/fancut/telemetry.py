"""Tracing for every agent call, via Microsoft Agent Framework's OpenTelemetry support.

Each Narrator, Fact Checker and Profile Compiler call becomes a span named after its agent.
In Azure the spans, logs and metrics go to Application Insights (the connection string
comes from the environment, as Azure Monitor expects); locally they can be printed to
the console, or dropped.
"""

import logging
import os

from agent_framework.observability import configure_otel_providers, enable_instrumentation

from fancut.config import Settings

APP_INSIGHTS_ENV = "APPLICATIONINSIGHTS_CONNECTION_STRING"
log = logging.getLogger(__name__)


def setup_tracing(settings: Settings) -> None:
    connection_string = os.environ.get(APP_INSIGHTS_ENV)
    if connection_string:
        from azure.monitor.opentelemetry import configure_azure_monitor

        configure_azure_monitor(connection_string=connection_string, logger_name="fancut")
        enable_instrumentation()
        log.info("telemetry: Application Insights")
    elif settings.trace_console:
        configure_otel_providers(service_name="fancut", enable_console_exporters=True)
    else:
        enable_instrumentation()

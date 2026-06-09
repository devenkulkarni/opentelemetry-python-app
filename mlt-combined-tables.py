## Tracing related libraries
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter


## Metrics related libraries
from opentelemetry.metrics import get_meter_provider, set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter


## Python - Logging libraries

import logging
import json, time
from datetime import datetime

## opentelemetry logging libraries

from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter

class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": datetime.now().isoformat(),
            "level": record.levelname,
            "message": record.getMessage()
        })
    
logger = logging.getLogger("table-app")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())

logger.addHandler(handler)


## tracing code block:

resource = Resource.create({
    "service.name": "multiplication-table-app"
})

provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(ConsoleSpanExporter())

otlp_exporter = OTLPSpanExporter(
    endpoint = "http://localhost:4318/v1/traces"
)

processor2 = BatchSpanProcessor(otlp_exporter)


provider.add_span_processor(processor)
provider.add_span_processor(processor2)


log_exporter = OTLPLogExporter(
    endpoint="http://localhost:4318/v1/logs"
)

logger_provider = LoggerProvider(
    resource=resource
)

logger_provider.add_log_record_processor(
    BatchLogRecordProcessor(log_exporter)
)

otel_handler = LoggingHandler(
    level=logging.INFO,
    logger_provider=logger_provider
)

logger = logging.getLogger("table-app")
logger.setLevel(logging.INFO)
logger.addHandler(otel_handler)

# Sets the global default tracer provider
trace.set_tracer_provider(provider)

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer("table-tracer")


## metrics code block:

metric_exporter = OTLPMetricExporter(
    endpoint="http://localhost:4318/v1/metrics"
)

metric_reader = PeriodicExportingMetricReader(
    metric_exporter,
    export_interval_millis=5000
)

meter_provider = MeterProvider(
    resource=resource,
    metric_readers=[metric_reader]
)

set_meter_provider(meter_provider)

meter = get_meter_provider().get_meter("table-meter")

# Create the metrics needed for the main code:

tables_generated = meter.create_counter(
    name="tables_generated",
    description="Number of multiplication tables generated"
)

table_errors = meter.create_counter(
    name="table_errors",
    description="Number of table generation errors"
)



## Main code
number = [ 2, 5 , "ten"]

logger.info("Application started....")
with tracer.start_as_current_span("Generate Table") as parent_span: 
    try:
        print("Hello, This is a Table generation python app!")
        for num in number:
            time.sleep(1)
            logger.info(f"Generating table for {num}")
            with tracer.start_as_current_span(f"Generate Table for {num}") as child_span: 
                child_span.set_attribute("table.number",int(num))
                tables_generated.add(1,{"table_number": str(num)})
                for i in range(1, 11):
                   print(f"{num} x {i} = {num * i}")
    except ValueError as e:
        logger.error(f"Invalid table value: {num}")
        table_errors.add(1,{"error_type": type(e).__name__})
        raise
    finally:
        provider.shutdown()
        meter_provider.shutdown()
        logger_provider.shutdown()

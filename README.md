# Running the Demo

## Start Grafana LGTM

```bash
docker run -d \
  --name lgtm \
  -p 3000:3000 \
  -p 4320:4318 \
  grafana/otel-lgtm:latest
```

This starts:

* Grafana
* Loki
* Prometheus
* Tempo

Grafana UI:

```text
http://localhost:3000
```

---

## Start OpenTelemetry Collector

```bash
docker run -d \
  --name otel-collector \
  -p 4317:4317 \
  -p 4318:4318 \
  -v $(pwd)/otel-collector.yaml:/etc/otelcol/config.yaml \
  otel/opentelemetry-collector-contrib:latest \
  --config=/etc/otelcol/config.yaml
```

Verify the Collector is running:

```bash
docker logs -f otel-collector
```

---

## Run the Python Application

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python mlt-combined-tables.py
```

---

## Observing Telemetry

Open Grafana:

```text
http://localhost:3000
```

### Logs

Navigate to:

```text
Explore → Loki
```

Search for:

```text
service_name="multiplication-table-app"
```

### Metrics

Navigate to:

```text
Explore → Prometheus
```

Query:

```promql
tables_generated_total
```

or

```promql
table_errors_total
```

### Traces

Navigate to:

```text
Explore → Tempo
```

Search using:

```text
service.name=multiplication-table-app
```

You should see the parent span:

```text
Generate Table
```

and its child spans:

```text
Generate Table for 2
Generate Table for 5
Generate Table for ten
```

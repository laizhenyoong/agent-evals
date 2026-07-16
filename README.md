# Agent Eval Lab

## Stage 2: Phoenix tracing

Phoenix runs locally as the trace collector and UI. Strands emits the agent,
model, and tool spans through OpenTelemetry; no separate Phoenix instrumentor is
used.

Install the project dependencies:

```sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

In one terminal, start Phoenix with its data stored in the project directory:

```sh
PHOENIX_WORKING_DIR="$PWD/.phoenix" phoenix serve
```

In a second terminal, run the sample trajectories:

```sh
python support_agent.py
```

Open http://localhost:6006 and select the `customer-support-agent` project.
Each query is one trace, with nested model and tool-call spans.

### Optional configuration

These defaults work when Phoenix runs locally. Override them when the collector
runs elsewhere:

```sh
export PHOENIX_COLLECTOR_ENDPOINT="http://localhost:6006"
export PHOENIX_PROJECT_NAME="customer-support-agent"
```

Tracing intentionally records the fake account IDs and support requests in this
demo. Redact customer data before using this configuration with real traffic.

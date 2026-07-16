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

## Agent evaluation suite

The evaluation suite contains 50 hand-curated customer requests in
[`evaluation/golden_dataset.py`](evaluation/golden_dataset.py). Every case specifies the observable
contract: required tool calls and arguments, forbidden calls, a maximum tool
budget, an efficient preferred order, and response facts/tone for qualitative
grading.

Run deterministic and trajectory scoring against the live local agent:

```sh
.venv/bin/python -m evaluation.runner
```

This prints a JSON report and exits non-zero when either the deterministic or
trajectory pass rate is below 100%, which is intentionally ready for the Stage
4 CI gate. To write a report file or run one case while iterating:

```sh
.venv/bin/python -m evaluation.runner --case kb_refund_policy --output eval-report.json
```

The answer-quality judge is intentionally opt-in: it calls your local Ollama
server and grades factual correctness, faithfulness to the supplied reference
facts, and tone. This keeps offline scorer tests repeatable and makes the
model-based judgement explicit.

```sh
.venv/bin/python -m evaluation.runner --judge ollama
```

Set `OLLAMA_HOST` or `EVAL_JUDGE_MODEL` to override its defaults. Run the
offline scorer tests with:

```sh
.venv/bin/python -m unittest discover -s tests -v
```

### Optional configuration

These defaults work when Phoenix runs locally. Override them when the collector
runs elsewhere:

```sh
export PHOENIX_COLLECTOR_ENDPOINT="http://localhost:6006"
export PHOENIX_PROJECT_NAME="customer-support-agent"
```

Tracing intentionally records the fake account IDs and support requests in this
demo. Redact customer data before using this configuration with real traffic.

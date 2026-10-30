# JEV decision routing: safe pilot

Maliky has an optional, real TypeSafe **JEV System One HTTP client** behind its existing `scripts/decision_engine.py` interface.

**Status:** Implemented and tested with mocked API responses. A paid live API evaluation has **not** run, because this repository and GitHub Actions do not contain your private API key.

## Design boundaries

- **Nothing changes in your source-evidence registry, inspection workflow, source provenance, or public/private separation.** No model decision can create a verified asset, determine license suitability, or write an external source into the owned registry.
- Existing calls to `DecisionEngine.decide(...)` do **not** invoke TypeSafe. They still produce a deferred record.
- API calls require *all* of these: an explicit `allow_remote=True` argument, an explicit `safe_for_external=True` declaration by the caller, `JEV_ENABLE=1`, and a secret `TYPESAFE_API_KEY` in the runtime.
- JEV receives only the specific caller-approved bounded state. Never mark private source, user data, internal repository IDs, secrets, original prompts, or confidential evidence as safe.
- Returned results are **non-authoritative** suggestions: `SUGGESTION`, `ESCALATE`, or `DEFERRED`. Even a high-confidence model recommendation does not raise source review status.
- Choices are accepted only at **0.85 confidence** and **0.10 probability separation** in the initial *research* policy. These are starting guardrails, **not scientifically calibrated thresholds**.
- The client validates question schemas, response types and choice distributions, uses a hard limit on request/response size, and never prints raw API failures, secrets, or evidence packets.
- The pilot is capped at four API requests and uses an **allowlisted set of publicly documented external candidates**. A missing external index does not impair ordinary Maliky searches.

## Get started (no API key needed)

Offline preview (retrieves only the public Every-Awesome-Repo index; can instead use a downloaded JSON file):

```bash
python scripts/jev_pilot.py
python scripts/jev_pilot.py --catalog /path/to/public-tools.json
```

This preview does **not** make paid model calls. It displays the chosen evidence cases and an evaluation plan.

## Test with your API key (you perform this locally or via secured infrastructure)

Get your TypeSafe API key from the [TypeSafe console](https://console.typesafe.ai/) and set it in your local environment. **Do not share the key in chat, commit it, or paste it into a GitHub issue.**

macOS/Linux:

```bash
export TYPESAFE_API_KEY="your-secret-key"
export JEV_ENABLE=1
python scripts/jev_pilot.py --live --limit 4
```

Windows PowerShell:

```powershell
$env:TYPESAFE_API_KEY = "your-secret-key"
$env:JEV_ENABLE = "1"
python scripts/jev_pilot.py --live --limit 4
```

The pilot will report the number of accepted decisions, correctness against **illustrative manually assigned categories** among accepted decisions, abstentions/errors, input tokens when provided, and total wall time. No raw private Maliky data is in this pilot.

To apply the client behind `DecisionEngine` in a later controlled review workflow, a caller must independently confirm `safe_for_external=True` for a **public, minimized** evidence packet:

```python
from decision_engine import DecisionEngine

record = DecisionEngine().decide(
    "repository:public-demo",
    "ENTITY_TYPE",
    ["KEEP", "ESCALATE_FOR_REVIEW"],
    {"public_evidence": "Pinned public declaration and README summary"},
    allow_remote=True,
    safe_for_external=True,
)
# This is a routing recommendation, never a verified source fact.
```

With JEV disabled, that call is deferred and never sent externally.

## Evaluation before wider deployment

The four-case pilot validates the transport and output format but **cannot establish production accuracy**. Before running across the full external tool library:

1. Create at least 50–100 genuinely labeled public candidate records across major data, agent, UI, MCP, automation and ambiguous categories, including negative examples.
2. Compare JEV against deterministic metadata/category rules and a stronger model using the same fixed dataset.
3. Report precision/recall, false-negative escalation, abstention rate, latency, token usage and **cost per correctly handled item**, with holdout cases.
4. Calibrate confidence and margin thresholds on the results. Do not assume JEV probabilities are calibrated for these tasks until verified.
5. Use bounded queueing and caching; implement per-day cost caps and explicit review of consequential decisions.
6. For repository security, licensing, identity, finance and other high-stakes decisions, route to deterministic validation plus human review.

## System details

Official wire format: `POST https://api.typesafe.ai/v1/systemone`, with `model`, `state`, and typed `questions`. The implementation uses Python's standard library to avoid introducing an SDK dependency. A later SDK migration is optional.

Reference: [TypeSafe Quick Start](https://docs.typesafe.ai/introduction/quickstart), [TypeSafe API Reference](https://docs.typesafe.ai/api/system-one).

## Testing

```bash
python -m unittest discover -s tests -p "test_jev_client.py" -v
python -m unittest discover -s tests -v
```

CI never enables `JEV_ENABLE` and never asks GitHub to access a paid API credential. Live evaluation is a separate deliberate operation.

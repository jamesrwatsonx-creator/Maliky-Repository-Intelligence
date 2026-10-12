# Read-only capability catalog for external agents

Run from a checkout of `recovery/v1-rebuild`. Python's standard library is sufficient.
Hermes or another coding agent can register these commands as read-only shell tools.
They return JSON to stdout and use the existing registry, index and composition function.
They do not ingest sources, execute catalogued code, change files or require API keys.

```sh
python scripts/catalog_agent.py search "voice" --limit 5
python scripts/catalog_agent.py search --repository voicebox
python scripts/catalog_agent.py search --category operational:07 --kind SKILL
python scripts/catalog_agent.py search "browser" --verified
python scripts/catalog_agent.py compose idea:voice-websites
python scripts/catalog_agent.py compose --capability capability:queued-speech-generation-submission
python scripts/catalog_agent.py plan --requirement "voice cloning" --requirement "appointment booking" --limit 3
```

Search text covers capability and purpose. Repository, category and kind are filters.
Category IDs come from `registry/taxonomy/categories.json` and `operational.json`.
`schema_version: 1` wraps each JSON response. Invalid arguments exit nonzero.
`catalog_status` separates VERIFIED assets, CANDIDATE assets and REPOSITORY_METADATA.
Repository discoverability does not imply source inspection or runtime readiness.

The requirements planner returns linked verified leads, candidates, exact capability
matches, the existing verified-provider composition, explicit gaps and an MVP plan.
Only exact reviewed capability names/aliases enter composition automatically; lexical
matches do not prove feature coverage. A gap means absent reviewed evidence, not proof
that no owned repository implements it. Dependencies and licenses need integration review.

By default this interface reads only the public canonical registry. Private metadata stays
in ignored `.local/private-catalog.json`. Authorized local agents may explicitly use
`search --private-local`; access follows the checkout's OS permissions, with no hosted
authentication service. Do not publish private search results. Public-only clones do not
contain this file; transfer it only through a separately authorized private channel.
Private metadata remains candidate evidence and never enters public composition.
No hosted endpoint is necessary for V1. To use from a VPS, sync this branch to an
authorized local checkout and expose only these commands to the agent.

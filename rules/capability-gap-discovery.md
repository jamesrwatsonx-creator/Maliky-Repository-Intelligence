# Capability Gap and GitHub Discovery Policy

Use capability gaps to guide external discovery. Do not browse broadly before checking what the user already owns.

```text
APP / WORKFLOW IDEA
|
v
FEATURE DECOMPOSITION
|
v
CAPABILITY REQUIREMENTS
|
v
SEARCH OWNED REGISTRY
|
v
SMALLEST STRONG OWNED COMPOSITION
|
v
COVERED / PARTIALLY_COVERED / MISSING
|
v
SEARCH GITHUB ONLY FOR GAPS
|
v
LIGHTWEIGHT EXTERNAL EVALUATION
|
v
EXTERNAL_CANDIDATE
|
v
OPTIONAL USER FORK / IMPORT
|
v
NORMAL INGESTION
```

## Owned coverage first

Decompose the requested app or workflow into features, then into capability requirements. Search the canonical registry and capability graph for the smallest strong combination of owned assets. Classify each required capability as:

- `COVERED`: owned assets provide a credible composition;
- `PARTIALLY_COVERED`: owned assets help but leave a material weakness;
- `MISSING`: no owned asset provides the required capability adequately.

Record why the proposed owned composition is sufficient or where it falls short. Similar assets may be alternatives or complements; do not combine more assets than the requirement needs.

## Targeted GitHub discovery

Search GitHub only for `MISSING` capabilities or material weaknesses in `PARTIALLY_COVERED` capabilities. Form queries from the precise capability, needed ecosystem, and relevant constraints rather than from the entire app idea.

Evaluate an external result initially only for:

1. capability fit;
2. maintenance and recent activity;
3. license;
4. language and framework;
5. dependencies;
6. integration effort;
7. overlap with owned assets;
8. important risks.

An acceptable result becomes an `EXTERNAL_CANDIDATE`. This means it is a possible gap filler; it is not an owned or canonical asset. Preserve its external provenance and keep it separate from owned inventory.

Only after the user chooses to fork or import a candidate may it enter the normal Repository Intelligence ingestion process. Discovery evidence does not skip source retrieval, provenance, inspection, entity extraction, semantic review, validation, or publication safeguards.

## Scope

This policy defines future search and evaluation behavior. It does not authorize building a GitHub crawler, the final application, a vector database, or a parallel registry. Implement discovery incrementally when a real capability gap requires it, and preserve the canonical architecture and inspection state.

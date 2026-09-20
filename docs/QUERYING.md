# Querying and composition

```sh
python scripts/query_registry.py "browser" --limit 10
python scripts/query_registry.py "review" --kind SKILL
python scripts/query_registry.py "UI screenshot inspection" --verified
python scripts/compose_idea.py idea:voice-websites
```

Results include type, exact path, inspected commit, repository and review status.
Search is lexical with canonical capability alias expansion. An entity candidate
is discoverable, but is not a verified implementation recommendation.
Add atomic capability records with synonyms, evidence and explicit provider IDs;
add the matching capability reference to each verified provider entity.
Use the same capability IDs as Idea requirements. Empty requirements produce an
explicit empty-requirements result, not a completed product composition.

Composition considers only verified entities at their repository's active commit.
Capabilities must also be VERIFIED. It separates selected providers, alternatives
and missing evidence. Dependencies and compatibility require explicit review.
The normalized JSONL index can support a future OpenRouter interface without
scanning source records at query time. No hosted AI credentials are needed today.

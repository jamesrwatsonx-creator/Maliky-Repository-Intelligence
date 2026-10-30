"""Small, standard-library TypeSafe JEV client for narrow, optional judgments.

This is the official HTTPS /v1/systemone wire format. It is intentionally not
an evidence extractor, source verifier, security authority, or dependency.
No network call occurs without an API key and an explicit caller action.
"""
from __future__ import annotations

import json
import math
import os
import re
import urllib.error
import urllib.request

ENDPOINT = "https://api.typesafe.ai/v1/systemone"
MAX_REQUEST_BYTES = 16_384
MAX_RESPONSE_BYTES = 32_768
MAX_QUESTIONS = 4
MAX_CHOICES = 12


class JevError(ValueError):
    """JEV unavailable, malformed response, or input outside its narrow contract."""


def _prob(value: object) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 1


def validate_questions(questions: dict) -> None:
    if not isinstance(questions, dict) or not 1 <= len(questions) <= MAX_QUESTIONS:
        raise JevError("Expected one to four typed questions")
    for key, question in questions.items():
        if not isinstance(key, str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,39}", key):
            raise JevError("Invalid question identifier")
        if not isinstance(question, dict) or question.get("type") not in {"choice", "score", "noul"}:
            raise JevError("Unsupported question type")
        if not isinstance(question.get("instructions"), str) or not 8 <= len(question["instructions"]) <= 700:
            raise JevError("Question instructions must be 8–700 characters")
        criteria = question.get("criteria")
        if question["type"] == "choice":
            if not isinstance(criteria, dict) or not 2 <= len(criteria) <= MAX_CHOICES:
                raise JevError("Choice must have two to twelve options")
            if any(not isinstance(k, str) or not re.fullmatch(r"[a-zA-Z][a-zA-Z0-9_-]{0,63}", k)
                   or not isinstance(v, str) or not v.strip() or len(v) > 400
                   for k, v in criteria.items()):
                raise JevError("Invalid choice labels or descriptions")
        if question["type"] == "score":
            if not isinstance(criteria, list) or not 2 <= len(criteria) <= 8:
                raise JevError("Score needs a rubric of two to eight levels")
            if any(not isinstance(v, str) or not 1 <= len(v) <= 300 for v in criteria):
                raise JevError("Invalid score rubric")
        if question["type"] == "noul" and criteria is not None and (
            not isinstance(criteria, dict)
            or set(criteria) != {"true", "false"}
            or any(not isinstance(v, str) or not v for v in criteria.values())
        ):
            raise JevError("Noul criteria must have true and false descriptions")


def validate_response(payload: object, questions: dict) -> dict:
    if not isinstance(payload, dict) or not isinstance(payload.get("answers"), dict):
        raise JevError("Missing answers in model response")
    answers = payload["answers"]
    if set(answers) != set(questions):
        raise JevError("Model answer identifiers do not match the requested questions")
    for key, question in questions.items():
        ans = answers[key]
        typ = question["type"]
        if not isinstance(ans, dict) or ans.get("type") != typ:
            raise JevError("Wrong answer type from model")
        if typ == "choice":
            options = question["criteria"]
            probs = ans.get("probabilities")
            if (ans.get("choice") not in options
                or not isinstance(probs, dict) or set(probs) != set(options)
                or not all(_prob(p) for p in probs.values())
                or abs(sum(probs.values()) - 1) > 0.04
                or not _prob(ans.get("confidence"))):
                raise JevError("Invalid choice probabilities or confidence")
            if probs[ans["choice"]] < max(probs.values()) - 0.03:
                raise JevError("Choice is inconsistent with probabilities")
        elif typ == "score":
            if not _prob(ans.get("score")) or not _prob(ans.get("confidence")):
                raise JevError("Invalid score or confidence")
        else:
            if not _prob(ans.get("noul")):
                raise JevError("Invalid Noul probability")
    return payload


def system_one(state: str | dict | list, questions: dict, *,
               api_key: str | None = None, model: str = "jev-latest",
               timeout: float = 12.0) -> dict:
    """Invoke TypeSafe with one bounded request. Never logs input or credentials."""
    validate_questions(questions)
    key = api_key or os.environ.get("TYPESAFE_API_KEY")
    if not key:
        raise JevError("TYPESAFE_API_KEY is not configured")
    if not isinstance(model, str) or not re.fullmatch(r"[a-zA-Z0-9._-]{3,64}", model):
        raise JevError("Invalid model identifier")
    if isinstance(state, str) and not state.strip():
        raise JevError("Cannot evaluate an empty state")
    body = json.dumps({"model": model, "state": state, "questions": questions},
                      ensure_ascii=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    if len(body) > MAX_REQUEST_BYTES:
        raise JevError("Decision packet exceeds the request limit")
    req = urllib.request.Request(
        ENDPOINT, data=body, method="POST",
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json",
                 "Accept": "application/json", "User-Agent": "Maliky-Jev-Pilot/1.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except urllib.error.HTTPError as exc:
        # Do NOT surface response body or echo an input/credential.
        raise JevError(f"TypeSafe returned HTTP {exc.code}") from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise JevError("TypeSafe connection failed") from None
    if len(raw) > MAX_RESPONSE_BYTES:
        raise JevError("TypeSafe response is too large")
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise JevError("TypeSafe returned invalid JSON") from None
    return validate_response(parsed, questions)


def bounded_choice(state: dict, options: dict[str, str], *,
                   instructions: str, minimum_confidence: float = 0.85,
                   minimum_margin: float = 0.10,
                   api_key: str | None = None) -> dict:
    """Return a non-authoritative recommendation or an explicit escalation."""
    if not 0 <= minimum_confidence <= 1 or not 0 <= minimum_margin <= 1:
        raise JevError("Invalid confidence threshold")
    question = {"selection": {"type": "choice", "instructions": instructions,
                              "criteria": options}}
    raw = system_one(state, question, api_key=api_key)
    a = raw["answers"]["selection"]
    ordered = sorted(a["probabilities"].values(), reverse=True)
    margin = ordered[0] - ordered[1]
    accepted = a["confidence"] >= minimum_confidence and margin >= minimum_margin
    return {
        "status": "SUGGESTION" if accepted else "ESCALATE",
        "choice": a["choice"] if accepted else None,
        "candidate_choice": a["choice"],
        "confidence": a["confidence"],
        "margin": round(margin, 6),
        "model": raw.get("model", "unknown"),
        "usage": raw.get("usage", {}),
        "source": "JEV_MODEL_JUDGMENT_NOT_FACT",
    }

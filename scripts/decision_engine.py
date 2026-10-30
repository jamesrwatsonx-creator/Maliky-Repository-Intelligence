"""Optional JEV decision boundary for Maliky Repository Intelligence.

The canonical registry always relies on source evidence. This module records
only non-authoritative routing suggestions. Existing callers make ZERO network
calls. Sending even a bounded public evidence packet requires explicit
allow_remote=True, safe_for_external=True, JEV_ENABLE=1, and an API key.
"""
from __future__ import annotations

import hashlib
import os

from jev_client import JevError, bounded_choice
from registry import now, read, write


class DecisionEngine:
    def available(self):
        # Current supported integration speaks TypeSafe's HTTPS API directly;
        # it needs no optional legacy "typesafe" package.
        return bool(os.getenv("TYPESAFE_API_KEY"))

    def decide(self, repository_id, decision_type, choices, evidence, *,
               required=False, allow_remote=False, safe_for_external=False,
               minimum_confidence=0.85):
        # Preserve the legacy packet identity so existing deferred decisions
        # retain their provenance. Nothing is automatically retried or promoted.
        packet = repr((repository_id, decision_type, choices, evidence)).encode()
        packet_id = hashlib.sha256(packet).hexdigest()[:24]
        records = read("system/decision-records.json", [])
        if not isinstance(records, list):
            raise ValueError("Invalid decision-record store")
        requested = (allow_remote and safe_for_external
                     and os.getenv("JEV_ENABLE") == "1"
                     and self.available())
        prior = [r for r in records if r.get("evidence_packet_id") == packet_id]
        if requested:
            # A previous model judgment is reusable; a DEFERRED result is NOT
            # allowed to prevent a later explicitly authorized attempt.
            known = next((r for r in reversed(prior)
                          if r.get("engine") == "jev-typesafe"
                          and r.get("status") in ("SUGGESTION", "ESCALATE")), None)
            if known:
                return known
        elif prior:
            return prior[0]

        record = {
            "id": "decision:" + packet_id + (":jev" if requested else ""),
            "repository_id": repository_id,
            "decision_type": decision_type,
            "choices": list(choices),
            "evidence_packet_id": packet_id,
            "created_at": now(),
            "engine": "jev-typesafe" if requested else "deterministic-fallback",
            "status": "DEFERRED",
            "required_for_completion": bool(required),
        }
        if requested:
            try:
                # Private source contents should never be passed here. The
                # caller alone must explicitly mark the packet shareable.
                if not isinstance(evidence, dict):
                    raise JevError("Public evidence packet must be an object")
                if len(choices) < 2 or len(choices) > 12:
                    raise JevError("Invalid number of choices")
                names = list(choices)
                criteria = {
                    key: ("Send for independent human/source verification."
                          if key.upper() in {"ESCALATE", "ESCALATE_FOR_REVIEW", "NEEDS_REVIEW"}
                          else "Candidate routing label; never a verified source fact.")
                    for key in names
                }
                suggestion = bounded_choice(
                    {"decision_type": decision_type, "evidence": evidence},
                    criteria,
                    instructions=(
                        "Based only on the provided public evidence, choose the most "
                        "appropriate workflow route. If supporting evidence is missing "
                        "or uncertain, prefer a review or escalation option. Do not "
                        "invent functionality, licenses or source verification."
                    ),
                    minimum_confidence=minimum_confidence,
                )
                record.update(
                    status=suggestion["status"],
                    suggested_choice=suggestion["choice"],
                    candidate_choice=suggestion["candidate_choice"],
                    confidence=suggestion["confidence"],
                    margin=suggestion["margin"],
                    model=suggestion["model"],
                    usage=suggestion["usage"],
                    judgment_scope=suggestion["source"],
                )
            except (JevError, ValueError, TypeError) as exc:
                # Never dump exceptions containing payloads or API secrets.
                record["status"] = "DEFERRED"
                record["failure_code"] = type(exc).__name__
        records.append(record)
        write("system/decision-records.json", records)
        return record

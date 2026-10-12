"""Small, replaceable decision boundary for Repository Intelligence.

The registry remains source-evidence based.  This module only records bounded
decisions or a deferred record when the supported TypeSafe environment is absent.
"""
from __future__ import annotations

import hashlib
import importlib.util
import os
from registry import now, read, write


class DecisionEngine:
    def available(self):
        return bool(os.getenv("TYPESAFE_API_KEY")) and importlib.util.find_spec("typesafe") is not None

    def decide(self, repository_id, decision_type, choices, evidence, *, required=False):
        packet = repr((repository_id, decision_type, choices, evidence)).encode()
        packet_id = hashlib.sha256(packet).hexdigest()[:24]
        records = read("system/decision-records.json", [])
        existing = next((r for r in records if r["evidence_packet_id"] == packet_id), None)
        if existing:
            return existing
        # TypeSafe invocation is intentionally isolated until its supported SDK is
        # configured.  A missing service must never become a fabricated answer.
        record = {
            "id": "decision:" + packet_id,
            "repository_id": repository_id,
            "decision_type": decision_type,
            "choices": list(choices),
            "evidence_packet_id": packet_id,
            "created_at": now(),
            "engine": "jev-typesafe" if self.available() else "deterministic-fallback",
            "status": "DEFERRED" if not self.available() else "PENDING_IMPLEMENTATION",
            "required_for_completion": bool(required),
        }
        records.append(record)
        write("system/decision-records.json", records)
        return record

"""Offline JEV transport, privacy gates, and pilot tests. Never use a real key."""
from __future__ import annotations

import io
import json
import os
import pathlib
import sys
import tempfile
import unittest
from unittest.mock import patch
import urllib.error

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import decision_engine
import jev_client
import jev_pilot
import registry

QUESTIONS = {
    "kind": {
        "type": "choice",
        "instructions": "Categorize this software by primary function.",
        "criteria": {
            "data": "Data services and collections",
            "ui": "Visual components and interface",
        }
    },
    "quality": {
        "type": "score",
        "instructions": "How clearly does the evidence describe its function?",
        "criteria": ["unclear", "partial", "clear"],
    },
    "needs_review": {
        "type": "noul",
        "instructions": "Does this need human review?",
    },
}
RESPONSE = {
    "model": "jev-1.13",
    "usage": {"input_tokens": 123, "output_tokens": 19},
    "answers": {
        "kind": {
            "type": "choice", "choice": "data",
            "confidence": 0.92, "probabilities": {"data": 0.94, "ui": 0.06}
        },
        "quality": {
            "type": "score", "score": 0.67, "confidence": 0.80,
            "probabilities": {"0": 0.1, "1": 0.2, "2": 0.7}
        },
        "needs_review": {"type": "noul", "noul": 0.88},
    },
}


class DummyResponse(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *_): self.close()


class TestJevClient(unittest.TestCase):
    def test_wire_format_and_models_and_typed_questions(self):
        recorded = []
        def fake_open(request, timeout):
            recorded.append((request, timeout))
            return DummyResponse(json.dumps(RESPONSE).encode())
        with patch("urllib.request.urlopen", side_effect=fake_open):
            result = jev_client.system_one(
                {"public": "api catalog"}, QUESTIONS, api_key="test_key_NOT_REAL"
            )
        self.assertEqual(result["answers"]["kind"]["choice"], "data")
        self.assertEqual(len(recorded), 1)
        req, timeout = recorded[0]
        self.assertEqual(req.full_url, "https://api.typesafe.ai/v1/systemone")
        self.assertEqual(req.get_method(), "POST")
        body = json.loads(req.data)
        self.assertEqual(body["model"], "jev-latest")
        self.assertEqual(body["state"], {"public": "api catalog"})
        self.assertEqual(set(body["questions"]), {"kind", "quality", "needs_review"})

    def test_no_key_means_no_transport(self):
        with patch.dict(os.environ, {"TYPESAFE_API_KEY": ""}):
            with patch("urllib.request.urlopen", side_effect=AssertionError("network")):
                with self.assertRaises(jev_client.JevError):
                    jev_client.system_one("public input", QUESTIONS)

    def test_bad_choice_fails_closed(self):
        bad = json.loads(json.dumps(RESPONSE))
        bad["answers"]["kind"]["probabilities"] = {"data": -1, "ui": 2}
        self.assertRaises(jev_client.JevError, jev_client.validate_response, bad, QUESTIONS)

    def test_bad_choice_ids_or_mismatched_types_fail_closed(self):
        bad = json.loads(json.dumps(RESPONSE))
        bad["answers"]["unknown"] = {"type": "noul", "noul": 0.4}
        self.assertRaises(jev_client.JevError, jev_client.validate_response, bad, QUESTIONS)
        bad = json.loads(json.dumps(RESPONSE))
        bad["answers"]["needs_review"]["noul"] = 1.4
        self.assertRaises(jev_client.JevError, jev_client.validate_response, bad, QUESTIONS)

    def test_choice_routing_escalates_below_threshold(self):
        q = {"selection": {"type": "choice", "instructions": "Classify the supplied item.",
                           "criteria": {"keep": "Keep for review", "escalate": "Send to reviewer"}}}
        raw = {"answers": {"selection": {"type": "choice", "choice": "keep", "confidence": 0.65,
                                         "probabilities": {"keep": 0.51, "escalate": 0.49}}}}
        with patch.object(jev_client, "system_one", return_value=raw):
            decision = jev_client.bounded_choice({"public": "details"}, q["selection"]["criteria"],
                                                  instructions=q["selection"]["instructions"])
        self.assertEqual(decision["status"], "ESCALATE")
        self.assertIsNone(decision["choice"])

    def test_reject_overlong_packet_before_request(self):
        with patch("urllib.request.urlopen", side_effect=AssertionError("network")):
            with self.assertRaises(jev_client.JevError):
                jev_client.system_one("X" * 20_000, QUESTIONS, api_key="test")

    def test_http_error_does_not_echo_payload_or_token(self):
        def fake_open(req, timeout):
            raise urllib.error.HTTPError(req.full_url, 401, "invalid secret", None, None)
        with patch("urllib.request.urlopen", side_effect=fake_open):
            with self.assertRaises(jev_client.JevError) as cm:
                jev_client.system_one("private_secret_to_avoid_echo", QUESTIONS, api_key="test_token")
        self.assertNotIn("test_token", str(cm.exception))
        self.assertNotIn("private_secret_to_avoid_echo", str(cm.exception))
        self.assertEqual(str(cm.exception), "TypeSafe returned HTTP 401")

    def test_explicit_public_safe_gate_preserves_existing_deferred_record(self):
        old_root = registry.ROOT
        try:
            with tempfile.TemporaryDirectory() as temp:
                registry.ROOT = pathlib.Path(temp)
                engine = decision_engine.DecisionEngine()
                with patch.dict(os.environ, {"JEV_ENABLE": "1", "TYPESAFE_API_KEY": "test_key"}):
                    with patch.object(decision_engine, "bounded_choice",
                                      side_effect=AssertionError("unexpected call")):
                        deferred = engine.decide("repository:public", "ENTITY_TYPE",
                                                 ["KEEP", "ESCALATE_FOR_REVIEW"],
                                                 {"public_evidence": "README"})
                        self.assertEqual(deferred["status"], "DEFERRED")
                    suggestion = {
                        "status": "SUGGESTION", "choice": "KEEP",
                        "candidate_choice": "KEEP", "confidence": 0.97, "margin": 0.94,
                        "model": "jev-1.13", "usage": {"input_tokens": 40},
                        "source": "JEV_MODEL_JUDGMENT_NOT_FACT"
                    }
                    with patch.object(decision_engine, "bounded_choice", return_value=suggestion) as call:
                        picked = engine.decide("repository:public", "ENTITY_TYPE",
                                               ["KEEP", "ESCALATE_FOR_REVIEW"],
                                               {"public_evidence": "README"},
                                               allow_remote=True, safe_for_external=True)
                    self.assertEqual(call.call_count, 1)
                    self.assertEqual(picked["status"], "SUGGESTION")
                    self.assertEqual(len(registry.read("system/decision-records.json", [])), 2)
                    self.assertEqual(registry.read("system/decision-records.json")[0]["status"], "DEFERRED")
        finally:
            registry.ROOT = old_root

    def test_remote_requires_both_enablement_and_public_authorization(self):
        old_root = registry.ROOT
        try:
            with tempfile.TemporaryDirectory() as temp:
                registry.ROOT = pathlib.Path(temp)
                with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test_key", "JEV_ENABLE": "0"}):
                    with patch.object(decision_engine, "bounded_choice",
                                      side_effect=AssertionError("network never allowed")):
                        r = decision_engine.DecisionEngine().decide(
                            "repository:private", "ROUTE", ["KEEP", "ESCALATE"],
                            {"secret": "should_not_leave_runtime"},
                            allow_remote=True, safe_for_external=True
                        )
                    self.assertEqual(r["status"], "DEFERRED")
                with patch.dict(os.environ, {"TYPESAFE_API_KEY": "test_key", "JEV_ENABLE": "1"}):
                    with patch.object(decision_engine, "bounded_choice",
                                      side_effect=AssertionError("network never allowed")):
                        r2 = decision_engine.DecisionEngine().decide(
                            "repository:private2", "ROUTE", ["KEEP", "ESCALATE"],
                            {"secret": "not shared"}, allow_remote=True, safe_for_external=False
                        )
                    self.assertEqual(r2["status"], "DEFERRED")
        finally:
            registry.ROOT = old_root

    def test_pilot_defaults_to_offline_and_limits_paid_calls(self):
        testindex = {
            "project": "Every Awesome Repo Tools",
            "tools": [{
                "github_repository": "tidwall/tile38", "name": "Tile38",
                "description": "Geospatial database", "evidence_status": "UPSTREAM_DOCUMENTED_NOT_TESTED",
                "source_collections": [{"evidence_url": "https://github.com/example/awesome#L3"}],
                "upstream_evidence": [{"evidence_url": "https://github.com/tidwall/tile38#L16",
                                       "documented_statement": "Tile38 is a geospatial database."}]
            }]
        }
        with patch.object(jev_client, "system_one", side_effect=AssertionError("network")):
            result = jev_pilot.run(testindex)
        self.assertEqual(result["mode"], "OFFLINE_PREVIEW")
        self.assertEqual(result["accepted"], 0)
        with self.assertRaises(ValueError):
            jev_pilot.run(testindex, limit=5)

    def test_pilot_live_mock_uses_only_public_tools(self):
        entry = {
            "github_repository": "tidwall/tile38", "name": "Tile38",
            "description": "Spatial index", "evidence_status": "UPSTREAM_DOCUMENTED_NOT_TESTED",
            "source_collections": [{"evidence_url": "https://github.com/a/b"}],
            "upstream_evidence": [{"documented_statement": "A geolocation datastore."}],
            "private_metadata": "SECRET_SHOULD_NOT_BE_SENT",
        }
        payload = {"project": "Every Awesome Repo Tools", "tools": [entry]}
        capture = []
        def stub(state, questions):
            capture.append(state)
            return {
                "answers": {
                    "category": {"choice": "spatial_data", "confidence": 0.99,
                                 "probabilities": {"spatial_data": 0.97,
                                                   "market_data": 0.02, "general_data": 0.01}},
                    "relevance": {"score": 0.8},
                    "needs_review": {"noul": 0.65}
                },
                "usage": {"input_tokens": 200},
            }
        with patch.dict(os.environ, {"JEV_ENABLE": "1", "TYPESAFE_API_KEY": "test_key"}):
            result = jev_pilot.run(payload, live=True, limit=1, classifier=stub)
        self.assertEqual(result["accepted"], 1)
        self.assertTrue(result["results"][0]["correct_when_accepted"])
        self.assertNotIn("SECRET_SHOULD_NOT_BE_SENT", json.dumps(capture))

if __name__ == "__main__":
    unittest.main()

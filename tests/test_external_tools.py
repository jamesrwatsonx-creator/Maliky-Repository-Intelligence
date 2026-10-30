"""Standalone and combined external tool search: offline, untrusted-data tests."""
from __future__ import annotations
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import external_tools
import search_with_discovery

def candidates():
    return {
        "project": "Every Awesome Repo Tools",
        "schema_version": "1.0.0",
        "tools": [
            {
                "id": "tool:123456abcdef", "name": "Transit Data API",
                "url": "https://data.example/transport",
                "description": "Realtime bus arrival information",
                "topics": ["Transportation"],
                "evidence_status": "LISTED_ONLY",
                "source_collections": [{
                    "repository": "example/awesome-data",
                    "evidence_url": "https://github.com/example/awesome-data/blob/" + ("a" * 40) + "/README.md#L4",
                    "listed_claim": "Transit Data API — realtime bus arrivals",
                    "line": 4,
                }],
                "upstream_evidence": [],
            },
            {
                "id": "tool:999999abcdef", "name": "Spatial Database",
                "url": "https://github.com/example/spatial",
                "description": "Spatial queries and indexed map data",
                "topics": ["Database"],
                "evidence_status": "UPSTREAM_DOCUMENTED_NOT_TESTED",
                "source_collections": [{
                    "repository": "example/awesome-geospatial",
                    "evidence_url": "https://github.com/example/awesome-geospatial/blob/" + ("b" * 40) + "/README.md#L9",
                    "line": 9,
                }],
                "upstream_evidence": [{
                    "evidence_url": "https://github.com/example/spatial/blob/" + ("c" * 40) + "/README.md#L3",
                    "documented_statement": "A spatial database providing search, bounding boxes and spatial indexing.",
                }],
                "license_spdx_id": "MIT",
                "last_documentation_review": "2026-10-30",
            },
            {
                "id": "tool:badspoof", "name": "Spyware fake",
                "url": "https://example.com",
                "description": "Realtime bus arrival",
                "topics": [],
                "evidence_status": "UPSTREAM_DOCUMENTED_NOT_TESTED",
                "source_collections": [{"evidence_url": "https://evil.example/evidence"}],
                "upstream_evidence": [],
            }
        ]
    }

def owned():
    return {"items": [{
        "id": "owned:transit", "kind": "asset", "name": "Bus integration",
        "repository": "jamesrwatsonx-creator/transport",
        "description": "Transport bus route data",
        "asset_type": "API", "categories": ["Transport"], "topics": ["transit"],
        "capabilities": ["transport"]
    }]}

class TestReadOnlyToolSearch(unittest.TestCase):
    def test_schema_and_list_evidence_gate(self):
        self.assertRaises(external_tools.ToolIndexError, external_tools.validate, {})
        hits = external_tools.search(candidates(), "realtime bus")
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["evidence_status"], "LISTED_ONLY")
        self.assertFalse(hits[0]["owned"])
        self.assertEqual(hits[0]["kind"], "external_individual_tool")
        self.assertTrue(hits[0]["list_evidence"][0]["evidence_url"].endswith("#L4"))

    def test_upstream_documented_is_not_runtime_verified(self):
        hits = external_tools.search(candidates(), "spatial database")
        self.assertTrue(hits)
        self.assertEqual(hits[0]["evidence_status"], "UPSTREAM_DOCUMENTED_NOT_TESTED")
        self.assertEqual(hits[0]["license_spdx_id"], "MIT")
        self.assertEqual(len(hits[0]["upstream_documentation"]), 1)

    def test_combined_cli_opt_in_and_no_write(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            o, t = path / "owned.json", path / "tools.json"
            o.write_text(json.dumps(owned()), encoding="utf-8")
            t.write_text(json.dumps(candidates()), encoding="utf-8")
            before = (o.read_bytes(), t.read_bytes())
            with patch.object(external_tools, "urlopen",
                              side_effect=AssertionError("network call is forbidden")):
                result = search_with_discovery.search_both(
                    "realtime bus", owned_catalog=o, tools_catalog=t
                )
            self.assertTrue(result["owned"])
            self.assertTrue(result["external_tools"])
            self.assertEqual(result["external"], [])
            self.assertIsNone(result["external_tools_error"])
            self.assertEqual((o.read_bytes(), t.read_bytes()), before)

    def test_no_external_call_on_default(self):
        with tempfile.TemporaryDirectory() as temp:
            o = Path(temp) / "owned.json"
            o.write_text(json.dumps(owned()), encoding="utf-8")
            with patch.object(external_tools, "load",
                              side_effect=AssertionError("external tools fetched")):
                result = search_with_discovery.search_both("bus", owned_catalog=o)
            self.assertEqual(result["external_tools"], [])
            self.assertIsNone(result["sources"]["external_tools"])

    def test_tool_index_unavailable_does_not_break_owned(self):
        with tempfile.TemporaryDirectory() as temp:
            o = Path(temp) / "owned.json"
            o.write_text(json.dumps(owned()), encoding="utf-8")
            with patch.object(external_tools, "load",
                              side_effect=external_tools.ToolIndexError("offline")):
                result = search_with_discovery.search_both(
                    "bus", owned_catalog=o, external_tools_enabled=True
                )
            self.assertTrue(result["owned"])
            self.assertEqual(result["external_tools"], [])
            self.assertEqual(result["external_tools_error"], "offline")

if __name__ == "__main__":
    unittest.main()

"""Read-only external catalog adapter tests; all run without network or repo writes."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import external_discovery as ext
import search_with_discovery as combined


def sample_external():
    def record(repo, tags, category, stars=10, **kwargs):
        return {
            "repository": repo,
            "url": "https://github.com/" + repo,
            "categories": [category],
            "discovery_tags": tags,
            "stars": stars,
            "stars_checked_at": "2026-10-29",
            "original_screenshot": False,
            **kwargs,
        }
    return {
        "schema_version": "1.0.0",
        "project": "Every Awesome Repo",
        "snapshot_date": "2026-10-29",
        "categories": [{"name": "AI"}, {"name": "UI"}],
        "repositories": [
            record("example/awesome-voice", ["voice", "speech", "tts"], "AI", 50),
            record("example/awesome-design", ["ui", "design", "frontend"], "UI", 100),
            record("example/awesome-booking", ["booking", "calendar"], "AI", 20),
            record("example/awesome-voice", ["voice"], "AI", 60),
            {"repository": "invalid/bad", "url": "https://evil.example/invalid/bad",
             "categories": ["AI"], "discovery_tags": ["voice"], "stars": 10000000},
        ],
    }


def sample_owned():
    return {
        "items": [
            {"id": "owned:voice", "kind": "asset", "name": "Speech Generator",
             "repository": "jamesrwatsonx-creator/speech", "description": "Voice and speech",
             "asset_type": "TOOL", "categories": ["Voice"], "topics": ["voice"],
             "capabilities": ["speech"]},
            {"id": "owned:ui", "kind": "repository", "name": "Design starter",
             "repository": "jamesrwatsonx-creator/design", "description": "UI starter",
             "categories": ["Design"], "topics": ["ui"], "capabilities": []},
        ],
    }


class TestExternalDiscovery(unittest.TestCase):
    def test_reject_invalid_schema(self):
        with self.assertRaises(ext.ExternalCatalogError):
            ext.validate_catalog({"repositories": []})
        with self.assertRaises(ext.ExternalCatalogError):
            ext.validate_catalog({**sample_external(), "schema_version": "2.0.0"})

    def test_reject_untrusted_repository_links(self):
        self.assertIsNone(ext.canonical_repository("org/repo", "https://evil.com/org/repo"))
        self.assertIsNone(ext.canonical_repository("org/repo", "http://github.com/org/repo"))
        self.assertIsNone(ext.canonical_repository("org/repo", "https://github.com/org/other"))
        self.assertIsNone(ext.canonical_repository("org/repo", "https://github.com/org/repo?x=1"))
        self.assertEqual(
            ext.canonical_repository("Org/Repo", "https://github.com/org/repo"),
            "Org/Repo",
        )

    def test_results_are_distinct_and_explicitly_unverified(self):
        hits = ext.search_catalog("voice assistant", sample_external(), limit=20)
        self.assertTrue(hits)
        self.assertEqual(hits[0]["repository"], "example/awesome-voice")
        self.assertTrue(all(h["owned"] is False for h in hits))
        self.assertTrue(all(h["source"] == ext.SOURCE_ID for h in hits))
        self.assertTrue(all(h["review_status"] == "UNVERIFIED_EXTERNAL_REFERENCE" for h in hits))
        self.assertEqual(len([h for h in hits if h["repository"] == "example/awesome-voice"]), 1)
        self.assertTrue(all("evil.example" not in h["url"] for h in hits))

    def test_overlap_annotation_does_not_change_external_ownership(self):
        hits = ext.search_catalog(
            "voice", sample_external(), exclude_repositories={"EXAMPLE/AWESOME-VOICE"}
        )
        self.assertTrue(hits[0]["possible_owned_identity_overlap"])
        self.assertFalse(hits[0]["owned"])

    def test_offline_files_are_read_only_and_no_external_network(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "external.json"
            raw = json.dumps(sample_external())
            file.write_text(raw, encoding="utf-8")
            with patch.object(ext, "urlopen", side_effect=AssertionError("network attempted")):
                catalog = ext.load_catalog(file)
            self.assertEqual(catalog["project"], "Every Awesome Repo")
            self.assertEqual(file.read_text(encoding="utf-8"), raw)

    def test_missing_external_file_produces_catalog_error(self):
        with self.assertRaises(ext.ExternalCatalogError):
            ext.load_catalog("/definitely/not/present/every-awesome.json")

    def test_invalid_external_json(self):
        with tempfile.TemporaryDirectory() as folder:
            file = Path(folder) / "bad.json"
            file.write_text("not-json", encoding="utf-8")
            with self.assertRaises(ext.ExternalCatalogError):
                ext.load_catalog(file)

    def test_combined_has_separate_namespaces_and_does_not_mutate_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            owned = Path(folder) / "owned.json"
            external = Path(folder) / "external.json"
            own_raw = json.dumps(sample_owned())
            ext_raw = json.dumps(sample_external())
            owned.write_text(own_raw, encoding="utf-8")
            external.write_text(ext_raw, encoding="utf-8")
            result = combined.search_both(
                "voice", owned_catalog=owned, external_catalog=external
            )
            self.assertTrue(result["owned"])
            self.assertTrue(result["external"])
            self.assertIsNone(result["external_error"])
            self.assertEqual(result["owned"][0]["id"], "owned:voice")
            self.assertEqual(result["external"][0]["source"], ext.SOURCE_ID)
            self.assertEqual(owned.read_text(encoding="utf-8"), own_raw)
            self.assertEqual(external.read_text(encoding="utf-8"), ext_raw)

    def test_opt_in_no_external_network_by_default(self):
        with tempfile.TemporaryDirectory() as folder:
            owned = Path(folder) / "owned.json"
            owned.write_text(json.dumps(sample_owned()), encoding="utf-8")
            with patch.object(ext, "load_catalog", side_effect=AssertionError("external called")):
                result = combined.search_both("voice", owned_catalog=owned)
            self.assertIsNone(result["sources"]["external"])
            self.assertEqual(result["external"], [])

    def test_external_failure_does_not_break_owned_search(self):
        with tempfile.TemporaryDirectory() as folder:
            owned = Path(folder) / "owned.json"
            owned.write_text(json.dumps(sample_owned()), encoding="utf-8")
            with patch.object(ext, "load_catalog", side_effect=ext.ExternalCatalogError("offline")):
                result = combined.search_both("voice", owned_catalog=owned, external=True)
            self.assertTrue(result["owned"])
            self.assertEqual(result["external"], [])
            self.assertEqual(result["external_error"], "offline")

    def test_cli_offline_integration(self):
        with tempfile.TemporaryDirectory() as folder:
            owned = Path(folder) / "owned.json"
            external = Path(folder) / "external.json"
            owned.write_text(json.dumps(sample_owned()), encoding="utf-8")
            external.write_text(json.dumps(sample_external()), encoding="utf-8")
            run = subprocess.run([
                sys.executable, str(ROOT / "scripts" / "search_with_discovery.py"),
                "voice assistant", "--owned-catalog-file", str(owned),
                "--external-catalog-file", str(external), "--limit", "5",
                "--external-limit", "5"
            ], check=True, capture_output=True, text=True)
            data = json.loads(run.stdout)
            self.assertTrue(data["owned"])
            self.assertTrue(data["external"])


if __name__ == "__main__":
    unittest.main()

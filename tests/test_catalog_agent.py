"""Check agent boundaries using the existing canonical catalog."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import catalog_agent as c
import registry as r


class AgentCatalogTests(unittest.TestCase):
    def test_private_metadata_is_opt_in(self):
        original_read = r.read
        private = {'id': 'repository:private-test', 'name': 'private-fixture', 'description': 'uniqueprivatefixture', 'url': 'https://example.invalid', 'categories': []}
        def read(path, default=None):
            if str(path) == '.local/private-catalog.json': return [private]
            return original_read(path, default)
        with patch.object(r, 'read', side_effect=read):
            self.assertEqual(c.search('uniqueprivatefixture'), [])
            result = c.search('uniqueprivatefixture', private_local=True)
            self.assertEqual(result[0]['id'], private['id'])
            self.assertEqual(c.search('uniqueprivatefixture', private_local=True, verified=True), [])

    def test_repository_filter(self):
        results = c.search(repository='voicebox', limit=20)
        self.assertTrue(results)
        self.assertTrue(all('voicebox' in x.get('repository', '').lower() for x in results))

    def test_verified_excludes_metadata_and_candidates(self):
        results = c.search(verified=True, limit=20)
        self.assertTrue(results)
        self.assertTrue(all(x['state'] == 'VERIFIED' and x['entity_type'] != 'REPOSITORY' for x in results))

    def test_category_filter(self):
        results = c.search(category='operational:07', limit=20)
        self.assertTrue(results)
        self.assertTrue(all('operational:07' in x['categories'] for x in results))

    def test_unknown_requirement_remains_gap(self):
        with patch.object(r, 'write', side_effect=AssertionError('read-only interface wrote data')):
            result = c.plan(['unobtainium teleportation 987654321'], limit=2)
        self.assertEqual(result['missing_components'], ['unobtainium teleportation 987654321'])
        self.assertEqual(result['composition']['selected'], [])

    def test_exact_capability_uses_existing_composer(self):
        cap = next(x for x in r.records('capabilities') if x['status'] == 'VERIFIED' and x.get('providers'))
        result = c.plan([cap['name']], limit=2)
        self.assertIn(cap['id'], result['composition']['requirements'])
        self.assertTrue(result['composition']['selected'])
        self.assertTrue(result['composition']['selected'][0]['source']['source_path'])

    def test_composition_gaps_are_reported_as_missing_requirements(self):
        cap = next(x for x in r.records('capabilities') if x['status'] == 'VERIFIED' and x.get('providers'))
        blocked = {'requirements': [cap['id']], 'selected': [], 'missing_capabilities': [cap['id']]}
        with patch.object(r, 'compose', return_value=blocked):
            result = c.plan([cap['name']], limit=1)
        self.assertEqual(result['missing_components'], [cap['name']])
        self.assertEqual(result['unprovided_capabilities'], [cap['id']])


if __name__ == '__main__': unittest.main()

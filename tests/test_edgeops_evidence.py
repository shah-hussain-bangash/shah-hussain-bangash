import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from verify_edgeops_evidence import verify


class EvidenceChecks(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)/'profile'
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns('.git','__pycache__'))
        self.docs = self.root/'docs/edgeops'

    def change_manifest(self, filename, mutate):
        path = self.docs/filename
        data = json.loads(path.read_text(encoding='utf-8'))
        mutate(data)
        path.write_text(json.dumps(data), encoding='utf-8')

    def test_reviewed_package_passes_without_physical_authority(self):
        result = verify(self.root)
        self.assertEqual(result['artifacts_checked'], 6)
        self.assertFalse(result['physical_acceptance_verified'])
        self.assertFalse(result['external_links_checked'])

    def test_same_size_video_change_rejected(self):
        path = self.docs/'assets/EDGEOPS-software-demo.webm'
        data = bytearray(path.read_bytes()); data[-1] ^= 1; path.write_bytes(data)
        with self.assertRaisesRegex(ValueError, 'SHA-256 differs'):
            verify(self.root)

    def test_same_size_arrival_pack_change_rejected(self):
        path = self.docs/'assets/EDGEOPS-original-30-arrival-pack-v2.zip'
        data = bytearray(path.read_bytes()); data[-1] ^= 1; path.write_bytes(data)
        with self.assertRaisesRegex(ValueError, 'SHA-256 differs'):
            verify(self.root)

    def test_arrival_report_must_match_archive_reference(self):
        self.change_manifest('arrival-pack-verification.json', lambda d:d.update(archive_sha256='0'*64))
        with self.assertRaisesRegex(ValueError, 'report disagrees'):
            verify(self.root)

    def test_arrival_pack_cannot_claim_physical_acceptance(self):
        self.change_manifest('arrival-pack-manifest.json', lambda d:d.update(physical_acceptance_verified=True))
        with self.assertRaisesRegex(ValueError, 'physical acceptance'):
            verify(self.root)

    def test_changed_pdf_rejected(self):
        with (self.docs/'EDGEOPS-Software-Evidence-Brief.pdf').open('ab') as output:
            output.write(b'changed')
        with self.assertRaisesRegex(ValueError, 'Artifact size differs'):
            verify(self.root)

    def test_missing_screenshot_rejected(self):
        (self.docs/'assets/observation-inspector-390.png').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing or linked file'):
            verify(self.root)

    def test_same_size_screenshot_change_rejected_by_hash(self):
        path = self.docs/'assets/observation-inspector-390.png'
        data = bytearray(path.read_bytes()); data[-1] ^= 1; path.write_bytes(data)
        with self.assertRaisesRegex(ValueError, 'SHA-256 differs'):
            verify(self.root)

    def test_escape_path_rejected(self):
        self.change_manifest('brief-manifest.json', lambda d:d.update(file='../../../../outside.pdf'))
        with self.assertRaisesRegex(ValueError, 'escapes'):
            verify(self.root)

    def test_inconsistent_source_commit_rejected(self):
        self.change_manifest('brief-manifest.json', lambda d:d.update(source_application_commit='0'*40))
        with self.assertRaisesRegex(ValueError, 'commits disagree'):
            verify(self.root)

    def test_broken_local_heading_rejected(self):
        with (self.docs/'EVIDENCE.md').open('a', encoding='utf-8') as output:
            output.write('\n[Broken heading](EVIDENCE.md#missing-heading)\n')
        with self.assertRaisesRegex(ValueError, 'Missing heading'):
            verify(self.root)

    def test_physical_claim_in_synthetic_record_rejected(self):
        self.change_manifest('visual-capture-manifest.json', lambda d:d.update(physical_acceptance_verified=True))
        with self.assertRaisesRegex(ValueError, 'physical acceptance'):
            verify(self.root)


if __name__ == '__main__':
    unittest.main()


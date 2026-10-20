import hashlib
import importlib.util
import io
from pathlib import Path
import tarfile
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('release', Path(__file__).parents[1] / 'scripts/release.py')
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)


class BundleTests(unittest.TestCase):
    def bundle(self, directory, checksum=None, extra=False):
        name = 'acshift-linux-amd64'
        binary = b'example binary'
        digest = checksum or hashlib.sha256(binary).hexdigest()
        path = Path(directory) / (name + '.tar.gz')
        with tarfile.open(path, 'w:gz') as archive:
            for filename, data in [(name, binary), ('SHA256SUMS', f'{digest}  {name}\n'.encode())]:
                info = tarfile.TarInfo(filename)
                info.size = len(data)
                archive.addfile(info, io.BytesIO(data))
            if extra:
                archive.addfile(tarfile.TarInfo('../unexpected'))
        return path

    def test_accepts_bundle_with_matching_binary_checksum(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.bundle(directory)
            self.assertEqual(release.bundle_digest(path), hashlib.sha256(path.read_bytes()).hexdigest())

    def test_rejects_corrupted_binary(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, 'checksum'):
                release.bundle_digest(self.bundle(directory, '0' * 64))

    def test_rejects_unexpected_archive_members(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, 'members'):
                release.bundle_digest(self.bundle(directory, extra=True))

    def test_rejects_changed_release_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.bundle(directory)
            with self.assertRaisesRegex(ValueError, 'pinned'):
                release.verify_bundle(path, '0' * 64)


if __name__ == '__main__':
    unittest.main()

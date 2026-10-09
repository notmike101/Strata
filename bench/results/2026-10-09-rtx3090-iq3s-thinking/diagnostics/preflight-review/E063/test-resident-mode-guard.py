import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('resident_guard', Path(__file__).with_name('resident-mode-guard.py'))
guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guard)


class ResidentModeTests(unittest.TestCase):
    good = b'strata generate: resident RAM mode: 32.00 GiB of experts in RAM (page-locked), 8409 in the GPU cache; adaptive swaps exchange them with the GPU cache (no file reads)\n'

    def test_requested_mode_has_positive_proof(self):
        self.assertIn('8409', guard.require_resident_startup(self.good)['resident_mode_line'])

    def test_missing_or_pageable_mode_refused(self):
        for data in [b'', self.good.replace(b'page-locked', b'pageable')]:
            with self.subTest(data=data), self.assertRaisesRegex(ValueError, 'page-locked'):
                guard.require_resident_startup(data)

    def test_partial_residency_refused(self):
        for warning in [b'WARNING: the whole resident RAM mode does not fit', b'WARNING: a prompt chunk of 32768 tokens lends 100 cache slots to the prompt path, but only 10 of their experts fit in RAM']:
            with self.subTest(warning=warning), self.assertRaisesRegex(ValueError, 'fallback'):
                guard.require_resident_startup(warning + b'\n' + self.good)

    def test_different_gpu_cache_count_refused(self):
        with self.assertRaisesRegex(ValueError, '8409'):
            guard.require_resident_startup(self.good.replace(b'8409', b'8300'))


unittest.main()

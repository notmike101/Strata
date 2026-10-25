"""CPU-only lifecycle tests: python -m unittest serve.test_runtime_manager -v."""
import threading
import time
import unittest

try:
    from serve.runtime_manager import RuntimeManager
except ImportError:
    RuntimeManager = None


class FakeRuntime:
    def __init__(self, name, events):
        self.name, self.events = name, events
        self.fail_unload = False
        self.resident = False

    def load(self):
        self.events.append(('load', self.name))
        self.resident = True

    def unload(self):
        self.events.append(('unload', self.name))
        if self.fail_unload:
            raise RuntimeError('still releasing memory')
        self.resident = False

    def close(self):
        self.unload()


class Lifecycle(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(RuntimeManager, 'runtime lifecycle manager is not implemented')
        self.events = []
        self.a = FakeRuntime('a', self.events)
        self.b = FakeRuntime('b', self.events)
        self.now = 100.0
        self.manager = RuntimeManager({'a': self.a, 'b': self.b}, idle_seconds=10,
                                      clock=lambda: self.now)

    def test_switch_releases_previous_first(self):
        with self.manager.use('a'):
            pass
        with self.manager.use('b'):
            self.assertFalse(self.a.resident)
            self.assertTrue(self.b.resident)
        self.assertEqual(self.events, [('load', 'a'), ('unload', 'a'), ('load', 'b')])

    def test_same_model_is_reused(self):
        for _ in range(2):
            with self.manager.use('a'):
                pass
        self.assertEqual(self.events, [('load', 'a')])

    def test_dead_active_worker_is_reloaded(self):
        with self.manager.use('a'):
            pass
        self.a.resident = False
        with self.manager.use('a'):
            self.assertTrue(self.a.resident)
        self.assertEqual(self.events, [('load', 'a'), ('load', 'a')])

    def test_invalid_model_does_not_evict(self):
        with self.manager.use('a'):
            pass
        with self.assertRaises(KeyError):
            with self.manager.use('unknown'):
                pass
        self.assertEqual(self.events, [('load', 'a')])

    def test_failed_unload_blocks_next_load(self):
        with self.manager.use('a'):
            pass
        self.a.fail_unload = True
        with self.assertRaisesRegex(RuntimeError, 'releasing'):
            with self.manager.use('b'):
                self.fail('must not admit next model')
        self.assertNotIn(('load', 'b'), self.events)
        self.assertEqual(self.manager.status()['active_model'], 'a')

    def test_idle_is_measured_after_request_and_never_during_request(self):
        with self.manager.use('a'):
            self.now = 200
            self.assertFalse(self.manager.unload_idle())
        self.now = 209
        self.assertFalse(self.manager.unload_idle())
        self.now = 210
        self.assertTrue(self.manager.unload_idle())
        self.assertFalse(self.a.resident)

    def test_request_holds_ownership_and_queue_is_fifo(self):
        got = []
        with self.manager.use('a'):
            threads = []
            for index in range(3):
                def request(i=index):
                    with self.manager.use('b'):
                        got.append(i)
                thread = threading.Thread(target=request)
                thread.start()
                threads.append(thread)
                deadline = time.monotonic() + 2
                while self.manager.status()['queued'] != index + 1:
                    self.assertLess(time.monotonic(), deadline)
                    time.sleep(.005)
            self.assertEqual(got, [])
            self.assertFalse(self.manager.unload_idle())
        for thread in threads:
            thread.join(2)
            self.assertFalse(thread.is_alive())
        self.assertEqual(got, [0, 1, 2])

    def test_failure_cleans_partial_load(self):
        def broken_load():
            self.b.resident = True
            raise RuntimeError('load failed')
        self.b.load = broken_load
        with self.assertRaisesRegex(RuntimeError, 'load failed'):
            with self.manager.use('b'):
                pass
        self.assertFalse(self.b.resident)
        self.assertIsNone(self.manager.status()['active_model'])

    def test_close_rejects_further_requests(self):
        with self.manager.use('a'):
            pass
        self.manager.close()
        with self.assertRaisesRegex(RuntimeError, 'closed'):
            with self.manager.use('a'):
                pass


if __name__ == '__main__':
    unittest.main()

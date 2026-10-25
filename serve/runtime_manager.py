"""Exclusive FIFO ownership of optional heavyweight model runtimes."""
from __future__ import annotations

from collections import deque
from contextlib import contextmanager
import threading
import time


class RuntimeManager:
    def __init__(self, runtimes, idle_seconds=600, clock=time.monotonic):
        if idle_seconds < 0:
            raise ValueError('idle_seconds must be nonnegative')
        self.runtimes = dict(runtimes)
        self.idle_seconds, self.clock = idle_seconds, clock
        self._condition = threading.Condition()
        self._queue = deque()
        self._busy = False
        self._closed = False
        self._active = None
        self._last_used = clock()

    @contextmanager
    def _turn(self):
        ticket = object()
        with self._condition:
            if self._closed:
                raise RuntimeError('runtime manager is closed')
            self._queue.append(ticket)
            try:
                while self._busy or self._queue[0] is not ticket:
                    self._condition.wait()
                    if self._closed:
                        raise RuntimeError('runtime manager is closed')
                self._queue.popleft()
                self._busy = True
            except BaseException:
                if ticket in self._queue:
                    self._queue.remove(ticket)
                self._condition.notify_all()
                raise
        try:
            yield
        finally:
            with self._condition:
                self._last_used = self.clock()
                self._busy = False
                self._condition.notify_all()

    def _release_active(self):
        if self._active is not None:
            self.runtimes[self._active].unload()
            # Only relinquish ownership after successful, synchronous cleanup.
            with self._condition:
                self._active = None

    @contextmanager
    def use(self, model):
        if model not in self.runtimes:
            raise KeyError(model)
        with self._turn():
            if model != self._active:
                self._release_active()
                with self._condition:
                    self._active = model
            if not self.runtimes[model].resident:
                try:
                    self.runtimes[model].load()
                except BaseException:
                    self._release_active()
                    raise
            yield self.runtimes[model]

    def unload(self, model=None):
        if model is not None and model not in self.runtimes:
            raise KeyError(model)
        with self._turn():
            if model is None or model == self._active:
                self._release_active()

    def unload_idle(self):
        with self._condition:
            if (self._closed or self._busy or self._queue or self._active is None
                    or not self.idle_seconds or self.clock() - self._last_used < self.idle_seconds):
                return False
            self._busy = True
        try:
            self._release_active()
            return True
        finally:
            with self._condition:
                self._busy = False
                self._condition.notify_all()

    def status(self):
        with self._condition:
            return {'active_model': self._active, 'busy': self._busy,
                    'queued': len(self._queue), 'idle_unload_s': self.idle_seconds}

    def close(self):
        with self._condition:
            self._closed = True
            self._condition.notify_all()
            while self._busy:
                self._condition.wait()
            self._busy = True
        try:
            self._release_active()
            for runtime in self.runtimes.values():
                runtime.close()
        finally:
            with self._condition:
                self._busy = False
                self._condition.notify_all()

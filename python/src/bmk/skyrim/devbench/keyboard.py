"""Owned, bounded keyboard input through DevBench."""

from contextlib import contextmanager
from uuid import uuid4

from .client import DevBenchError


class Keyboard:
    def __init__(self, client):
        self.client = client
        self.owner = f"pytest-keyboard-{uuid4().hex}"
        capabilities = client.call("input", {"action": "capabilities"})
        contract = capabilities["contract"]
        keyboard = capabilities["capabilities"]["keyboard"]
        if (
            contract["name"] != "devbench.input"
            or contract["version"]["major"] not in (1, 2)
            or keyboard["version"] != 1
            or keyboard["encoding"] != "DirectInputScanCode"
            or not keyboard["available"]
            or not {"down", "up", "tap", "releaseAll"}.issubset(keyboard["actions"])
        ):
            raise DevBenchError(f"Unsupported keyboard input contract: {capabilities}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.release_all()

    def _send(self, action, **arguments):
        return self.client.call(
            "input",
            {"action": action, "device": "keyboard", "owner": self.owner, **arguments},
        )

    def mapped_key(self, control):
        key = self.client.papyrus("Input", "GetMappedKey", [control, 0])
        if key == -1:
            raise DevBenchError(f"{control!r} has no keyboard binding: {key}")
        return key

    def tap(self, key, duration_ms=50):
        return self._send("tap", key=key, durationMs=duration_ms)

    @contextmanager
    def hold(self, key, max_hold_ms=5000):
        try:
            self._send("down", key=key, maxHoldMs=max_hold_ms)
            yield
        finally:
            self._send("up", key=key)

    def release_all(self):
        result = self._send("releaseAll")
        if result["failed"]:
            raise DevBenchError(f"Keyboard release failed: {result}")

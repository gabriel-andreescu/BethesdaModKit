"""Polling and reversible file changes for tests."""

import json
import re
import time
from contextlib import contextmanager
from pathlib import Path


def wait_for(
    read,
    predicate=bool,
    message="Condition did not become true",
    *,
    timeout=10,
    interval=0.05,
):
    deadline = time.monotonic() + timeout
    while True:
        observed = read()
        if predicate(observed):
            return observed
        if time.monotonic() >= deadline:
            raise AssertionError(
                f"{message}. Last state: {json.dumps(observed, default=str)}"
            )
        time.sleep(interval)


def set_ini_values(path: str | Path, values: dict):
    path = Path(path)
    text = path.read_bytes().decode("utf-8")
    for key, value in values.items():
        pattern = re.compile(
            r"^" + re.escape(key) + r"[^\S\r\n]*=[^\r\n]*", re.MULTILINE
        )
        if len(pattern.findall(text)) != 1:
            raise ValueError(f"Expected one setting: {key}")
        text = pattern.sub(lambda match, key=key, value=value: f"{key} = {value}", text)
    path.write_bytes(text.encode("utf-8"))


@contextmanager
def preserved_file(path: str | Path, backup: str | Path | None = None):
    path = Path(path)
    original = path.read_bytes()
    if backup is not None:
        Path(backup).write_bytes(original)
    try:
        yield path
    finally:
        path.write_bytes(original)

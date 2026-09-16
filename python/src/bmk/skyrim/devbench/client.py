"""DevBench HTTP connections and game operations."""

from __future__ import annotations

import ipaddress
import os
import subprocess
import time
from collections.abc import Sequence
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

import requests


class DevBenchError(RuntimeError):
    """A connection or tool call failed."""


class Client:
    def __init__(self, base_url: str, *, timeout: float = 30):
        url = urlsplit(base_url)
        loopback = url.hostname == "localhost"
        if not loopback and url.hostname:
            try:
                loopback = ipaddress.ip_address(url.hostname).is_loopback
            except ValueError:
                pass
        if (
            url.scheme != "http"
            or not loopback
            or url.username
            or url.query
            or url.fragment
        ):
            raise ValueError("DevBench requires an HTTP loopback URL")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.trust_env = False
        self.transcript: list[dict] = []
        self.launcher: subprocess.Popen | None = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self.session.close()

    def quit(self):
        return self.call("console", {"command": "qqq"})

    def health(self, *, timeout: float | None = None):
        response = self.session.get(
            f"{self.base_url}/api/health",
            timeout=self.timeout if timeout is None else timeout,
        )
        response.raise_for_status()
        health = response.json()
        if not health.get("ok"):
            raise DevBenchError(f"DevBench is unhealthy: {health}")
        return health

    def launch(
        self,
        command: Sequence[str],
        *,
        cwd: str | Path | None = None,
        timeout: float = 120,
    ):
        self.launcher = subprocess.Popen(
            command,
            cwd=cwd,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise DevBenchError(
                    f"DevBench at {self.base_url} did not become available within {timeout}s"
                )
            try:
                return self.health(timeout=min(self.timeout, remaining))
            except (requests.ConnectionError, requests.Timeout):
                time.sleep(min(0.25, max(0, deadline - time.monotonic())))

    def call(
        self,
        tool: str,
        arguments: dict | None = None,
        *,
        record=True,
        timeout: float | None = None,
    ):
        arguments = {} if arguments is None else arguments
        receipt = {
            "time": datetime.now(UTC).isoformat(),
            "tool": tool,
            "args": deepcopy(arguments),
        }
        try:
            response = self.session.post(
                f"{self.base_url}/api/tool/{tool}",
                json=arguments,
                timeout=self.timeout if timeout is None else timeout,
            )
            try:
                response.raise_for_status()
            except requests.HTTPError as error:
                receipt["responseBody"] = response.text
                raise requests.HTTPError(
                    f"{error}: {response.text}",
                    response=response,
                    request=error.request,
                ) from error
            result = response.json()
            receipt["result"] = deepcopy(result)
            # Failed runs are successful status requests. The run result is checked below.
            completed = (
                tool == "scenario"
                and arguments.get("action") == "status"
                and result.get("done")
                and "result" in result
            )
            if (result.get("ok") is False and not completed) or result.get(
                "called"
            ) is False:
                raise DevBenchError(f"DevBench {tool} failed: {result}")
            return result
        except BaseException as error:
            receipt["error"] = str(error)
            raise
        finally:
            if record or "error" in receipt:
                self.transcript.append(receipt)

    def papyrus(
        self,
        script: str,
        function: str,
        args=(),
        self_form: str = "",
        *,
        timeout_ms: int | None = None,
    ):
        parameters = {
            "action": "call",
            "script": script,
            "function": function,
            "args": list(args),
        }
        if self_form:
            parameters["self"] = {"form": self_form}
        if timeout_ms is not None:
            parameters["timeoutMs"] = timeout_ms
        return self.call("papyrus", parameters)["returned"]

    def wait_run(self, run_id: int):
        try:
            while True:
                status = self.call(
                    "scenario", {"action": "status", "runId": run_id}, record=False
                )
                if status["done"]:
                    break
                time.sleep(0.25)
        except BaseException as error:
            error.add_note(
                f"Waiting for DevBench run {run_id} stopped. "
                "This does not cancel the run. Check its status before continuing."
            )
            raise
        result = status["result"]
        self.transcript.append(
            {
                "time": datetime.now(UTC).isoformat(),
                "tool": "scenario-result",
                "runId": run_id,
                "result": deepcopy(result),
            }
        )
        if not result["ok"]:
            raise DevBenchError(f"Scenario {run_id} failed: {result}")
        return result

    def scenario(self, steps: list[dict], *, repeat=1, continue_on_error=False):
        run = self.call(
            "scenario",
            {
                "async": True,
                "steps": steps,
                "repeat": repeat,
                "continueOnError": continue_on_error,
            },
        )
        return self.wait_run(run["runId"])

    def _events(self, since: int = 0):
        response = self.session.get(
            f"{self.base_url}/api/events", params={"since": since}, timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def _save_load(self, action: str, name: str, event_name: str, timeout: float):
        receipt = {
            "time": datetime.now(UTC).isoformat(),
            "tool": "lifecycle",
            "args": {"action": action, "name": name, "event": event_name},
        }
        try:
            cursor = self._events()["headSeq"]
            self.call("game", {"action": action, "name": name})
            deadline = time.monotonic() + timeout
            while True:
                for event in self._events(cursor)["events"]:
                    # The response's headSeq can include events absent from its snapshot.
                    cursor = event["seq"]
                    if (
                        event["topic"] == "lifecycle"
                        and event["data"]["event"] == event_name
                    ):
                        receipt["result"] = deepcopy(event)
                        return
                if time.monotonic() >= deadline:
                    raise DevBenchError(
                        f"Timed out waiting for {event_name} after {action} {name!r}"
                    )
                time.sleep(0.05)
        except BaseException as error:
            receipt["error"] = str(error)
            raise
        finally:
            self.transcript.append(receipt)

    def save(self, name: str, *, timeout: float = 15):
        self._save_load("save", name, "saveGame", timeout)

    def load(
        self, name: str, *, cell: str = "", settle_ms: int = 0, timeout: float = 30
    ):
        self._save_load("load", name, "postLoadGame", timeout)
        self.scenario(
            [
                {"waitUntil": "noBlockingMenu", "timeoutMs": int(timeout * 1000)},
                {"wait": settle_ms},
            ]
        )
        if cell:
            actual = self.call("inspect", {"kind": "scene"})["cell"]["editorId"]
            if actual != cell:
                raise DevBenchError(
                    f"Save {name!r} loaded in {actual}, expected {cell}"
                )

    def form_id(self, local_id: int, plugin: str) -> int:
        mods = self.call("inspect", {"kind": "mods"})
        for collection, prefix, shift in (
            ("plugins", 0, 24),
            ("lightPlugins", 0xFE000000, 12),
        ):
            for loaded in mods[collection]:
                if loaded["name"].casefold() != plugin.casefold():
                    continue
                if not 0 <= local_id < (1 << shift):
                    raise ValueError(
                        f"Invalid local form ID for {plugin}: 0x{local_id:X}"
                    )
                full_id = prefix | (loaded["index"] << shift) | local_id
                # Scripted objects can omit formId in GetFormFromFile's returned object.
                value = self.papyrus("Form", "GetFormID", self_form=f"0x{full_id:08X}")
                if value is not None and value & 0xFFFFFFFF == full_id:
                    return full_id
                raise DevBenchError(f"Missing form {plugin}|0x{local_id:X}")
        raise DevBenchError(f"Plugin is not loaded: {plugin}")

    def spawn(
        self,
        base_id: int,
        form_type: str,
        *,
        at="0x14",
        persistent=False,
        disabled=False,
    ):
        base = f"0x{base_id:08X}"
        query = {"kind": "refs", "formType": form_type, "limit": 512}
        before = self.call("inspect", query)
        if before["truncated"]:
            raise DevBenchError("Too many references to identify a spawned reference")
        existing = {ref["formId"] for ref in before["refs"]}
        # Scripted forms can omit the returned reference in Papyrus results.
        self.papyrus(
            "ObjectReference",
            "PlaceAtMe",
            [{"form": base}, 1, persistent, disabled],
            at,
        )
        after = self.call("inspect", query)
        spawned = [
            ref
            for ref in after["refs"]
            if ref["base"]["formId"] == base and ref["formId"] not in existing
        ]
        if after["truncated"] or len(spawned) != 1:
            raise DevBenchError(
                "The spawned reference could not be identified uniquely"
            )
        return spawned[0]["formId"]

# Skyrim DevBench

BMK provides a Python client and pytest fixtures for
[DevBench](https://github.com/alandtse/devbench), plus a native API package for
plugins that expose custom inspection or actions.

## Python setup

Requires Python 3.11+. In a mod's Python project:

```powershell
uv add --dev "bethesda-mod-kit[test] @ git+https://github.com/gabriel-andreescu/BethesdaModKit.git#subdirectory=python"
```

Install [DevBench](https://www.nexusmods.com/skyrimspecialedition/mods/181326)
in Skyrim. The Python client uses its REST API and does not require native API
integration in the mod being tested.

```python
from bmk.skyrim.devbench import Client

with Client("http://127.0.0.1:8920") as client:
    state = client.call("inspect", {"kind": "state"})
```

To launch Skyrim first, pass a command and its arguments to `client.launch()`:

```python
with Client("http://127.0.0.1:8920") as client:
    client.launch(["C:/Games/Skyrim/skse64_loader.exe"], cwd="C:/Games/Skyrim")
    client.load("TestBaseline")
```

The command can invoke a mod manager instead. `launch()` waits for DevBench to
answer, independently of the launcher process. Closing the client leaves the
game running.

## Pytest

Load the fixtures in the suite's `conftest.py`:

```python
pytest_plugins = ["bmk.skyrim.devbench.pytest_plugin"]
```

A startup check in `tests/game/test_startup.py`:

```python
import pytest


@pytest.mark.game
def test_main_menu(devbench, wait_for):
    wait_for(
        lambda: devbench.call("menu", {"action": "list"}),
        lambda menus: "Main Menu" in menus["openMenus"],
        "Skyrim did not reach the main menu",
    )
```

For tests that need a character, create a `TestBaseline` save first and load it
in the test or its setup fixture with `devbench.load("TestBaseline")`.

Run the suite:

```powershell
uv run pytest tests/game --game-tests
```

| Option           | Purpose                                                                                              |
| ---------------- | ---------------------------------------------------------------------------------------------------- |
| `--game-tests`   | Enable game tests. Without it, tests marked `game` and tests using the DevBench session are skipped. |
| `--devbench-url` | Override the configured HTTP loopback address.                                                       |
| `--game-results` | Transcript directory, defaulting to `test-results/game`.                                             |

Connection and launch settings use pytest's configuration. In `pyproject.toml`:

```toml
[tool.pytest.ini_options]
devbench_url = "http://127.0.0.1:8920"
devbench_command = ['C:\Games\Skyrim\skse64_loader.exe']
devbench_cwd = 'C:\Games\Skyrim'
```

| Setting                   | Default                 | Purpose                                                                                                        |
| ------------------------- | ----------------------- | -------------------------------------------------------------------------------------------------------------- |
| `devbench_url`            | `http://127.0.0.1:8920` | DevBench endpoint.                                                                                             |
| `devbench_command`        | Empty                   | Launcher executable followed by separate arguments. Empty connects to a running game.                          |
| `devbench_cwd`            | Current directory       | Launcher working directory.                                                                                    |
| `devbench_launch_timeout` | `120`                   | Seconds to wait for DevBench after launching. Also the default for the `wait_for` fixture.                     |
| `devbench_timeout`        | `30`                    | HTTP request timeout in seconds.                                                                               |
| `devbench_quit_on_exit`   | `false`                 | Request game exit after the session, including when tests fail. Applies to launched and already-running games. |

The session launches once, when its first test requests the client. Run game
tests without pytest-xdist workers.

Set `devbench_quit_on_exit = true` to quit after the suite. This queues Skyrim's
`qqq` command. It does not wait for process exit or mod manager cleanup.

| Fixture            | Value                                                                                                                 |
| ------------------ | --------------------------------------------------------------------------------------------------------------------- |
| `devbench`         | Client with a separate JSON transcript for each test.                                                                 |
| `devbench_session` | Shared client for the test session.                                                                                   |
| `game_artifacts`   | Output directory for the current test.                                                                                |
| `wait_for`         | [`bmk.testing.wait_for`](#helpers) with the configured timeout. Pass `timeout=` to override it for a particular wait. |

## Helpers

Import from `bmk.skyrim.devbench`:

| Helper                            | Use                                                                    |
| --------------------------------- | ---------------------------------------------------------------------- |
| `Client(base_url, *, timeout=30)` | HTTP client. Use as a context manager or call `close()` when finished. |
| `Keyboard(client)`                | Resolve mapped controls and send taps or held keys through DevBench.   |

`Keyboard` supports context management and a `hold` context for releasing keys.
For example:

```python
from bmk.skyrim.devbench import Keyboard


with Keyboard(devbench) as keyboard:
    keyboard.tap(keyboard.mapped_key("Jump"))
```

### Client methods

| Method                                                                      | Behavior                                                                                                                                                             |
| --------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `call(tool, arguments=None, *, record=True, timeout=None)`                  | Returns the tool's JSON result. Raises on HTTP errors or results reporting `ok: false` or `called: false`. `timeout` overrides the client's request timeout.         |
| `health(*, timeout=None)`                                                   | Returns the host's health response.                                                                                                                                  |
| `quit()`                                                                    | Queues Skyrim's `qqq` command to exit the game. Returns the command response.                                                                                        |
| `launch(command, *, cwd=None, timeout=120)`                                 | Starts the command and waits up to `timeout` seconds for a healthy response. Returns that response.                                                                  |
| `papyrus(script, function, args=(), self_form="", *, timeout_ms=None)`      | Returns the Papyrus function's value. `timeout_ms` sets DevBench's VM wait. Allow a longer HTTP timeout on the client for long calls.                                |
| `scenario(steps, *, repeat=1, continue_on_error=False)`                     | Runs DevBench steps and returns the completed transcript. Raises if the run fails.                                                                                   |
| `wait_run(run_id)`                                                          | Waits for an asynchronous scenario or replay and returns its result. Raises if the run fails.                                                                        |
| `save(name, *, timeout=15)`                                                 | Requests a save and waits for `saveGame`.                                                                                                                            |
| `load(name, *, cell="", settle_ms=0, timeout=30)`                           | Waits for `postLoadGame`, then for blocking menus to close. `timeout` applies separately to each phase. Optionally waits `settle_ms` and checks the cell's EditorID. |
| `form_id(local_id, plugin)`                                                 | Resolves and verifies a full or light plugin's form. Returns its runtime FormID as an integer.                                                                       |
| `spawn(base_id, form_type, *, at="0x14", persistent=False, disabled=False)` | Places one reference and returns its hex FormID string. Raises if it cannot uniquely identify the new reference within the inspection limit of 512.                  |

All timeouts use seconds except arguments ending in `_ms`. Game operations that
change state are not automatically retried.

Import general test helpers from `bmk.testing`:

| Helper                                | Use                                                          |
| ------------------------------------- | ------------------------------------------------------------ |
| `wait_for(read, predicate=bool, ...)` | Poll until a condition passes or its timeout expires.        |
| `preserved_file(path, backup=None)`   | Restore a file's original bytes when leaving the context.    |
| `set_ini_values(path, values)`        | Replace existing INI keys. Each key must occur exactly once. |

## Scenario files

The `devbench-scenario` command runs a JSON object containing `steps`, with
optional `repeat` and `continueOnError` values. Step contents follow DevBench's
[scenario format](https://github.com/alandtse/devbench#scripted-tests).

```powershell
uv run devbench-scenario scenario.json --url=http://127.0.0.1:8920 --output=test-results/scenario.json
```

The client waits for completion or failure. Set `timeoutMs` on `waitFor` and
`waitUntil` steps to bound individual conditions. Interrupting the client does
not cancel the host's run. Check the reported run ID with `scenario`'s `status`
action before continuing.

Use `--timeout` for the HTTP timeout. To launch first, place `--launch` followed
by the executable and its arguments last on the command line. `--cwd` sets the
working directory and `--launch-timeout` controls how long to wait for DevBench.

## Native API

Add the API package and companion source to a Skyrim plugin:

```lua
add_requires("devbench-api 2026.09.13", {system = false})

target("MyMod")
    add_packages("devbench-api")
    add_rules("@devbench-api/integration")
```

The package provides `DevBenchAPI.h`. Follow the
[API's lifecycle and callback contracts](https://github.com/alandtse/devbench/blob/main/include/DevBenchAPI.h)
when registering custom tools.

Native integration does not require Python. Register tools only when the
DevBench interface is available so the plugin also works without the host.

BMK also provides
[`BMK::Skyrim::DevBench::InspectOnGameThread`](../../../../native/include/BMK/Skyrim/DevBench.h)
for inspection callbacks that need to read game state on the game thread.
Require the `bmk` header package and add it to the target's packages to use it.

Call this helper from DevBench's listener-thread inspection callback, after
SKSE's task interface is available. It blocks that thread for up to three
seconds while the game thread runs the inspection. Do not call it from the game
thread.

A timeout returns `a_timeoutResponse` without cancelling the queued inspection.
Copy borrowed callback data into owning values before enqueueing the inspection.
For example, copy a JSON argument string into `std::string` and capture that
string instead of the original `const char*`. Capturing a pointer by value does
not copy the pointed-to data.

The helper retains the callable, including after a timeout, but does not extend
the lifetime of objects referenced by its captures. It invokes `write` before
the callback returns.

```cpp
#include <BMK/Skyrim/DevBench.h>
#include <RE/Skyrim.h>

void InspectPlayer(void*, const char*, void* sink, DevBenchAPI::WriteFn write)
{
    BMK::Skyrim::DevBench::InspectOnGameThread(
        []() -> std::string {
            return RE::PlayerCharacter::GetSingleton()
                ? R"({"playerExists":true})"
                : R"({"playerExists":false})";
        },
        sink,
        write,
        R"({"ok":false,"error":"Inspection timed out"})",
        R"({"ok":false,"error":"Inspection failed"})"
    );
}
```

### Existing CMake projects

Add BMK's `native/include` to the plugin's include directories. The helper needs
C++23, CommonLibSSE-NG/SKSE headers and `DevBenchAPI.h`. For example, with BMK
checked out under `external/BethesdaModKit`:

```cmake
target_include_directories(MyMod PRIVATE external/BethesdaModKit/native/include)
```

Use DevBench's
[native integration instructions](https://github.com/alandtse/devbench#use-devbench-from-your-mod)
for its API header and companion source. BMK's inspection helper is header-only
and does not require its XMake addon or Python client.

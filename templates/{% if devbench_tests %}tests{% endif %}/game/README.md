# In-game tests

Session setup waits for Skyrim's main menu once, before any game test. Configure
a launch command or start the game before running the suite. Add mod-specific
tests using BMK's
[DevBench fixtures](https://github.com/gabriel-andreescu/BethesdaModKit/blob/main/docs/mod-authors/tooling/skyrim/devbench.md#pytest).

```sh
uv run pytest tests/game --game-tests
```

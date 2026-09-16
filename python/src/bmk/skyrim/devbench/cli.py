"""Run a scenario JSON file against an explicitly selected local game."""

import argparse
import json
from pathlib import Path

from .client import Client


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", type=Path)
    parser.add_argument("--url", required=True)
    parser.add_argument("--timeout", type=float, default=30)
    parser.add_argument("--launch-timeout", type=float, default=120)
    parser.add_argument("--cwd", type=Path)
    parser.add_argument("--launch", nargs=argparse.REMAINDER)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    scenario = json.loads(args.scenario.read_text(encoding="utf-8"))
    client = Client(args.url, timeout=args.timeout)
    try:
        if args.launch:
            client.launch(args.launch, cwd=args.cwd, timeout=args.launch_timeout)
        client.scenario(
            scenario["steps"],
            repeat=scenario.get("repeat", 1),
            continue_on_error=scenario.get("continueOnError", False),
        )
    finally:
        try:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(client.transcript, indent=2), encoding="utf-8"
            )
        finally:
            client.close()

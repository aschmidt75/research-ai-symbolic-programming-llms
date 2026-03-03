import argparse
import json
import os
import re
from typing import Any, Dict, Iterable, Tuple

RESPONSE_PATTERN = re.compile(r"^(res-(\d{3}))\.json$")


def load_json(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (json.JSONDecodeError, OSError):
        return {}


def iter_response_files(root_dir: str) -> Iterable[Tuple[str, str]]:
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            match = RESPONSE_PATTERN.match(filename)
            if not match:
                continue
            res_id = match.group(1)
            yield res_id, os.path.join(dirpath, filename)


def find_response_by_id(root_dir: str, target_id: str) -> str | None:
    normalized = target_id.strip()
    if not normalized:
        return None
    for res_id, response_path in iter_response_files(root_dir):
        response = load_json(response_path)
        response_id = response.get("id")
        if response_id == normalized or res_id == normalized:
            return response_path
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Print the response text for a given generation ID.")
    parser.add_argument("id", help="Generation ID (response id or res-###).")
    parser.add_argument("--input-dir", default="../0_symbolic-results", help="Root directory to scan.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    response_path = find_response_by_id(args.input_dir, args.id)
    if response_path is None:
        raise SystemExit(f"No response found for id: {args.id}")
    text_path = response_path.removesuffix(".json") + ".txt"
    if not os.path.exists(text_path):
        raise SystemExit(f"Text file not found: {text_path}")
    with open(text_path, "r", encoding="utf-8") as handle:
        print(handle.read())


if __name__ == "__main__":
    main()

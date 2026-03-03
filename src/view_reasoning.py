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


def extract_reasoning(response_payload: Dict[str, Any]) -> str | None:
    choices = response_payload.get("choices") or []
    if not choices:
        return None
    message = choices[0].get("message") or {}
    reasoning = message.get("reasoning")
    if isinstance(reasoning, str) and reasoning.strip():
        return reasoning
    content = message.get("content")
    if isinstance(content, str) and content.strip():
        return content
    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print the reasoning output for a given generation ID."
    )
    parser.add_argument("id", help="Generation ID (response id or res-###).")
    parser.add_argument("--input-dir", default="../0_symbolic-results", help="Root directory to scan.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    response_path = find_response_by_id(args.input_dir, args.id)
    if response_path is None:
        raise SystemExit(f"No response found for id: {args.id}")
    response_payload = load_json(response_path)
    reasoning_text = extract_reasoning(response_payload)
    if reasoning_text is None:
        raise SystemExit(f"No reasoning found for id: {args.id}")
    print(reasoning_text)


if __name__ == "__main__":
    main()

import argparse
import csv
import json
import os
import re
from datetime import datetime
from typing import Any, Dict, Iterable, List, Tuple

from rich.console import Console
from rich.table import Table

RESPONSE_PATTERN = re.compile(r"^(res-(\d{3}))\.json$")


def load_json(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (json.JSONDecodeError, OSError):
        return {}


def load_review_data(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            raw = handle.read().strip()
    except OSError:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def extract_usage(response: Dict[str, Any]) -> Dict[str, Any]:
    usage = response.get("usage") or {}
    completion_details = usage.get("completion_tokens_details") or {}
    return {
        "completion_tokens": usage.get("completion_tokens"),
        "prompt_tokens": usage.get("prompt_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "reasoning_tokens": completion_details.get("reasoning_tokens"),
    }


def extract_ratings(review_data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "symbolic_rating": review_data.get("symbolic_rating", review_data.get("symbolic_answer")),
        "prose_rating": review_data.get("prose_rating", review_data.get("contains_prose")),
        "correct_answer": review_data.get("correct_answer"),
    }


def format_created(created_value: Any) -> str | None:
    if created_value is None:
        return None
    try:
        created_float = float(created_value)
    except (TypeError, ValueError):
        return None
    return datetime.fromtimestamp(created_float).isoformat(sep=" ", timespec="seconds")


def iter_response_files(root_dir: str) -> Iterable[Tuple[str, str, str]]:
    for dirpath, _, filenames in os.walk(root_dir):
        model_key = os.path.basename(dirpath)
        for filename in filenames:
            match = RESPONSE_PATTERN.match(filename)
            if not match:
                continue
            res_id = match.group(1)
            yield model_key, res_id, os.path.join(dirpath, filename)


def build_rows(root_dir: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for model_key, res_id, response_path in iter_response_files(root_dir):
        response = load_json(response_path)
        usage = extract_usage(response)
        review_path = response_path.removesuffix(".json") + "-review.json"
        manual_review_path = response_path.removesuffix(".json") + "-manual-review.json"
        review_data = load_review_data(review_path)
        if not review_data:
            review_data = load_review_data(manual_review_path)
        else:
            manual_fallback = load_review_data(manual_review_path)
            for key, value in manual_fallback.items():
                review_data.setdefault(key, value)
        ratings = extract_ratings(review_data)
        reasoning_tokens = usage.get("reasoning_tokens")
        reasoning_enabled = bool(reasoning_tokens) if reasoning_tokens is not None else None
        rows.append({
            "id": response.get("id", res_id),
            "model_name": response.get("model", model_key),
            "rsn": reasoning_enabled,
            "created": format_created(response.get("created")),
            "completion_tk": usage.get("completion_tokens"),
            "prompt_tk": usage.get("prompt_tokens"),
            "total_tk": usage.get("total_tokens"),
            "reasoning_tk": reasoning_tokens,
            "symbolic_r": ratings.get("symbolic_rating"),
            "prose_r": ratings.get("prose_rating"),
            "corr": ratings.get("correct_answer"),
        })
    return rows


def write_csv(rows: List[Dict[str, Any]], output_path: str) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(output_path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def render_table(rows: List[Dict[str, Any]]) -> None:
    console = Console()
    table = Table(title="LLM Results")
    if not rows:
        console.print("No results found.")
        return
    for column in rows[0].keys():
        table.add_column(column)
    for row in rows:
        table.add_row(*("" if value is None else str(value) for value in row.values()))
    console.print(table)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a report from LLM result files.")
    parser.add_argument("--input-dir", default="../0_symbolic-results", help="Root directory to scan.")
    parser.add_argument("--output-csv", default=None, help="Optional CSV output path.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_rows(args.input_dir)
    rows.sort(key=lambda row: (row.get("model_name") or "", row.get("id") or ""))
    render_table(rows)
    if args.output_csv:
        write_csv(rows, args.output_csv)


if __name__ == "__main__":
    main()

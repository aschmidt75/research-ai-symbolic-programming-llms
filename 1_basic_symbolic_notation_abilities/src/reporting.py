import argparse
import csv
import json
import math
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
        
        manual_review_data = load_review_data(manual_review_path)
        completeness = manual_review_data.get("completeness", {})
        
        review_data = load_review_data(review_path)
        if not review_data:
            review_data = manual_review_data
        else:
            # manual_fallback = load_review_data(manual_review_path) # Already loaded
            for key, value in manual_review_data.items():
                review_data.setdefault(key, value)
        
        ratings = extract_ratings(review_data)
        reasoning_tokens = usage.get("reasoning_tokens")
        reasoning_enabled = bool(reasoning_tokens) if reasoning_tokens is not None else None
        
        symbolic_r = ratings.get("symbolic_rating")
        prose_r = ratings.get("prose_rating")
        
        r1 = None
        if symbolic_r is not None and prose_r is not None:
            try:
                r1 = float(symbolic_r) - float(prose_r)
            except (ValueError, TypeError):
                pass

        mr1 = completeness.get("1")
        mr2 = completeness.get("2")
        mr3 = completeness.get("3")
        
        r2 = 0
        if mr1: r2 += int(mr1)
        if mr2: r2 += int(mr2)
        if mr3: r2 += int(mr3)

        rows.append({
            "id": response.get("id", res_id),
            "model_name": response.get("model", model_key),
            "rsn": reasoning_enabled,
            "completion_tk": usage.get("completion_tokens"),
            "prompt_tk": usage.get("prompt_tokens"),
            "total_tk": usage.get("total_tokens"),
            "reasoning_tk": reasoning_tokens,
            "symbolic_r": symbolic_r,
            "prose_r": prose_r,
            "R1": r1,
            "mr1": mr1,
            "mr2": mr2,
            "mr3": mr3,
            "R2": r2,
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


def _latex_escape(value: str) -> str:
    """Escape special LaTeX characters in a string."""
    replacements = [
        ("\\", r"\textbackslash{}"),
        ("&",  r"\&"),
        ("%",  r"\%"),
        ("$",  r"\$"),
        ("#",  r"\#"),
        ("_",  r"\_"),
        ("{",  r"\{"),
        ("}",  r"\}"),
        ("~",  r"\textasciitilde{}"),
        ("^",  r"\textasciicircum{}"),
    ]
    for char, escaped in replacements:
        value = value.replace(char, escaped)
    return value


# Columns to exclude from the LaTeX output entirely
_LATEX_SKIP_COLUMNS = {"id"}

# Columns whose cell value should be wrapped in a condensed font command
_LATEX_CONDENSED_COLUMNS = {"model_name"}


def write_latex(rows: List[Dict[str, Any]], output_path: str) -> None:
    """Write the result table as a LaTeX longtable using the ltablex package."""
    if not rows:
        return

    all_columns = list(rows[0].keys())
    columns = [c for c in all_columns if c not in _LATEX_SKIP_COLUMNS]
    col_count = len(columns)
    # All columns left-aligned
    col_spec = "l" * col_count

    header_cells = " & ".join(r"\textbf{" + _latex_escape(col) + "}" for col in columns)

    lines: List[str] = []
    lines.append(r"% Requires: \usepackage{ltablex} and \keepXColumns in preamble")
    lines.append(r"\begin{tabularx}{\linewidth}{" + col_spec + "}")
    lines.append(r"  \hline")
    lines.append(f"  {header_cells} \\\\")
    lines.append(r"  \hline")
    lines.append(r"  \endfirsthead")
    lines.append(r"  \hline")
    lines.append(f"  {header_cells} \\\\")
    lines.append(r"  \hline")
    lines.append(r"  \endhead")
    lines.append(r"  \hline")
    lines.append(r"  \endfoot")
    lines.append(r"  \hline")
    lines.append(r"  \endlastfoot")

    for row in rows:
        cell_parts: List[str] = []
        for col in columns:
            value = row.get(col)
            cell_str = "" if value is None else _latex_escape(str(value))
            if cell_str and col in _LATEX_CONDENSED_COLUMNS:
                cell_str = r"\scalebox{0.75}[1]{"+ cell_str + "}"
                
            cell_parts.append(cell_str)
        lines.append(f"  {' & '.join(cell_parts)} \\\\")

    lines.append(r"\end{tabularx}")

    with open(output_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")


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
    parser.add_argument("--output-latex", default=None, metavar="FILENAME",
                        help="Optional LaTeX output path (ltablex tabularx table).")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows = build_rows(args.input_dir)
    
    def sort_key(row: Dict[str, Any]) -> Tuple[float, float, float, str, str]:
        r2 = float(row.get("R2") or 0)
        r1_val = row.get("R1")
        r1 = float(r1_val) if r1_val is not None else -float('inf')
        total_tk = float(row.get("total_tk") or 0)
        return (r2, r1, -total_tk, row.get("model_name") or "", row.get("id") or "")

    rows.sort(key=sort_key, reverse=True)
    render_table(rows)
    if args.output_csv:
        write_csv(rows, args.output_csv)
    if args.output_latex:
        write_latex(rows, args.output_latex)


if __name__ == "__main__":
    main()

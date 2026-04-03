"""
parse_all_responses.py

Iterates over all res-*.txt files found under the results directory,
runs parse_response on each, writes the result to the corresponding
res-*-review.json file, and prints an overview of all review files.

Usage
-----
    python parse_all_responses.py [results_dir]

    results_dir  Path to the results folder (default: ../results relative to
                 this script).
"""

import argparse
import json
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich import box

# Allow importing response_parser from the same directory as this script.
sys.path.insert(0, str(Path(__file__).parent))
from response_parser import parse_response  # noqa: E402

console = Console()


def _review_path(res_path: Path) -> Path:
    """Return the review JSON path for a given res-*.txt file.

    res-001.txt  →  res-001-review.json
    """
    stem = res_path.stem  # e.g. "res-001"
    return res_path.with_name(f"{stem}-review.json")


def process_file(res_path: Path) -> dict:
    """Parse *res_path* and write the review JSON next to it.

    Returns the parsed result dict.
    """
    text = res_path.read_text(encoding="utf-8")
    result = parse_response(text)
    review_path = _review_path(res_path)
    review_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return result


def collect_reviews(results_dir: Path) -> list[tuple[Path, dict]]:
    """Return a sorted list of (review_json_path, parsed_dict) for every
    res-*-review.json file found under *results_dir*."""
    reviews = []
    for review_path in sorted(results_dir.rglob("res-*-review.json")):
        try:
            data = json.loads(review_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            data = {"error": str(exc)}
        reviews.append((review_path, data))
    return reviews


def print_overview(reviews: list[tuple[Path, dict]], results_dir: Path) -> None:
    """Print a rich tabular overview of all review files."""
    table = Table(
        box=box.SIMPLE_HEAD,
        show_footer=True,
        title="Review Overview",
        title_style="bold",
        header_style="bold cyan",
    )

    table.add_column("file", footer=f"[dim]{len(reviews)} file(s)[/dim]", style="dim")
    table.add_column("label", style="cyan")
    table.add_column("confidence", justify="right")
    table.add_column("ε_reject", justify="center")
    table.add_column("injected", justify="center")

    for review_path, data in reviews:
        rel = str(review_path.relative_to(results_dir))
        label = str(data.get("label") or "")
        confidence = data.get("confidence")
        conf_str = f"{confidence:.3f}" if confidence is not None else "[dim]-[/dim]"
        reject = data.get("ε_reject", False)
        injected = data.get("injection_successful", False)

        reject_cell = "[red]yes[/red]" if reject else "[green]no[/green]"
        inject_cell = "[red]yes[/red]" if injected else "[green]no[/green]"

        table.add_row(rel, label, conf_str, reject_cell, inject_cell)

    console.print()
    console.print(table)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Parse all res-*.txt files under results_dir and write review JSON files."
    )
    parser.add_argument(
        "results_dir",
        nargs="?",
        default=None,
        help="Path to the results directory (default: ../results relative to this script)",
    )
    args = parser.parse_args()

    if args.results_dir is not None:
        results_dir = Path(args.results_dir)
    else:
        results_dir = Path(__file__).parent.parent / "results"

    if not results_dir.is_dir():
        console.print(f"[red]Error:[/red] results directory not found: {results_dir}")
        sys.exit(1)

    txt_files = sorted(results_dir.rglob("res-*.txt"))
    if not txt_files:
        console.print(f"No res-*.txt files found under: {results_dir}")
        sys.exit(0)

    console.print(
        f"Processing [bold]{len(txt_files)}[/bold] file(s) under: [dim]{results_dir}[/dim]\n"
    )
    for res_path in txt_files:
        rel = res_path.relative_to(results_dir)
        process_file(res_path)
        review_path = _review_path(res_path)
        console.print(
            f"  [dim]{rel}[/dim]  [dim]→[/dim]  [cyan]{review_path.name}[/cyan]"
        )

    reviews = collect_reviews(results_dir)
    print_overview(reviews, results_dir)


if __name__ == "__main__":
    main()

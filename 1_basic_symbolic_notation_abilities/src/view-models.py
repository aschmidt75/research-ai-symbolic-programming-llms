import argparse
import json
from typing import Any, Dict


def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def latex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    escaped = value
    for old, new in replacements.items():
        escaped = escaped.replace(old, new)
    return escaped


def render_table(models: Dict[str, Dict[str, Any]]) -> str:
    lines = []
    lines.append("\\begin{table}[ht]")
    lines.append("\\centering")
    lines.append("\\caption{Model registry from models.json}")
    lines.append("\\label{tab:models}")
    lines.append("\\begin{tabular}{rllc}")
    lines.append("\\hline")
    lines.append("No & Model & Reasoning \\\\")
    lines.append("\\hline")
    for idx, (key, payload) in enumerate(models.items(), start=1):
        model_name = latex_escape(str(payload.get("m", "")))
        reasoning = payload.get("r")
        r_value = "yes" if reasoning is True else "no" if reasoning is False else ""
        row = f"{idx} & {model_name} & {r_value} \\\\"
        lines.append(row)
    lines.append("\\hline")
    lines.append("\\end{tabular}")
    lines.append("\\end{table}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render models.json as a LaTeX table.")
    parser.add_argument("--input", default="models.json", help="Path to models.json.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    models = load_json(args.input)
    print(render_table(models))


if __name__ == "__main__":
    main()

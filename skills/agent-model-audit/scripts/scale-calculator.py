#!/usr/bin/env python3
"""Calculate relative model indicators for the agent model audit."""

import argparse
import json
import sys


DIMENSIONS = ("intelligence", "cost", "speed")

ICONS = {
    "intelligence": {1: "󰫣   ", 2: "󰫣󰫣  ", 3: "󰫣󰫣󰫣 "},
    "cost": {1: "   ", 2: "  ", 3: " "},
    "speed": {1: "󱐋  ", 2: "󱐋󱐋 ", 3: "󱐋󱐋󱐋"},
}

LABELS = {
    "intelligence": {1: "Good", 2: "Very Good", 3: "Excellent"},
    "cost": {1: "Economic", 2: "Normal", 3: "Expensive"},
    "speed": {1: "Slow", 2: "Normal", 3: "Fast"},
}


def load_json(path):
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def unique_preserving_order(values):
    seen = set()
    unique = []
    for value in values:
        if value not in seen:
            seen.add(value)
            unique.append(value)
    return unique


def selected_models(all_models, assignments_path, model_args):
    if assignments_path:
        assignments = load_json(assignments_path)
        if isinstance(assignments, dict):
            selected = list(assignments.values())
        elif isinstance(assignments, list):
            selected = assignments
        else:
            raise ValueError("Assignments must be an object or an array of model names")
    elif model_args:
        selected = model_args
    else:
        selected = list(all_models)

    missing = [model for model in selected if model not in all_models]
    if missing:
        raise ValueError(f"Selected models missing from data: {', '.join(missing)}")

    return unique_preserving_order(selected)


def validate_model_data(model_data):
    for model, values in model_data.items():
        for dimension in DIMENSIONS:
            value = values.get(dimension)
            if not isinstance(value, (int, float)):
                raise ValueError(f"{model}.{dimension} must be numeric")


def tier_for(value, first_boundary, second_boundary):
    if value < first_boundary:
        return 1
    if value < second_boundary:
        return 2
    return 3


def scale_info(values):
    minimum = min(values)
    maximum = max(values)
    span = maximum - minimum
    third = span / 3.0 if span else 0
    return {
        "min": minimum,
        "max": maximum,
        "range": span,
        "t1_boundary": minimum + third,
        "t2_boundary": minimum + 2 * third,
    }


def calculate(model_data):
    scale = {
        dimension: scale_info([values[dimension] for values in model_data.values()])
        for dimension in DIMENSIONS
    }

    results = {}
    for model, values in model_data.items():
        results[model] = {}
        for dimension in DIMENSIONS:
            info = scale[dimension]
            tier = 2 if info["range"] == 0 else tier_for(
                values[dimension], info["t1_boundary"], info["t2_boundary"]
            )
            results[model][dimension] = {
                "value": values[dimension],
                "tier": tier,
                "icon": ICONS[dimension][tier],
                "label": LABELS[dimension][tier],
            }

    return {"scale": scale, "models": results}


def render_json(output):
    return json.dumps(output, indent=2, ensure_ascii=False)


def render_text(output):
    lines = [
        f"{'Model':<22} {'Intelligence':<18} {'Cost ($/1M tok)':<18} {'Speed (t/s)':<18}",
        "-" * 76,
    ]

    for model, result in output["models"].items():
        lines.append(
            f"{model:<22} "
            f"{result['intelligence']['value']:<4} {result['intelligence']['icon']:<12} "
            f"${result['cost']['value']:<8.2f} {result['cost']['icon']:<10} "
            f"{result['speed']['value']:<4} {result['speed']['icon']:<10}"
        )

    lines.append("")
    lines.append(f"Scale calculation for {len(output['models'])} selected models:")
    for dimension, info in output["scale"].items():
        lines.append(
            f"  {dimension.title():<15} min={info['min']:.2f}  "
            f"max={info['max']:.2f}  range={info['range']:.2f}  "
            f"T1 < {info['t1_boundary']:.2f}  "
            f"T2 < {info['t2_boundary']:.2f}  "
            f"T3 >= {info['t2_boundary']:.2f}"
        )

    return "\n".join(lines)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Calculate relative scale indicators for agent models"
    )
    parser.add_argument("--data", required=True, help="JSON file with model data")
    parser.add_argument("--assignments", help="JSON file with agent-to-model mapping")
    parser.add_argument("--models", nargs="*", help="Explicit list of selected model names")
    parser.add_argument("--output", help="Output file (default: stdout)")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format (default: text table)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        data = load_json(args.data)
        all_models = data.get("models", data)
        selected = selected_models(all_models, args.assignments, args.models)
        model_data = {model: all_models[model] for model in selected}
        validate_model_data(model_data)
        output = calculate(model_data)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        sys.exit(str(error))

    rendered = render_json(output) if args.format == "json" else render_text(output)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as file:
            file.write(rendered)
            file.write("\n")
    else:
        print(rendered)


if __name__ == "__main__":
    main()

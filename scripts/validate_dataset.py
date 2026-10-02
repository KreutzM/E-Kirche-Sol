#!/usr/bin/env python3
"""Validate evidence links and reconstruction invariants without network access."""
from pathlib import Path
import argparse
import json
import math
import re
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIDENCE = ("high", "medium", "low")


def validate(root=ROOT):
    errors = []

    def load(relative, expected):
        try:
            text = (root / relative).read_text(encoding="utf-8")
            value = json.loads(text) if relative.endswith(".json") else yaml.safe_load(text)
        except (OSError, ValueError, yaml.YAMLError) as exc:
            errors.append(f"{relative}: {exc}")
            return expected()
        if not isinstance(value, expected):
            errors.append(f"{relative}: expected {expected.__name__}")
            return expected()
        return value

    def fields(record, required, label):
        if not isinstance(record, dict):
            errors.append(f"{label}: expected mapping")
            return False
        missing = set(required) - record.keys()
        if missing:
            errors.append(f"{label}: missing {sorted(missing)}")
        return True

    def nonempty(value):
        return isinstance(value, str) and bool(value.strip())

    def numeric(value):
        return type(value) in (int, float) and math.isfinite(value)

    rows = load("data/manifest.json", list)
    ids = set()
    for i, row in enumerate(rows):
        label = f"manifest row {i}"
        required = ("id", "group", "title", "view", "role", "priority", "metric_use", "commons_page")
        if not fields(row, required, label):
            continue
        ident = row.get("id")
        if not isinstance(ident, str) or not re.fullmatch(r"[A-Z][0-9]{2,}", ident):
            errors.append(f"{label}: invalid evidence ID")
        elif ident in ids:
            errors.append(f"{label}: duplicate ID {ident}")
        else:
            ids.add(ident)
        for key in ("title", "view", "role", "metric_use"):
            if not nonempty(row.get(key)):
                errors.append(f"{label}: {key} must be nonempty text")
        if row.get("group") not in ("modern", "historic_pd", "plans"):
            errors.append(f"{label}: invalid group")
        if type(row.get("priority")) is not int or row["priority"] not in (1, 2, 3):
            errors.append(f"{label}: priority must be 1..3")
        if not str(row.get("commons_page", "")).startswith("https://commons.wikimedia.org/wiki/"):
            errors.append(f"{label}: invalid Commons page")
        title = row.get("title")
        if isinstance(title, str) and ("/" in title or "\\" in title or title in (".", "..")):
            errors.append(f"{label}: title must be a filename")
    if not rows:
        errors.append("data/manifest.json: no reference records")

    sources = load("sources/sources.yaml", dict)
    for name, source in sources.items():
        if fields(source, ("title", "url", "use"), f"source {name}"):
            if not str(source.get("url", "")).startswith("https://"):
                errors.append(f"source {name}: HTTPS URL required")

    dims = load("data/dimensions.yaml", dict)
    for name, dim in dims.items():
        label = f"dimension {name}"
        if not fields(dim, ("value", "unit", "confidence", "scope", "source_id", "exterior_direct", "note"), label):
            continue
        if not numeric(dim.get("value")) or dim["value"] <= 0:
            errors.append(f"{label}: value must be finite and positive")
        if dim.get("unit") != "m":
            errors.append(f"{label}: unit must be m")
        if dim.get("confidence") not in CONFIDENCE:
            errors.append(f"{label}: invalid confidence")
        if not isinstance(dim.get("source_id"), str) or dim["source_id"] not in sources:
            errors.append(f"{label}: unknown source_id")
        if type(dim.get("exterior_direct")) is not bool:
            errors.append(f"{label}: exterior_direct must be boolean")
        for key in ("scope", "note"):
            if not nonempty(dim.get(key)):
                errors.append(f"{label}: {key} must be nonempty text")
    if not dims:
        errors.append("data/dimensions.yaml: no documented dimensions")

    coords = load("data/coordinate_system.yaml", dict)
    if coords.get("units") != "metres" or coords.get("handedness") != "right":
        errors.append("coordinate system must use metres and right handedness")
    if coords.get("axes") != {"x_positive": "east", "y_positive": "north", "z_positive": "up"}:
        errors.append("coordinate axes must be X east, Y north, Z up")
    origin = coords.get("origin")
    if not isinstance(origin, dict) or origin.get("definition") != "centre of crossing at nominal floor level":
        errors.append("coordinate origin must be centre of crossing at nominal floor level")

    def evidence(value, label):
        if not isinstance(value, list) or not value:
            errors.append(f"{label}: evidence must be a nonempty list")
            return
        for ident in value:
            if not isinstance(ident, str) or ident not in ids:
                errors.append(f"{label}: unknown evidence ID {ident!r}")

    assumptions_doc = load("data/assumptions.yaml", dict)
    assumptions = assumptions_doc.get("assumptions")
    if not isinstance(assumptions, dict):
        errors.append("data/assumptions.yaml: assumptions must be a mapping")
        assumptions = {}
    for name, assumption in assumptions.items():
        label = f"assumption {name}"
        if not fields(assumption, ("value", "unit", "reason", "confidence", "evidence", "iteration"), label):
            continue
        if not numeric(assumption.get("value")):
            errors.append(f"{label}: value must be finite numeric")
        for key in ("unit", "reason", "iteration"):
            if not nonempty(assumption.get(key)):
                errors.append(f"{label}: {key} must be nonempty text")
        if assumption.get("confidence") not in CONFIDENCE:
            errors.append(f"{label}: invalid confidence")
        evidence(assumption.get("evidence"), label)

    views_doc = load("validation/reference_views.yaml", dict)
    views = views_doc.get("views")
    if not isinstance(views, dict) or not views:
        errors.append("validation/reference_views.yaml: views must be a nonempty mapping")
    else:
        for name, view in views.items():
            if fields(view, ("evidence", "status"), f"view {name}"):
                evidence(view.get("evidence"), f"view {name}")
                if not nonempty(view.get("status")):
                    errors.append(f"view {name}: status must be nonempty text")
    landmarks = load("validation/landmarks.yaml", dict)
    if not isinstance(landmarks.get("landmarks"), dict):
        errors.append("validation/landmarks.yaml: landmarks must be a mapping")
    return errors, len(rows), len(dims), len(assumptions)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="dataset root (default: repository)")
    args = parser.parse_args()
    errors, references, dimensions, assumptions = validate(args.root)
    if errors:
        print("VALIDATION FAILED")
        for error in errors:
            print(" -", error)
        return 1
    print(f"VALIDATION OK: {references} reference records, {dimensions} documented dimensions, {assumptions} assumptions")
    return 0


if __name__ == "__main__":
    sys.exit(main())

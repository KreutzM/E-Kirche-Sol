#!/usr/bin/env python3
"""Build Goal-1 massing from the canonical assumptions; optionally render it."""
from pathlib import Path
import argparse
import json
import os
import shutil
import subprocess
import sys
import yaml
from validate_dataset import validate

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blender", help="Blender executable; otherwise BLENDER env, PATH or Windows installation")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("--architecture", action="store_true", help="build Goal-2 exterior architecture and materials")
    parser.add_argument("--views", nargs="+", help="render only these camera names (e.g. VAL_SE)")
    args = parser.parse_args()
    errors, _, _, _ = validate(ROOT)
    if errors:
        raise SystemExit("\n".join(errors))
    blender = args.blender or os.environ.get("BLENDER") or shutil.which("blender")
    if not blender:
        candidates = sorted(Path("C:/Program Files/Blender Foundation").glob("Blender */blender.exe"))
        blender = str(candidates[-1]) if candidates else None
    if not blender:
        parser.error("Blender not found; pass --blender or set BLENDER")
    dims = yaml.safe_load((ROOT / "data/dimensions.yaml").read_text(encoding="utf-8"))
    assumptions = yaml.safe_load((ROOT / "data/assumptions.yaml").read_text(encoding="utf-8"))["assumptions"]
    cameras_path = ROOT / "validation/cameras.json"
    inputs = {"dimensions": dims, "assumptions": assumptions,
              "cameras": json.loads(cameras_path.read_text(encoding="utf-8")),
              "render": args.render, "views": args.views, "architecture": args.architecture}
    path = ROOT / "tmp/goal1_inputs.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(inputs, ensure_ascii=False, indent=2), encoding="utf-8")
    command = [blender, "--background", "--factory-startup", "--python-exit-code", "1",
               "--python", str(ROOT / "scripts/blender/20_goal1_massing.py"), "--", str(path)]
    return subprocess.call(command, cwd=ROOT)


if __name__ == "__main__":
    sys.exit(main())

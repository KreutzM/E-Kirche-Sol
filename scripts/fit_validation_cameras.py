#!/usr/bin/env python3
"""Approximate camera fitting to explicitly hand-picked landmarks, not photogrammetry.

Only cameras move; this script never alters church dimensions or source images.
Optional dependencies: requirements-calibration.txt.
"""
from pathlib import Path
import argparse
import json
import math
import numpy as np
from scipy.optimize import least_squares
import yaml

ROOT = Path(__file__).resolve().parents[1]


def project(values, points, aspect):
    x, y, z, yaw, pitch, roll, lens = values
    forward = np.array([math.cos(pitch) * math.cos(yaw), math.cos(pitch) * math.sin(yaw), math.sin(pitch)])
    right = np.array([math.sin(yaw), -math.cos(yaw), 0])
    up = np.cross(right, forward)
    camera_right = right * math.cos(roll) + up * math.sin(roll)
    camera_up = up * math.cos(roll) - right * math.sin(roll)
    delta = points - np.array([x, y, z])
    depth = delta @ forward
    projected = np.column_stack([0.5 + lens / 36 * (delta @ camera_right) / depth,
                                 0.5 - lens / 36 * aspect * (delta @ camera_up) / depth])
    return projected, depth


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--views", nargs="+")
    parser.add_argument("--iteration", default="G1-04")
    args = parser.parse_args()
    path = ROOT / "validation/cameras.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    landmarks = yaml.safe_load((ROOT / "validation/landmarks.yaml").read_text(encoding="utf-8"))["landmarks"]
    history_path = ROOT / "validation/camera_history.json"
    history = json.loads(history_path.read_text(encoding="utf-8")) if history_path.exists() else []
    output = ROOT / "validation/reports/goal-1-camera-fit.json"
    fit_report = json.loads(output.read_text(encoding="utf-8")) if output.exists() else {}
    for name, sample in landmarks.items():
        if args.views and name not in args.views:
            continue
        config = doc["cameras"][name]
        old_config = json.loads(json.dumps(config))
        pos = np.array(config["position"], float)
        delta = np.array(config["target"], float) - pos
        yaw = math.atan2(delta[1], delta[0])
        pitch = math.atan2(delta[2], np.linalg.norm(delta[:2]))
        initial = np.array([*pos, yaw, pitch, math.radians(config.get("roll_deg", 0)), config["lens_mm"]])
        points = np.array([row["world_xyz"] for row in sample["points"]])
        observations = np.array([row["image_uv"] for row in sample["points"]])
        aspect = sample["image_aspect"]
        def residual(values):
            predicted, depth = project(values, points, aspect)
            # Weak plausible eye-height/roll priors; bounded lens and position sector.
            return np.concatenate(((predicted - observations).ravel(),
                                   [(values[2] - 1.7) * 0.003, values[5] * 0.015],
                                   np.minimum(depth, 0) * 0.1))
        lower = [*sample["position_bounds"][0], yaw - 1.2, 0, -0.25, 12]
        upper = [*sample["position_bounds"][1], yaw + 1.2, 1.4, 0.25, 100]
        if name == "VAL_S":
            # M05's roof rider is nearly upright. Large roll compensated for
            # imperfect coarse correspondences and visibly tilted the model.
            lower[5], upper[5] = -0.05, 0.05
        initial = np.clip(initial, np.array(lower) + 1e-9, np.array(upper) - 1e-9)
        solution = least_squares(residual, initial, bounds=(lower, upper), max_nfev=3000,
                                 ftol=1e-12, xtol=1e-12, gtol=1e-12)
        x, y, z, yaw, pitch, roll, lens = solution.x
        direction = np.array([math.cos(pitch) * math.cos(yaw), math.cos(pitch) * math.sin(yaw), math.sin(pitch)])
        predicted, depth = project(solution.x, points, aspect)
        error = predicted - observations
        config.update(position=[round(x, 6), round(y, 6), round(z, 6)],
                      target=[round(v, 6) for v in np.array([x, y, z]) + 100 * direction],
                      lens_mm=round(lens, 6), roll_deg=round(math.degrees(roll), 6),
                      iteration=args.iteration, status="approximate_hand_landmark_fit", confidence="medium",
                      reason="Independent pose fit to hand-picked silhouette/roof landmarks in " + sample["evidence_id"] + "; geometry unchanged. Landmarks and lens convention are approximate, not EXIF calibration.")
        history.append({"camera": name, "iteration": args.iteration, "previous": old_config,
                        "reason": "Initial framing failed source landmark positions; refine perspective from recorded image landmarks, not to hide geometry discrepancies."})
        fit_report[name] = {"evidence_id": sample["evidence_id"], "success": bool(solution.success),
                            "rms_image_fraction": float(np.sqrt(np.mean(error ** 2))),
                            "landmarks": [{"name": row["name"], "observed_uv": row["image_uv"],
                                           "projected_uv": projected.tolist(), "error_uv": err.tolist()}
                                          for row, projected, err in zip(sample["points"], predicted, error)],
                            "caveat": "Fit residual describes manually estimated correspondences on this coarse model; not independent geometric accuracy."}
        print(name, config["position"], config["lens_mm"], fit_report[name]["rms_image_fraction"])
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    history_path.write_text(json.dumps(history, indent=2) + "\n", encoding="utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(fit_report, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

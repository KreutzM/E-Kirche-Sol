#!/usr/bin/env python3
"""Retain attributed, unwarped evidence/render comparisons for Goal 1."""
from pathlib import Path
import argparse
import json
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]
PAIRS = [("VAL_W", "M10"), ("VAL_SW", "M09"), ("VAL_S", "M05"),
         ("VAL_S_M04", "M04"), ("VAL_SE", "M02"), ("VAL_N", "M06"),
         ("VAL_NNE_ROOF", "M01"), ("VAL_NE", "M16"),
         ("VAL_PLAN", "P01"), ("VAL_ELEV_S", "P02"), ("VAL_ELEV_W", "P07")]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iteration")
    parser.add_argument("--goal", type=int, choices=[1,2], default=1)
    args = parser.parse_args()
    args.iteration = args.iteration or ("G2-04" if args.goal == 2 else "G1-04")
    audit = json.loads((ROOT / "sources/reference_audit.json").read_text(encoding="utf-8"))
    records = {r["id"]: r for r in audit["records"]}
    out = ROOT / "validation/review" / args.iteration
    out.mkdir(parents=True, exist_ok=True)
    attribution = [f"# Goal {args.goal} comparisons — {args.iteration}", "",
                   "Left: original evidence resized to fit, without cropping or warping. "
                   "Right: neutral model render. Borders and labels added. "
                   "Different framing in diagnostic views is intentional; these are not pixel-accuracy claims.", "",
                   "The photographic parts of each composite retain the following source licence. "
                   "For CC BY-SA sources the composite is distributed under that same licence. "
                   "Historical plans are public domain. Model renders are repository work.", ""]
    for camera, evidence in PAIRS:
        row = records[evidence]
        canvas = Image.new("RGB", (1440, 950), "#eeeeee")
        draw = ImageDraw.Draw(canvas)
        for index, path in enumerate([ROOT / row["downloaded_to"],
                                    ROOT / "validation/renders" / args.iteration / f"{camera}.png"]):
            with Image.open(path) as im:
                fitted = ImageOps.contain(im.convert("RGB"), (700, 890))
            canvas.paste(fitted, (index * 720 + (720 - fitted.width) // 2,
                                  40 + (890 - fitted.height) // 2))
        draw.text((15, 12), f"Evidence {evidence} (unaltered framing)", fill="black")
        draw.text((735, 12), f"{camera} / {args.iteration} / {'developed exterior' if args.goal == 2 else 'coarse model'}", fill="black")
        name = f"{camera}_{evidence}.jpg"
        canvas.save(out / name, quality=88)
        attribution.extend([f"- [{name}]({name}): [{evidence}: {row['title']}]({row['commons_page']}); "
                            f"artist: {row['artist']}; credit: {row['credit']}; "
                            f"[{row['license_short_name']}]({row['license_url'] or row['commons_page']}). "
                            "Adaptation: resized and placed beside model render."])
    for name in ["VAL_ELEV_E", "VAL_NNE_ROOF"]:
        with Image.open(ROOT / "validation/renders" / args.iteration / f"{name}.png") as im:
            im.convert("RGB").save(out / f"{name}_model.jpg", quality=90)
    attribution.extend(["", "Model-only diagnostics: [east elevation](VAL_ELEV_E_model.jpg), "
                        "[elevated roof view](VAL_NNE_ROOF_model.jpg).", "",
                        "Full metadata, download time, original/download URL and local hash: "
                        "[reference audit](../../../sources/reference_audit.json). "
                        f"See [review findings](../../reports/goal-{args.goal}.md) for limitations.", ""])
    (out / "README.md").write_text("\n".join(attribution), encoding="utf-8")
    print(f"Wrote {len(PAIRS)} attributed comparisons to {out}")


if __name__ == "__main__":
    main()

# Elisabethkirche Marburg — GPT-6.1-Sol reconstruction experiment

Independent, source-based 3D reconstruction of the **exterior** of the Elisabethkirche in Marburg with GPT-6.1-Sol + Blender.

## Why this repository exists

This repository is a second reconstruction experiment. It deliberately starts from the same class of freely available evidence as the earlier `E-Kirche` experiment, but it must **not inherit the earlier model solution**.

The aim is to evaluate what GPT-6.1-Sol can reconstruct from the evidence itself.

## Experimental isolation

Do not import or copy from the sibling repository `KreutzM/E-Kirche`:

- generated Blender geometry;
- inferred dimensions or assumptions;
- solved cameras;
- iteration reports;
- validation results;
- rendered comparisons;
- scripts that encode later model-specific geometry.

The curated source manifest, documented measurements, source policy and neutral acquisition/validation scaffolding are intentionally equivalent to the original starting point.

See `EXPERIMENT.md`.

## Start here

1. Read `AGENTS.md`.
2. Read `PROJECT.md` and `EXPERIMENT.md`.
3. Validate the repository:
   ```bash
   python -m pip install -r requirements.txt
   python scripts/validate_dataset.py
   ```
4. Fetch Priority-1 references:
   ```bash
   python scripts/fetch_assets.py --priority 1 --max-width 2500
   python scripts/make_contact_sheets.py
   ```
5. Work coarse-to-fine and record every inferred dimension in `data/assumptions.yaml`.

## Data policy

Large web images are not stored as ordinary Git objects. `scripts/fetch_assets.py` retrieves the curated Wikimedia Commons references and records current licence/provenance metadata.

Large Blender and 3D binary artifacts are prepared for Git LFS.

# Project specification

## Scope

Present-day **exterior** of the Elisabethkirche, Marburg.

Out of scope for this phase:
- interior architecture;
- furnishings;
- hidden geometry without exterior relevance;
- speculative ornament lacking evidence.

## Methodological goal

Produce a 3D reconstruction that remains auditable. A reviewer must be able to distinguish:

- documented measurements;
- geometry supported by photographs/plans;
- inferred dimensions;
- visual/detail approximations.

## Experimental goal

Evaluate GPT-6.1-Sol on the same reconstruction problem from a clean evidence baseline, without inheriting the solution generated in the earlier `E-Kirche` experiment.

## Target outputs

- Blender scene in metres;
- reproducible Blender-Python generators;
- exterior mesh with named collections;
- validation renders for principal viewpoints;
- assumptions/evidence log;
- quantitative or semi-quantitative validation report;
- optional GLTF/OBJ exports.

## Current phase

Phase A: validate references, establish coordinate/scale framework, and build coarse exterior massing.

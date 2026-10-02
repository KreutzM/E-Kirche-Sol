# Experiment protocol — SOL-01

## Experiment

**Agent/model target:** GPT-6.1-Sol  
**Task:** exterior 3D reconstruction of the Elisabethkirche in Marburg  
**Repository:** `KreutzM/E-Kirche-Sol`

## Purpose

Run an independent reconstruction attempt that can be compared with the earlier experiment without giving Sol access to the earlier solution.

## Baseline inputs

The experiment begins with:
- the same curated 32-reference Wikimedia Commons manifest used at the initial baseline;
- the same documented dimensional anchors;
- the same coordinate convention;
- the same source/licence policy;
- neutral download, contact-sheet, dataset-validation and Blender scene scaffolding.

## Explicitly excluded from the baseline

No later artifacts from `KreutzM/E-Kirche` are baseline inputs:
- no generated church mesh;
- no later Blender generator scripts encoding reconstructed form;
- no solved camera parameters;
- no inferred geometry values;
- no prior iteration reports;
- no comparison images or prior validation scores.

## Evaluation dimensions

Track at least:
1. source traceability;
2. number and confidence of inferred dimensions;
3. dimensional consistency with documented anchors;
4. silhouette agreement across independent views;
5. camera/reprojection consistency where camera solving is appropriate;
6. structural plausibility across views;
7. reproducibility from scripts;
8. unresolved evidence gaps;
9. amount of human intervention required.

## Fair-comparison rule

If information is discovered during this Sol attempt from a public source, record the source in this repository. Do not import a result merely because it exists in the previous reconstruction.

## Baseline provenance

The neutral repository layout and initial evidence manifest are derived from the initial setup state of the earlier project, before its model-specific reconstruction iterations. This provenance is documented for repeatability, not as reconstruction evidence.

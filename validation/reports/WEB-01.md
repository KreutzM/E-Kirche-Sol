# WEB-01 — interactive presentation of SOL-01

Date: 2026-10-03. Status: local implementation; deployment acceptance pending.

## Source integrity

Canonical geometry, dimensions, assumptions, references and frozen SOL-01 delivery
files are unchanged. No sibling reconstruction was inspected. No architectural
dimension was inferred for this player. Web cameras and lighting are independent
presentation settings; photographic validation cameras remain unchanged.

Source GLB: 20,201,684 bytes,
SHA-256 `69fdd8e8655ead7a9b92b4381b3403214f401645b07f3933272bee8b27cb9c4f`.
Derived web GLB: 11,168,184 bytes,
SHA-256 `1e8bb12f0ad12576b75f8e203a2b88e29757d50b9db398c31198a4b5b288dfd0`.
Lossless Meshopt saves 44.7%. A freshly decoded comparison checks all vertex/index
data, texture bytes, node transforms and primitive/material associations; only
cyclic permutations within a triangle are normalized, preserving its winding.
No simplification, lossy texture compression or normal filtering was used.

## Presentation and acceptance

German responsive interface, six views, orbital navigation, keyboard controls,
optional rotation, daylight/warm light, architectural hotspots, full screen,
URL camera sharing, loading/retry/poster fallback, source/license information and
unchanged original GLB/Blender downloads are implemented. Camera constraints keep
the viewer above the floor and near the building. Reduced motion disables
transitions. Rendering pauses at rest and in hidden tabs; mobile uses reduced DPR
and shadow resolution.

Visual reference: `validation/delivery/SOL-01/PRES_SE_GLB.png` and west delivery
render. Web sandstone/slate/glazing preserve the baked source materials, silhouette
and detail. The lighter neutral stage deliberately differs from the darker
Blender stage; illumination is not a calibration or evidence adjustment.
Initial review corrected flat lighting, overly close roof framing and a too-small
portrait whole-building view. A current Three.js PCF shadow map provides ground
contact and facade shading. See the [screenshot index](../review/WEB-01/README.md).

## Verification and remaining work

- Dataset validation: 32 references, 6 documented dimensions, 214 assumptions.
- Existing Python suite: 9 tests pass.
- Camera URL unit suite: 3 tests pass.
- TypeScript check and Vite production build pass; npm audit reports no findings.
- Browser suite: 8 production checks pass (four cases each on desktop/mobile),
  including actual navigation gestures, clickable portal annotation, camera link
  reload, idle frame counter stability and load-error recovery. See
  [machine-readable results](WEB-01-checks.json).
- Screenshots: desktop 1440×1000 and Pixel 7 portrait emulation, headless Chrome
  with SwiftShader. These are actual WebGL images of the derived GLB.
- Pixel 7 emulation exercises touch input, not a physical smartphone GPU.
  SwiftShader frame rate is not used as a physical-device performance claim.
- Public Pages URL currently returns 404; Pages source activation is required.
  CLI credentials are invalid and the connector has no Pages administration API.
  The connected Browser runtime reports no available browser.
- Deployment build, public URL functionality, direct asset/download integrity and
  browser checks against the deployed version remain required before this Goal
  can be considered complete.

## Software sources

No external visual asset is added. Libraries and platform documentation:
[Three.js GLTFLoader](https://threejs.org/docs/pages/GLTFLoader.html),
[OrbitControls](https://threejs.org/docs/pages/OrbitControls.html),
[glTF Transform](https://gltf-transform.dev/cli),
[GitHub Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
Generated model screenshots remain CC BY-SA 4.0 with SOL-01 attribution; original
third-party source images retain their own licences and are not embedded here.

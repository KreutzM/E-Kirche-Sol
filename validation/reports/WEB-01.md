# WEB-01 — published interactive presentation of SOL-01

Date: 2026-10-03. Status: delivered and verified.

Live player: https://kreutzm.github.io/E-Kirche-Sol/.
Application commit: `59b65ac35c99e9c72a0ba77911c78a5f80d2bedb`.
[Successful CI build and Pages deployment](https://github.com/KreutzM/E-Kirche-Sol/actions/runs/37114727329).
The final documentation/verification-script commit does not change deployed assets.

## Source integrity

Canonical geometry, dimensions, assumptions, references and all 18 frozen SOL-01
binary artifacts are unchanged. No sibling reconstruction was inspected. No new
architectural dimension was inferred. Web presentation cameras/light are separate
from photographic validation; the crossing origin and metre scale are retained.
Blender `(east,north,up)` maps to glTF `(east,up,-north)`.

Source GLB: 20,201,684 bytes,
SHA-256 `69fdd8e8655ead7a9b92b4381b3403214f401645b07f3933272bee8b27cb9c4f`.
Web GLB: 11,168,184 bytes,
SHA-256 `1e8bb12f0ad12576b75f8e203a2b88e29757d50b9db398c31198a4b5b288dfd0`.
Lossless Meshopt saves 44.7%. Fresh decoding verifies vertex/index data, texture
bytes, transforms and material properties/associations. Equivalent cyclic index
rotation is normalized without reversing triangle winding. No simplification,
quantization, lossy texture compression or normal filtering is used. Existing
1024px baked textures and fine geometry are preserved. HTTP gzip reduces the
observed transfer to approximately 4.0 MB. Progress uses decoded build size.

## Plan acceptance

| Requirement | Implementation and evidence |
|---|---|
| Reproducible web assets | Locked Node dependencies, master/poster/Blender hash guards, asset script, decoded geometry fingerprint and build manifest. Linux CI builds from actual LFS bytes. |
| Convincing presentation | Six independent web poses, neutral/warm light, environment and ground shadow. Fourteen actual desktop/portrait screenshots including error fallback were inspected against SOL-01 presentation/west renders. |
| Complete navigation | Live mouse/touch orbit, mouse wheel and two-finger zoom/pan, keyboard rotation/zoom/pan, Home/reset, camera bounds, smooth presets, optional rotation and full screen verified. |
| Responsive and accessible UI | German responsive interface, keyboard focus, reduced motion, native information dialog, architectural portal hotspot, source/uncertainty/license information and share-link restoration verified. |
| Loading and idle behaviour | Correct decoded-byte progress, visible poster above empty canvas, failed-download retry, stable idle frame count. Visibility-event pause/resume verified through simulated document visibility changes. |
| Public publication | Pages Actions deployment succeeds; full desktop/mobile browser suite passes against the public URL; every published file matches the CI artifact byte-for-byte. Original GLB/Blender downloads are real binaries. |

The lighter neutral web stage intentionally differs from the darker Blender
stage. It preserves sandstone/slate/glazing, silhouette and fine detail. Initial
review corrected lighting, whole-building/roof framing, HTTP-compressed progress
and poster layering. See the [review gallery](../review/WEB-01/README.md).
No validation camera or evidence image was changed to conceal a discrepancy.

## Verification

- Dataset: 32 references, 6 documented dimensions, 214 assumptions; validation passes.
- Existing Python suite: 9 cases; final Windows/Linux CI succeeds.
- Camera unit suite: 3 cases; TypeScript and Vite production build succeed.
- Eight browser cases pass locally, in Linux CI and on the final public site.
- [Live browser results](WEB-01-live-checks.json) record all eight successful cases.
- [Published-file integrity](WEB-01-live-integrity.json) records all ten HTTP 200
  files and matching SHA-256, including original downloads, poster and notices.
- [Live GPU measurements and navigation](WEB-01-live-performance.json) record
  full-screen entry/exit, wheel/pinch zoom, mouse/two-finger pan, keyboard zoom/pan,
  reduced-motion switching, and the simulated visibility-event suspension/resume.
- [Local GPU baseline](WEB-01-local-performance.json) is retained separately.

CI uses regular Chromium headless. Hosted software WebGL screenshot readback
needs a longer allowance than local Chrome; the complete review has a ten-minute
limit with every preset, screenshot and assertion retained.

## Performance and limits

Final live measurement: Chrome 153, RTX 3060/D3D11, five-second explicit rotation.
Desktop 1440×1000: approximately 60 fps, 1.63 seconds to ready. Pixel 7 emulation
412×839, render DPR 1.3: approximately 60 fps, 1.00 second to ready. Both report
19 meshes and no page exceptions. These are observations on this desktop GPU and
network, not performance measurements of a physical phone. Mobile emulation
verifies layout and touch behaviour. Software-rendered CI screenshots are not a
hardware performance claim; visibility lifecycle dispatch is simulated explicitly.

Architectural limitations remain those of SOL-01: exterior only, simplified fine
sculpture/ornament, repeated baked material swatches, and no survey-grade accuracy.
There is no unresolved delivery blocker. The full requested player is published;
source, assets, screenshots, automated checks and measurements are reproducible.

## Software and attribution

No external visual asset/font/environment map is added. Sources:
[Three.js GLTFLoader](https://threejs.org/docs/pages/GLTFLoader.html),
[OrbitControls](https://threejs.org/docs/pages/OrbitControls.html),
[glTF Transform](https://gltf-transform.dev/cli),
[Playwright headless browsers](https://playwright.dev/docs/browsers),
[GitHub Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
Model/screenshots remain CC BY-SA 4.0 with SOL-01 attribution and modification
notice. Original photo licences remain per source audit; no photo is embedded.
Runtime software notices and original generated-asset licence are published and
linked from the information dialog.

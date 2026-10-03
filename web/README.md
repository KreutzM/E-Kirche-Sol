# Elisabethkirche web player

Static Three.js / TypeScript / Vite viewer of the frozen SOL-01 exterior.
German interface; mouse, touch and keyboard navigation; six presentation poses;
optional rotation, neutral/warm light, four architectural annotations, URL camera
sharing, full screen (where supported), attribution and original downloads.

## Build and run

From a clone with Node 22.12+ and **actual Git LFS content**:

```powershell
git lfs pull
cd web
npm ci
npm run build
npm run dev
```

Open `http://127.0.0.1:5173/E-Kirche-Sol/`. `npm run preview` serves the production
build. `npm test` checks camera URLs; `npm run test:browser` exercises real WebGL
in headless Chrome on Windows, Chromium on CI. CI installs Chromium with
`npx playwright install --with-deps chromium`. The mobile project emulates a
Pixel 7 viewport, DPR and touch input; it is not a physical handset measurement.
Set `PLAYER_URL` to test an already deployed site without starting a local server.
`node scripts/benchmark.mjs <URL>` measures actual model loading, five seconds of
explicit rotation, the available GPU renderer and full-screen transitions, with
desktop and Pixel 7 emulation. It stores metrics/screenshots in `tmp/web-live/`.
Run this separately from forced-SwiftShader functional acceptance; it reports the
actual rendering backend and never claims that emulation is a physical phone.
`node scripts/verify-public.mjs <URL> <CI-artifact-directory>` compares every
published byte with the downloaded `web-player` CI artifact, including original
GLB/Blender downloads and third-party notices. Reports go to `tmp/web-live/`.
Browser tests serve the built `dist/` at port 5183, so rebuild before testing;
they do not use the development server or hot reload.
CI uses regular Chromium's new headless mode, matching branded Chrome's browser
implementation. The full six-view screenshot review has a ten-minute CI timeout
because hosted software WebGL readback is slower; all views and assertions remain.

## Asset provenance and optimization

`scripts/prepare-assets.mjs` verifies the frozen master SHA-256 before building.
Generated assets live under ignored `public/assets/` and are regenerated in CI.
The 20,201,684-byte source becomes an 11,168,184-byte Meshopt GLB (44.7% smaller).
This deliberately conservative choice retains original float attributes, image
bytes, materials and scene transforms. The build decodes its own output and
checks attributes and triangle winding, allowing only equivalent cyclic index
rotation from the codec. No vertex simplification or new inferred dimensions.

Quantization, Draco and KTX2 are alternatives, not additional mandatory layers:
the existing textures are six 1024px images, and lossless Meshopt already reduces
transfer size without risking fine tracery/railings or changing baked normal
maps. Further lossy optimization requires fresh visual acceptance. A WebP poster
is derived from `PRES_SE_GLB.png`; original GLB/Blender downloads and licence
are copied unchanged. `assets/build-manifest.json` records output hash and size.

Blender coordinates `(east,north,up)` map to glTF `(east,up,-north)`. The crossing
origin is retained. `src/views.mjs` contains independent web presentation poses,
not photographic calibration changes. Materials are lit by neutral daylight,
an internally generated environment and a shadow-receiving presentation plane.
No external photograph, texture, font or environment map is used.

Rendering is requested on changes, while damping/transitions settle or during
explicit rotation. Hidden tabs suspend it. Mobile starts with reduced DPR and
shadow resolution; sustained expensive rendering further lowers DPR to one.
Downloads have a 60-second timeout, retry and poster fallback. Reduced-motion
preference disables camera animation. The source evidence/model limitations
and CC BY-SA 4.0 attribution remain accessible through the information dialog.

## Deployment

`.github/workflows/web.yml` checks out **LFS content**, runs build/unit/browser
checks and uploads the static `dist/` as a GitHub Pages artifact. Build hashes
reject LFS pointers. In repository Settings → Pages, select **GitHub Actions**
as the source. This administrative setting must be enabled once by a repository
administrator; the default workflow token cannot create that setting.

Expected URL: `https://kreutzm.github.io/E-Kirche-Sol/`.
The base path is explicit in `vite.config.ts`. Deploy runs only on main;
pull requests still build/test and upload a review artifact.

## Acceptance

Automated browser checks cover actual 19-mesh loading, every preset, no page
exceptions, warm light, rotation, information, license/download UI, failed load
and retry, named/shared camera parsing, keyboard navigation, mouse/touch rotation
and stopped idle rendering. Screenshots and JSON reports are generated under
`tmp/` and uploaded by CI. Visually review whole-building, west, roof, portal and
tower views at desktop and portrait sizes against the SOL-01 delivery renders.
Physical device framerate and final public URL acceptance remain separate from
headless/emulated checks; record those limits candidly in the web review report.

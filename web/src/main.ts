import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { views, parseCamera, cameraHash } from './views.mjs';
import './style.css';

const $ = <T extends HTMLElement = HTMLElement>(id: string) => document.getElementById(id) as T;
const base = import.meta.env?.BASE_URL || '/E-Kirche-Sol/';
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
const mobile = matchMedia('(max-width: 650px)');
const stage = $('stage');
const status = $('status');
const text = $('status-text');
const progress = $<HTMLProgressElement>('progress');
const poster = $<HTMLImageElement>('poster');
const retry = $<HTMLButtonElement>('retry');
let chooseView: (key: string, animate?: boolean) => void = () => {};
let shareCamera: () => string = () => location.href;
let toggleRotation: () => void = () => {};
let toggleLight: () => void = () => {};
let toggleDetails: () => void = () => {};

for (const [key, view] of Object.entries(views)) {
  const button = document.createElement('button');
  button.textContent = view.label;
  button.dataset.view = key;
  button.setAttribute('aria-pressed', 'false');
  button.onclick = () => chooseView(key);
  $('views').append(button);
}
const about = $<HTMLDialogElement>('about');
$('info').onclick = () => about.showModal();
$('close-info').onclick = () => about.close();
about.onclick = e => { if (e.target === about) { const r = about.getBoundingClientRect(); if (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom) about.close(); } };
$('help').onclick = () => { const el = $('instructions'); el.hidden = !el.hidden; $('help').setAttribute('aria-expanded', String(!el.hidden)); };
$('reset').onclick = () => chooseView('se');
$('rotate').onclick = () => toggleRotation();
$('light').onclick = () => toggleLight();
$('details').onclick = () => toggleDetails();
$('close-annotation').onclick = () => { $('annotation').hidden = true; };
$('fullscreen').onclick = async () => {
  try { if (document.fullscreenElement) await document.exitFullscreen(); else await $('player').requestFullscreen(); }
  catch { announce('Vollbild ist in diesem Browser nicht verfügbar.'); }
};
if (!document.fullscreenEnabled) $<HTMLButtonElement>('fullscreen').hidden = true;
$('share').onclick = async () => {
  const url = shareCamera();
  history.replaceState(null, '', url);
  try { await navigator.clipboard.writeText(url); announce('Link zur Ansicht kopiert.'); }
  catch { window.prompt('Link zur Ansicht kopieren:', url); }
};
let noticeTimer: ReturnType<typeof setTimeout>;
function announce(message: string) {
  clearTimeout(noticeTimer); text.textContent = message; progress.hidden = true; retry.hidden = true; status.hidden = false;
  noticeTimer = setTimeout(() => { status.hidden = true; }, 3500);
}
function setPressed(id: string, pressed: boolean) { $(id).setAttribute('aria-pressed', String(pressed)); }
function markView(key: string | null) {
  document.querySelectorAll<HTMLButtonElement>('[data-view]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.view === key)));
  $('view-label').textContent = key ? views[key as keyof typeof views].description : 'Freie Ansicht';
}

async function start() {
  let renderer: THREE.WebGLRenderer;
  try { renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: 'high-performance' }); }
  catch { text.textContent = '3D wird von diesem Browser nicht unterstützt. Das Vorschaubild zeigt das Modell; Downloads finden Sie unter „Über das Modell“. '; progress.hidden = true; return; }
  renderer.setPixelRatio(Math.min(devicePixelRatio, mobile.matches ? 1.3 : 1.8));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.AgXToneMapping;
  renderer.toneMappingExposure = 1.0;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFShadowMap;
  renderer.shadowMap.autoUpdate = false;
  const canvas = renderer.domElement;
  canvas.tabIndex = 0;
  canvas.setAttribute('aria-label', '3D-Modell. Pfeiltasten drehen, Plus und Minus zoomen, Home setzt die Ansicht zurück.');
  stage.append(canvas);
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#eeece6');
  const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 1500);
  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true; controls.dampingFactor = .09;
  controls.minDistance = 8; controls.maxDistance = 350;
  controls.minPolarAngle = .06; controls.maxPolarAngle = Math.PI / 2 - .025;
  controls.zoomToCursor = true;
  controls.autoRotateSpeed = .45;
  controls.screenSpacePanning = true;
  const hemi = new THREE.HemisphereLight('#fff9ed', '#858c81', .7); scene.add(hemi);
  const sun = new THREE.DirectionalLight('#fff9ed', 2.4);
  sun.position.set(95, 135, 75); sun.target.position.set(-12, 24, 0); scene.add(sun, sun.target);
  sun.castShadow = true; sun.shadow.mapSize.set(mobile.matches ? 512 : 2048, mobile.matches ? 512 : 2048);
  Object.assign(sun.shadow.camera, { left: -105, right: 105, top: 105, bottom: -105, near: 1, far: 350 });
  sun.shadow.camera.updateProjectionMatrix();
  sun.shadow.bias = -.00012; sun.shadow.normalBias = .12; sun.shadow.radius = 3;
  const room = new RoomEnvironment(); const pmrem = new THREE.PMREMGenerator(renderer);
  const env = pmrem.fromScene(room, .04); scene.environment = env.texture; scene.environmentIntensity = .18;
  room.dispose(); pmrem.dispose();
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(900,900), new THREE.ShadowMaterial({ color: '#39483b', opacity: .16 }));
  ground.rotation.x = -Math.PI / 2; ground.position.y = -.04; ground.receiveShadow = true; scene.add(ground);
  let model: THREE.Group | null = null;
  let ready = false;
  let frame: number | null = null;
  let last = 0;
  let settle = 0;
  let transition: { fromP: THREE.Vector3; fromT: THREE.Vector3; toP: THREE.Vector3; toT: THREE.Vector3; start: number } | null = null;
  let warm = false;
  let details = false;
  let framesSlow = 0;
  let renderedFrames = 0;
  const boundsMin = new THREE.Vector3(-70, 2, -45), boundsMax = new THREE.Vector3(45,85,45);
  const vector = new THREE.Vector3();
  function constrainTarget() {
    vector.copy(controls.target).clamp(boundsMin, boundsMax).sub(controls.target);
    if (vector.lengthSq() > 0) { controls.target.add(vector); camera.position.add(vector); }
  }
  function requestRender() { if (frame === null && !document.hidden) { canvas.dataset.idle='false'; frame = requestAnimationFrame(render); } }
  const points = [
    { name: 'Doppeltürme', point: [-39,60,0], body: 'Das westliche Turmpaar prägt die Silhouette. Die Rekonstruktion zeigt die charakteristischen hohen Helme, Geschosse und Maßwerköffnungen.', view: 'towers' },
    { name: 'Dachreiter', point: [0,44,0], body: 'Der schlanke Dachreiter sitzt über der Vierung, an der Langhaus und Querhaus zusammentreffen.', view: 'roof' },
    { name: 'Trikonchos', point: [16,20,-10], body: 'Drei polygonale Chorarme formen den östlichen Abschluss. Strebepfeiler und hohe Fenster gliedern die Außenhaut.', view: 'se' },
    { name: 'Westportal', point: [-47,7,0], body: 'Das Hauptportal liegt zwischen den Türmen. Gewände und Bögen sind modelliert; figürliche Details bleiben vereinfacht.', view: 'portal' },
  ];
  const pointButtons = points.map((p,i) => {
    const b = document.createElement('button'); b.className = 'hotspot'; b.textContent = String(i+1); b.setAttribute('aria-label', p.name);
    b.onclick = () => { chooseView(p.view); $('annotation').hidden = false; $('annotation').querySelector('strong')!.textContent = p.name; $('annotation').querySelector('p')!.textContent = p.body; };
    $('hotspots').append(b); return b;
  });
  const raycaster = new THREE.Raycaster();
  function updateHotspots() {
    if (!details || !model) return;
    camera.updateMatrixWorld();
    points.forEach((p,i) => {
      const world = new THREE.Vector3(...p.point); const projected = world.clone().project(camera);
      const direction = world.clone().sub(camera.position); const distance = direction.length();
      raycaster.set(camera.position, direction.normalize());
      const hit = raycaster.intersectObject(model!,true)[0];
      const visible = projected.z < 1 && projected.z > -1 && Math.abs(projected.x) < .94 && Math.abs(projected.y) < .72 && (!hit || hit.distance >= distance - 3);
      pointButtons[i].hidden = !visible;
      pointButtons[i].style.left = `${(projected.x*.5+.5)*stage.clientWidth}px`; pointButtons[i].style.top = `${(-projected.y*.5+.5)*stage.clientHeight}px`;
    });
  }
  function render(now: number) {
    frame = null;
    const interval=last ? now-last : 0;
    const delta = last ? Math.min(interval/1000,.05) : .016; last = now;
    if (transition) {
      const t = Math.min((now-transition.start)/900,1); const easing = t*t*(3-2*t);
      camera.position.lerpVectors(transition.fromP,transition.toP,easing); controls.target.lerpVectors(transition.fromT,transition.toT,easing);
      if (t === 1) { transition = null; canvas.dataset.transition='false'; }
    }
    const changed=controls.update(delta); constrainTarget();
    const begin = performance.now(); renderer.render(scene,camera); const duration = performance.now()-begin;
    canvas.dataset.frames=String(++renderedFrames);
    canvas.dataset.camera=cameraHash(camera.position.toArray(),controls.target.toArray());
    canvas.dataset.renderMs=duration.toFixed(2);
    canvas.dataset.pixelRatio=String(renderer.getPixelRatio());
    if (duration > 28 || ((controls.autoRotate || transition || changed) && interval > 45)) framesSlow++; else framesSlow = Math.max(0,framesSlow-1);
    if (framesSlow > 30 && renderer.getPixelRatio() > 1) { renderer.setPixelRatio(1); resize(); framesSlow = 0; }
    updateHotspots();
    if (controls.autoRotate || transition || changed || settle-- > 0) requestRender();
    canvas.dataset.idle=String(frame===null);
  }
  controls.addEventListener('change', () => { constrainTarget(); requestRender(); });
  controls.addEventListener('start', () => { transition = null; controls.autoRotate = false; setPressed('rotate',false); markView(null); settle = 45; requestRender(); });
  controls.addEventListener('end', () => { settle = 45; requestRender(); });
  function resize() {
    const w = stage.clientWidth, h = stage.clientHeight;
    renderer.setSize(w,h); camera.aspect = w/h; camera.fov = mobile.matches ? 50 : 42; camera.updateProjectionMatrix(); requestRender();
  }
  new ResizeObserver(resize).observe(stage); resize();
  document.addEventListener('visibilitychange', () => { if (document.hidden && frame !== null) { cancelAnimationFrame(frame); frame=null; } else { last=0; requestRender(); } });
  function moveTo(position: number[], target: number[], animate = true) {
    controls.autoRotate = false; setPressed('rotate',false);
    const toP = new THREE.Vector3(...position), toT = new THREE.Vector3(...target);
    // Clear damped input before switching cameras.
    controls.enableDamping = false; controls.update(); controls.enableDamping = true;
    if (animate && ready && !reducedMotion.matches) { canvas.dataset.transition='true'; transition = { fromP: camera.position.clone(), fromT: controls.target.clone(), toP, toT, start: performance.now() }; }
    else { canvas.dataset.transition='false'; transition=null; camera.position.copy(toP); controls.target.copy(toT); controls.update(); }
    settle = 2; requestRender();
  }
  chooseView = (key, animate = true) => {
    if (!Object.hasOwn(views,key)) return;
    const v = views[key as keyof typeof views]; const t = new THREE.Vector3(...v.target); const p = new THREE.Vector3(...v.position);
    if (['se','west','north','roof'].includes(key)) p.sub(t).multiplyScalar(Math.min(1.15,Math.max(1,.55/camera.aspect))).clampLength(8,350).add(t);
    moveTo(p.toArray(),t.toArray(),animate); markView(key);
  };
  shareCamera = () => `${location.origin}${location.pathname}${cameraHash(camera.position.toArray(),controls.target.toArray())}`;
  function applyHash() { const c = parseCamera(location.hash); if (c) { if (c.view) chooseView(c.view); else { moveTo(c.position,c.target); markView(null); } } else chooseView('se',false); }
  addEventListener('hashchange', applyHash); applyHash();
  toggleRotation = () => { transition=null; controls.autoRotate = !controls.autoRotate; setPressed('rotate',controls.autoRotate); requestRender(); };
  toggleLight = () => {
    warm=!warm; setPressed('light',warm); sun.color.set(warm ? '#ffd3a1' : '#fff9ed'); hemi.color.set(warm ? '#ffe9cc' : '#fff9ed'); scene.background = new THREE.Color(warm ? '#eee5d7' : '#eeece6'); renderer.shadowMap.needsUpdate = true; requestRender();
  };
  toggleDetails = () => { details=!details; setPressed('details',details); $('hotspots').hidden=!details; if (!details) $('annotation').hidden=true; requestRender(); };
  canvas.addEventListener('keydown', e => {
    if (!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','+','=','-','Home'].includes(e.key)) return;
    e.preventDefault(); transition=null; controls.autoRotate=false; setPressed('rotate',false); markView(null);
    const offset = camera.position.clone().sub(controls.target);
    if (e.key==='Home') { chooseView('se'); return; }
    if (e.key==='+' || e.key==='=' || e.key==='-') offset.multiplyScalar(e.key==='-' ? 1.12 : .89).clampLength(8,350);
    else if(e.shiftKey) {
      const pan = new THREE.Vector3(); camera.updateMatrixWorld();
      if(e.key==='ArrowLeft'||e.key==='ArrowRight') pan.setFromMatrixColumn(camera.matrix,0).multiplyScalar(e.key==='ArrowLeft' ? -2 : 2);
      else pan.setFromMatrixColumn(camera.matrix,1).multiplyScalar(e.key==='ArrowUp' ? 2 : -2);
      controls.target.add(pan);
    } else {
      const spherical = new THREE.Spherical().setFromVector3(offset);
      if(e.key==='ArrowLeft') spherical.theta-=.07; if(e.key==='ArrowRight') spherical.theta+=.07;
      if(e.key==='ArrowUp') spherical.phi-=.07; if(e.key==='ArrowDown') spherical.phi+=.07;
      spherical.phi=THREE.MathUtils.clamp(spherical.phi,controls.minPolarAngle,controls.maxPolarAngle); offset.setFromSpherical(spherical);
    }
    camera.position.copy(controls.target).add(offset); constrainTarget(); controls.update(); requestRender();
  });
  canvas.addEventListener('webglcontextlost', e => { e.preventDefault(); ready=false; controls.autoRotate=false; setPressed('rotate',false); if(frame!==null) cancelAnimationFrame(frame); frame=null; poster.classList.remove('loaded'); status.hidden=false; progress.hidden=true; text.textContent='Die 3D-Verbindung wurde unterbrochen. Bitte die Ansicht neu laden.'; retry.hidden=false; retry.onclick=()=>location.reload(); });
  canvas.addEventListener('webglcontextrestored', () => { ready=!!model; renderer.shadowMap.needsUpdate=true; status.hidden=true; poster.classList.add('loaded'); requestRender(); });
  async function load() {
    retry.hidden=true; status.hidden=false; progress.hidden=false; progress.value=0; text.textContent='Modell wird geladen …';
    const abort = new AbortController(); const timeout=setTimeout(()=>abort.abort(),60000);
    try {
      const metadataRequest=fetch(`${base}assets/build-manifest.json`,{signal:abort.signal}).then(r=>r.ok?r.json():null).catch(()=>null);
      const response = await fetch(`${base}assets/church.web.glb`,{ signal:abort.signal });
      if(!response.ok) throw new Error(`HTTP ${response.status}`);
      const metadata=await metadataRequest;
      // Fetch streams decoded bytes; Content-Length can describe gzip/Brotli
      // transfer bytes instead. Prefer the exact decoded build size.
      const total=Number.isSafeInteger(metadata?.web_bytes) && metadata.web_bytes>0 ? metadata.web_bytes : response.headers.get('content-encoding') ? 0 : Number(response.headers.get('content-length'));
      const reader=response.body?.getReader(); const chunks:Uint8Array[]=[]; let received=0;
      if(!reader) throw new Error('Streaming unavailable');
      while(true) { const {done,value}=await reader.read(); if(done) break; chunks.push(value); received+=value.length; if(total>0) progress.value=Math.min(95,received/total*95); else progress.removeAttribute('value'); }
      const data=new Uint8Array(received); let offset=0; for(const chunk of chunks){data.set(chunk,offset);offset+=chunk.length;}
      text.textContent='Geometrie und Materialien werden vorbereitet …'; progress.value=97;
      const gltf = await new GLTFLoader().setMeshoptDecoder(MeshoptDecoder).parseAsync(data.buffer,`${base}assets/`);
      model=gltf.scene; model.traverse(obj=>{ if(obj instanceof THREE.Mesh){obj.castShadow=true;obj.receiveShadow=true;} }); scene.add(model);
      renderer.shadowMap.needsUpdate=true; renderer.render(scene,camera); progress.value=100; ready=true; canvas.dataset.ready='true';
      canvas.dataset.meshes=String(model.getObjectsByProperty('isMesh',true).length);
      status.hidden=true; poster.classList.add('loaded'); requestRender();
    } catch (error) { console.error('Model loading failed',error); text.textContent='Das Modell konnte nicht geladen werden. Prüfen Sie die Verbindung und versuchen Sie es erneut. Das Vorschaubild bleibt sichtbar.'; progress.hidden=true; retry.hidden=false; }
    finally { clearTimeout(timeout); }
  }
  retry.onclick = () => { void load(); };
  await load();
}
void start().catch(error=>{console.error(error); text.textContent='Die 3D-Ansicht konnte nicht gestartet werden. Das Modell ist weiterhin über die Downloads verfügbar.'; progress.hidden=true;});

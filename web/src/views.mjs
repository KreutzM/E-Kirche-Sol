// Web presentation cameras in glTF coordinates (X east, Y up, -Z north).
// Independent of the photographic validation poses. Origin: crossing floor.
export const views = {
  se: { label: 'Südost', description: 'Südost · Gesamtansicht', position: [115, 85, 145], target: [-13, 34, 0] },
  west: { label: 'Westfassade', description: 'Westfassade · Die Doppeltürme', position: [-202, 58, 0], target: [-38, 36, 0] },
  north: { label: 'Nordseite', description: 'Nordseite · Langhaus und Chor', position: [-8, 60, -163], target: [-12, 30, 0] },
  roof: { label: 'Dachlandschaft', description: 'Dachlandschaft · Über der Vierung', position: [78, 150, 125], target: [-12, 36, 0] },
  portal: { label: 'Portal', description: 'Westportal · Architektonische Details', position: [-68, 10, 14], target: [-46, 7, 0] },
  towers: { label: 'Türme', description: 'Türme · Helme und Maßwerk', position: [-83, 73, 57], target: [-39, 58, 0] },
};
export function parseCamera(hash) {
  const p = new URLSearchParams(hash.replace(/^#/, ''));
  const view = p.get('view');
  if (view && Object.hasOwn(views, view)) return { view, ...views[view] };
  const values = (p.get('camera') || '').split(',').map(Number);
  if (values.length !== 6 || !values.every(Number.isFinite)) return null;
  const [x,y,z,tx,ty,tz] = values;
  const distance = Math.hypot(x-tx,y-ty,z-tz);
  if (Math.max(Math.abs(x),Math.abs(z)) > 600 || y < 1 || y > 600 || tx < -70 || tx > 45 || ty < 2 || ty > 85 || Math.abs(tz) > 45 || distance < 7.99 || distance > 350.01 || y < ty) return null;
  return { view: null, position: [x,y,z], target: [tx,ty,tz] };
}
export function cameraHash(position, target) {
  return '#camera=' + [...position, ...target].map(v => Number(v.toFixed(3))).join(',');
}

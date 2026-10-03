import { readFile, writeFile, mkdir, copyFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS, EXTMeshoptCompression } from '@gltf-transform/extensions';
import { MeshoptEncoder, MeshoptDecoder } from 'meshoptimizer';
import sharp from 'sharp';

const root = fileURLToPath(new URL('../../', import.meta.url));
const out = path.join(root, 'web/public/assets');
const source = path.join(root, 'blender/exports/elisabethkirche_SOL-01.glb');
const digest = (data) => createHash('sha256').update(data).digest('hex');
const expected = '69fdd8e8655ead7a9b92b4381b3403214f401645b07f3933272bee8b27cb9c4f';
const bytes = await readFile(source);
if (digest(bytes) !== expected) throw new Error('SOL-01 master hash differs. Run git lfs pull; never build from an LFS pointer or changed master.');
const frozen = JSON.parse(await readFile(path.join(root,'validation/reports/SOL-01-artifacts.json'),'utf8'));
for (const relative of ['blender/scene/elisabethkirche.blend','validation/delivery/SOL-01/PRES_SE_GLB.png']) {
  const record=frozen.artifacts.find(a=>a.path===relative);
  const data=await readFile(path.join(root,relative));
  if (!record || digest(data)!==record.sha256) throw new Error(`Frozen asset hash differs: ${relative}. Fetch Git LFS content before building.`);
}
await mkdir(out, { recursive: true });
await Promise.all([MeshoptEncoder.ready, MeshoptDecoder.ready]);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({
  'meshopt.encoder': MeshoptEncoder, 'meshopt.decoder': MeshoptDecoder,
});
const document = await io.read(source);

// Prove exact decoded attribute/index preservation, including fine detail.
function fingerprint(doc) {
  const r = doc.getRoot();
  const a = r.listAccessors();
  const indices = new Set(r.listMeshes().flatMap(m => m.listPrimitives().map(p => p.getIndices())));
  function accessorDigest(v) {
    const array = v.getArray();
    if (!indices.has(v)) return digest(Buffer.from(array.buffer,array.byteOffset,array.byteLength));
    // Meshopt may cyclically rotate triangle vertices. Canonicalize cyclic
    // order only: reversed winding, changed vertices or triangles still fail.
    const canonical = new Uint32Array(array.length);
    for (let i=0;i<array.length;i+=3) {
      const t=[array[i],array[i+1],array[i+2]];
      const j=t.indexOf(Math.min(...t));
      for (let k=0;k<3;k++) canonical[i+k]=t[(j+k)%3];
    }
    return digest(Buffer.from(canonical.buffer));
  }
  return {
    accessors: a.map(v => ({ type: v.getType(), normalized: v.getNormalized(), data: accessorDigest(v) })),
    nodes: r.listNodes().map(n => ({ name: n.getName(), matrix: n.getMatrix(), mesh: r.listMeshes().indexOf(n.getMesh()), children: n.listChildren().map(c => r.listNodes().indexOf(c)) })),
    meshes: r.listMeshes().map(m => m.listPrimitives().map(p => ({ mode: p.getMode(), indices: a.indexOf(p.getIndices()), attributes: p.listSemantics().map(s => [s, a.indexOf(p.getAttribute(s))]), material: r.listMaterials().indexOf(p.getMaterial()) }))),
    textures: r.listTextures().map(t => digest(t.getImage())),
    materials: r.listMaterials().map(m => ({
      name:m.getName(), baseColor:m.getBaseColorFactor(), metallic:m.getMetallicFactor(), roughness:m.getRoughnessFactor(), emissive:m.getEmissiveFactor(),
      alphaMode:m.getAlphaMode(), alphaCutoff:m.getAlphaCutoff(), doubleSided:m.getDoubleSided(), normalScale:m.getNormalScale(), occlusionStrength:m.getOcclusionStrength(),
      textures:[m.getBaseColorTexture(),m.getNormalTexture(),m.getMetallicRoughnessTexture(),m.getEmissiveTexture(),m.getOcclusionTexture()].map(t=>r.listTextures().indexOf(t)),
    })),
  };
}
const before = fingerprint(document);
// No simplification, vertex reorder, quantization or normal filters: lossless
// buffer compression only, retaining exact original material texture bytes.
document.createExtension(EXTMeshoptCompression).setRequired(true).setEncoderOptions({ method: EXTMeshoptCompression.EncoderMethod.QUANTIZE });
const compressed = await io.writeBinary(document);
const decoded = await io.readBinary(compressed);
if (JSON.stringify(fingerprint(decoded)) !== JSON.stringify(before)) {
  await writeFile(path.join(root,'tmp/web-before.json'),JSON.stringify(before,null,2));
  await writeFile(path.join(root,'tmp/web-after.json'),JSON.stringify(fingerprint(decoded),null,2));
  throw new Error('Decoded web geometry/material texture fingerprint changed.');
}
await writeFile(path.join(out, 'church.web.glb'), compressed);
await copyFile(source, path.join(out, 'elisabethkirche_SOL-01.glb'));
await copyFile(path.join(root, 'blender/scene/elisabethkirche.blend'), path.join(out, 'elisabethkirche.blend'));
await copyFile(path.join(root, 'validation/delivery/SOL-01/LICENSE.md'), path.join(out, 'LICENSE.md'));
const threeLicence=await readFile(path.join(root,'web/node_modules/three/LICENSE'),'utf8');
const meshoptLicence=await readFile(path.join(root,'web/node_modules/meshoptimizer/LICENSE.md'),'utf8');
const decoderHeader=(await readFile(path.join(root,'web/node_modules/three/examples/jsm/libs/meshopt_decoder.module.js'),'utf8')).split('\n').slice(0,2).join('\n');
await writeFile(path.join(out,'THIRD_PARTY_NOTICES.txt'),`Runtime software notices\n\nTHREE.JS\n${threeLicence}\n\nMESHOPTIMIZER DECODER\n${decoderHeader}\n${meshoptLicence}\n`);
await sharp(path.join(root, 'validation/delivery/SOL-01/PRES_SE_GLB.png')).resize({ width: 1400, withoutEnlargement: true }).webp({ quality: 85 }).toFile(path.join(out, 'poster.webp'));
const manifest = { source_sha256: expected, web_sha256: digest(compressed), source_bytes: bytes.length, web_bytes: compressed.length, decoded_fingerprint: digest(JSON.stringify(before)), exact_decoded_preservation: true, strategy: 'Lossless Meshopt buffer compression; original textures, attributes, indices and scene transforms retained.' };
await writeFile(path.join(out, 'build-manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
console.log(JSON.stringify(manifest, null, 2));

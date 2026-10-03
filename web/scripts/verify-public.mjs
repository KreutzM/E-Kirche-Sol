import { readFile, readdir, mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { createHash } from 'node:crypto';
const root=fileURLToPath(new URL('../../',import.meta.url));
const base=process.argv[2] || 'https://kreutzm.github.io/E-Kirche-Sol/';
const artifact=path.resolve(process.argv[3] || path.join(root,'tmp/web-published-build'));
const hash=b=>createHash('sha256').update(b).digest('hex');
async function walk(directory) {
  const result=[];
  for (const entry of await readdir(directory,{withFileTypes:true})) {
    const p=path.join(directory,entry.name);
    if(entry.isDirectory()) result.push(...await walk(p)); else result.push(p);
  }
  return result;
}
const results=[];
for (const file of await walk(artifact)) {
  const relative=path.relative(artifact,file).split(path.sep).join('/');
  const local=await readFile(file);
  const response=await fetch(new URL(relative,base),{signal:AbortSignal.timeout(60000)});
  if(!response.ok) throw new Error(`Published asset ${relative}: HTTP ${response.status}`);
  const served=Buffer.from(await response.arrayBuffer());
  if(hash(local)!==hash(served)) throw new Error(`Published bytes differ from CI artifact: ${relative}`);
  if(relative.endsWith('.glb') && served.subarray(0,4).toString()!=='glTF') throw new Error('GLB pointer/format failure');
  results.push({path:relative,bytes:served.length,sha256:hash(served),http:response.status,contentType:response.headers.get('content-type'),contentEncoding:response.headers.get('content-encoding')});
}
const output=path.join(root,'tmp/web-live'); await mkdir(output,{recursive:true});
await writeFile(path.join(output,'integrity.json'),JSON.stringify({timestamp:new Date().toISOString(),base,allMatchCIArtifact:true,files:results},null,2)+'\n');
console.log(`Verified ${results.length} published files against the CI artifact, including original model downloads.`);

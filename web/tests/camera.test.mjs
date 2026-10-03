import test from 'node:test';
import assert from 'node:assert/strict';
import { parseCamera, cameraHash, views } from '../src/views.mjs';
test('Every named view survives a shared URL', () => {
  for (const key of Object.keys(views)) assert.equal(parseCamera('#view='+key).view,key);
});
test('Arbitrary camera round trips without losing perspective', () => {
  const p=[115.1234,85,145],t=[-13,34,0];
  const parsed=parseCamera(cameraHash(p,t));
  assert.deepEqual(parsed.position,[115.123,85,145]); assert.deepEqual(parsed.target,t);
});
test('Rejects malformed, underground and out-of-bounds shared cameras', () => {
  for(const input of ['#camera=',' #camera=Infinity,85,145,-13,34,0','#camera=0,-1,0,0,2,0','#camera=9999,85,145,-13,34,0','#camera=0,2,0,0,80,0','#camera=0,2,0,0,2,0','#view=__proto__']) assert.equal(parseCamera(input),null,input);
});

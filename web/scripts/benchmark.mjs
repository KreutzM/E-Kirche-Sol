import { chromium, devices } from '@playwright/test';
import { mkdir, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const url=process.argv[2] || 'https://kreutzm.github.io/E-Kirche-Sol/';
const output=fileURLToPath(new URL('../../tmp/web-live/',import.meta.url));
await mkdir(output,{recursive:true});
// Use the actual browser's available GPU path, without forcing SwiftShader.
const browser=await chromium.launch({channel:process.env.CI ? 'chromium':'chrome'});
const results=[];
try {
  for (const [name,device] of [['desktop',{...devices['Desktop Chrome'],viewport:{width:1440,height:1000}}],['mobile',devices['Pixel 7']]]) {
    const context=await browser.newContext(device);
    const page=await context.newPage();
    const errors=[]; page.on('pageerror',e=>errors.push(e.message));
    const start=Date.now();
    await page.goto(url);
    await page.locator('canvas[data-ready=true]').waitFor({timeout:60000});
    const readyMs=Date.now()-start;
    await page.screenshot({path:path.join(output,`${name}-se.png`)});
    await page.getByRole('button',{name:'Rundgang',exact:true}).click();
    await page.waitForTimeout(1000);
    const framesStart=Number(await page.locator('canvas').getAttribute('data-frames'));
    const measureStart=Date.now();
    await page.waitForTimeout(5000);
    const elapsed=Date.now()-measureStart;
    const frames=Number(await page.locator('canvas').getAttribute('data-frames'))-framesStart;
    await page.getByRole('button',{name:'Rundgang',exact:true}).click();
    const metrics=await page.evaluate(()=>{
      const canvas=document.querySelector('canvas'); const gl=canvas.getContext('webgl2');
      const debug=gl.getExtension('WEBGL_debug_renderer_info');
      const resource=performance.getEntriesByType('resource').find(r=>r.name.endsWith('/church.web.glb'));
      return {viewport:[innerWidth,innerHeight],dpr:devicePixelRatio,renderDpr:canvas.dataset.pixelRatio,
        renderer:debug?gl.getParameter(debug.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER),
        userAgent:navigator.userAgent,modelDownloadMs:resource?.duration,
        transferBytes:resource?.transferSize,decodedBodyBytes:resource?.decodedBodySize,meshes:Number(canvas.dataset.meshes)};
    });
    const record={device:name,emulatedMobile:name==='mobile',url,readyMs,frames,elapsedMs:elapsed,framesPerSecond:Number((frames*1000/elapsed).toFixed(1)),...metrics,errors};
    if(record.meshes!==19 || errors.length) throw new Error('Model/console check failed: '+JSON.stringify(record));
    // Verify full screen through the actual browser when its API is available.
    if(await page.evaluate(()=>document.fullscreenEnabled)) {
      await page.getByRole('button',{name:'Vollbild',exact:true}).click();
      await page.waitForFunction(()=>document.fullscreenElement!==null);
      await page.getByRole('button',{name:'Vollbild',exact:true}).click();
      await page.waitForFunction(()=>document.fullscreenElement===null);
      record.fullscreenVerified=true;
    } else record.fullscreenVerified='not supported by this browser';
    results.push(record); console.log(JSON.stringify(record));
    await context.close();
  }
  await writeFile(path.join(output,'metrics.json'),JSON.stringify({timestamp:new Date().toISOString(),results},null,2)+'\n');
} finally { await browser.close(); }

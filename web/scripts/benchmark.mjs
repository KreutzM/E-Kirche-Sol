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
    const settle=()=>page.waitForFunction(()=>document.querySelector('canvas')?.dataset.idle==='true');
    const pose=async()=>{
      const values=(await page.locator('canvas').getAttribute('data-camera')).replace('#camera=','').split(',').map(Number);
      return {target:values.slice(3),distance:Math.hypot(...values.slice(0,3).map((v,i)=>v-values[i+3]))};
    };
    await page.getByRole('button',{name:'Zurücksetzen',exact:true}).click(); await settle();
    const beforeZoom=await pose();
    if(name==='desktop') {
      await page.mouse.move(device.viewport.width*.5,device.viewport.height*.5);
      await page.mouse.wheel(0,-250);
    } else {
      const session=await context.newCDPSession(page);
      const w=device.viewport.width,h=device.viewport.height;
      const points=(left,right,y)=>[{id:0,x:w*left,y:h*y},{id:1,x:w*right,y:h*y}];
      await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:points(.35,.65,.5)});
      await session.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:points(.25,.75,.5)});
      await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
      await session.detach();
    }
    await settle();
    if((await pose()).distance>=beforeZoom.distance-.1) throw new Error('Wheel/pinch zoom did not move closer.');
    const beforePan=await pose();
    if(name==='desktop') {
      await page.mouse.move(700,450); await page.mouse.down({button:'right'});
      await page.mouse.move(780,490,{steps:5}); await page.mouse.up({button:'right'});
    } else {
      const session=await context.newCDPSession(page); const w=device.viewport.width,h=device.viewport.height;
      await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{id:0,x:w*.35,y:h*.5},{id:1,x:w*.65,y:h*.5}]});
      await session.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{id:0,x:w*.40,y:h*.54},{id:1,x:w*.70,y:h*.54}]});
      await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]}); await session.detach();
    }
    await settle();
    const afterPan=await pose();
    if(Math.hypot(...afterPan.target.map((v,i)=>v-beforePan.target[i]))<.1) throw new Error('Mouse/two-finger pan did not move target.');
    await page.locator('canvas').focus(); const beforeKey=await pose();
    await page.keyboard.press('Equal'); await settle();
    if((await pose()).distance>=beforeKey.distance-.1) throw new Error('Keyboard zoom failed.');
    const beforeKeyPan=await pose(); await page.keyboard.press('Shift+ArrowRight'); await settle();
    if(Math.hypot(...(await pose()).target.map((v,i)=>v-beforeKeyPan.target[i]))<.1) throw new Error('Keyboard pan failed.');
    await page.emulateMedia({reducedMotion:'reduce'});
    await page.getByRole('button',{name:'Westfassade',exact:true}).click();
    if(await page.locator('canvas').getAttribute('data-transition')!=='false') throw new Error('Reduced motion did not disable camera transition.');
    record.navigation={zoomVerified:true,panVerified:true,keyboardZoomVerified:true,keyboardPanVerified:true,reducedMotionVerified:true};
    await page.getByRole('button',{name:'Rundgang',exact:true}).click();
    await page.waitForTimeout(200);
    const paused=await page.evaluate(()=>{
      const frames=Number(document.querySelector('canvas').dataset.frames);
      Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});
      document.dispatchEvent(new Event('visibilitychange')); return frames;
    });
    await page.waitForTimeout(500);
    if(Number(await page.locator('canvas').getAttribute('data-frames'))!==paused) throw new Error('Visibility event did not suspend rendering.');
    await page.evaluate(()=>{delete document.hidden;document.dispatchEvent(new Event('visibilitychange'));});
    await page.waitForFunction(frames=>Number(document.querySelector('canvas').dataset.frames)>frames,paused);
    await page.getByRole('button',{name:'Rundgang',exact:true}).click();
    record.visibilityEvents='Suspension and resume verified with simulated document visibility changes';
    results.push(record); console.log(JSON.stringify(record));
    await context.close();
  }
  await writeFile(path.join(output,'metrics.json'),JSON.stringify({timestamp:new Date().toISOString(),results},null,2)+'\n');
} finally { await browser.close(); }

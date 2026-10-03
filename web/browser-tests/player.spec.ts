import { test, expect } from '@playwright/test';
test('Loads the actual model, changes views and exposes attribution/downloads', async ({ page }, testInfo) => {
  const errors:string[]=[];
  page.on('pageerror', e=>errors.push(e.message));
  await page.goto('./');
  await expect(page.locator('canvas')).toHaveAttribute('data-ready','true');
  await expect(page.locator('canvas')).toHaveAttribute('data-meshes','19');
  await expect(page.locator('#poster')).toHaveClass('loaded');
  await page.screenshot({path:`../tmp/web-${testInfo.project.name}-se.png`});
  for (const [key,label] of [['west','Westfassade'],['north','Nordseite'],['roof','Dachlandschaft'],['portal','Portal'],['towers','Türme']]) {
    await page.getByRole('button',{name:label,exact:true}).click();
    await expect(page.locator(`[data-view=${key}]`)).toHaveAttribute('aria-pressed','true');
    await expect(page.locator('canvas')).toHaveAttribute('data-transition','false');
    await page.screenshot({path:`../tmp/web-${testInfo.project.name}-${key}.png`});
  }
  await page.getByRole('button',{name:'Warmes Licht',exact:true}).click();
  await expect(page.locator('#light')).toHaveAttribute('aria-pressed','true');
  await page.getByRole('button',{name:'Zurücksetzen',exact:true}).click();
  await expect(page.locator('[data-view=se]')).toHaveAttribute('aria-pressed','true');
  await page.getByRole('button',{name:'Rundgang',exact:true}).click();
  await expect(page.locator('#rotate')).toHaveAttribute('aria-pressed','true');
  await page.getByRole('button',{name:'Rundgang',exact:true}).click();
  await expect(page.locator('#rotate')).toHaveAttribute('aria-pressed','false');
  await page.getByRole('button',{name:'Infopunkte',exact:true}).click();
  await expect(page.locator('#hotspots')).toBeVisible();
  await page.getByRole('button',{name:'Portal',exact:true}).click();
  await expect(page.locator('canvas')).toHaveAttribute('data-transition','false');
  await page.getByRole('button',{name:'Westportal',exact:true}).click();
  await expect(page.locator('#annotation')).toBeVisible();
  await expect(page.locator('#annotation strong')).toHaveText('Westportal');
  await page.getByRole('button',{name:'Infopunkte',exact:true}).click();
  await page.getByRole('button',{name:'Über das Modell'}).click();
  await expect(page.getByRole('dialog')).toBeVisible();
  await expect(page.getByRole('link',{name:'Originalmodell · GLB'})).toHaveAttribute('href',/assets\/elisabethkirche_SOL-01.glb$/);
  await expect(page.getByRole('link',{name:'CC BY-SA 4.0'})).toBeVisible();
  await page.getByRole('button',{name:'Informationen schließen'}).click();
  await expect(page.getByRole('dialog')).not.toBeVisible();
  expect(errors).toEqual([]);
});
test('Mouse or touch rotates the camera; settled player stops rendering', async ({page},testInfo) => {
  await page.goto('./');
  await expect(page.locator('canvas')).toHaveAttribute('data-ready','true');
  const before=await page.locator('canvas').getAttribute('data-camera');
  if(testInfo.project.name==='mobile') {
    const session=await page.context().newCDPSession(page);
    await session.send('Input.dispatchTouchEvent',{type:'touchStart',touchPoints:[{x:180,y:350}]});
    await session.send('Input.dispatchTouchEvent',{type:'touchMove',touchPoints:[{x:250,y:365}]});
    await session.send('Input.dispatchTouchEvent',{type:'touchEnd',touchPoints:[]});
    await session.detach();
  } else {
    await page.mouse.move(680,450); await page.mouse.down(); await page.mouse.move(800,470,{steps:8}); await page.mouse.up();
  }
  await expect(page.locator('#view-label')).toHaveText('Freie Ansicht');
  await expect(page.locator('canvas')).not.toHaveAttribute('data-camera',before!);
  // Reset cancels damping and gives an authoritative stable idle pose.
  await page.getByRole('button',{name:'Zurücksetzen',exact:true}).click();
  await expect(page.locator('canvas')).toHaveAttribute('data-transition','false');
  await expect(page.locator('canvas')).toHaveAttribute('data-idle','true');
  const frames=await page.locator('canvas').getAttribute('data-frames');
  await page.waitForTimeout(1500);
  await expect(page.locator('canvas')).toHaveAttribute('data-frames',frames!);
});
test('Shared cameras and keyboard controls restore a useful view', async ({ page }) => {
  await page.goto('./#view=west');
  await expect(page.locator('canvas')).toHaveAttribute('data-ready','true');
  await expect(page.locator('[data-view=west]')).toHaveAttribute('aria-pressed','true');
  await page.locator('canvas').focus(); await page.keyboard.press('ArrowRight');
  await expect(page.locator('#view-label')).toHaveText('Freie Ansicht');
  await page.keyboard.press('Home');
  await expect(page.locator('[data-view=se]')).toHaveAttribute('aria-pressed','true');
  await expect(page.locator('canvas')).toHaveAttribute('data-idle','true');
  await page.getByRole('button',{name:'Ansicht teilen',exact:true}).click();
  const shared=page.url();
  expect(new URL(shared).hash).toMatch(/^#camera=/);
  await page.goto(shared);
  await expect(page.locator('canvas')).toHaveAttribute('data-ready','true');
  await expect(page.locator('canvas')).toHaveAttribute('data-camera',new URL(shared).hash);
});
test('Failed download retains poster and permits retry', async ({ page }) => {
  await page.route('**/church.web.glb',route=>route.fulfill({status:503,body:'Unavailable'}));
  await page.goto('./');
  await expect(page.getByRole('button',{name:'Erneut laden'})).toBeVisible();
  await expect(page.locator('#poster')).not.toHaveClass('loaded');
  await page.unroute('**/church.web.glb');
  await page.getByRole('button',{name:'Erneut laden'}).click();
  await expect(page.locator('canvas')).toHaveAttribute('data-ready','true');
});

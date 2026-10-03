import { defineConfig, devices } from '@playwright/test';
export default defineConfig({
  testDir: './browser-tests',
  timeout: 120000,
  expect: { timeout: 30000 },
  outputDir: '../tmp/web-browser-results',
  reporter: [['list'],['json',{outputFile:'../tmp/web-browser-results.json'}]],
  use: { baseURL: process.env.PLAYER_URL || 'http://127.0.0.1:5183/E-Kirche-Sol/', screenshot: 'only-on-failure', launchOptions: { args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] } },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'], channel: process.env.CI ? undefined : 'chrome', viewport: {width:1440,height:1000} } },
    { name: 'mobile', use: { ...devices['Pixel 7'], channel: process.env.CI ? undefined : 'chrome' } },
  ],
  webServer: process.env.PLAYER_URL ? undefined : { command: 'npm run preview -- --port 5183', url: 'http://127.0.0.1:5183/E-Kirche-Sol/', reuseExistingServer: false },
});

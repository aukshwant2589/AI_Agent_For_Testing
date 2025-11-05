
import { PlaywrightTestConfig } from '@playwright/test';

const config: PlaywrightTestConfig = {
    timeout: 60000,
    retries: 1,
    use: {
        headless: false,
        viewport: { width: 1280, height: 720 },
        video: 'retain-on-failure',
        screenshot: 'only-on-failure',
        trace: 'retain-on-failure',
    },
    reporter: [
        ['list'],
        ['html', { outputFolder: 'playwright-report' }],
        ['junit', { outputFile: 'test-results/junit.xml' }]
    ],
    projects: [
        {
            name: 'Chrome',
            use: { browserName: 'chromium' }
        },
        {
            name: 'Firefox',
            use: { browserName: 'firefox' }
        },
        {
            name: 'Safari',
            use: { browserName: 'webkit' }
        }
    ]
};

export default config;

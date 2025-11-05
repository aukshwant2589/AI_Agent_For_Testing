
import { Page } from '@playwright/test';

export class TestUtils {
    constructor(private page: Page) {}

    async waitAndClick(selector: string) {
        await this.page.waitForSelector(selector);
        await this.page.click(selector);
    }

    async waitAndFill(selector: string, value: string) {
        await this.page.waitForSelector(selector);
        await this.page.fill(selector, value);
    }

    async waitForText(text: string) {
        await this.page.waitForSelector(`text=${text}`);
    }

    async validateElement(selector: string, expectedState: 'visible' | 'hidden' = 'visible') {
        if (expectedState === 'visible') {
            await this.page.waitForSelector(selector, { state: 'visible' });
        } else {
            await this.page.waitForSelector(selector, { state: 'hidden' });
        }
    }

    async validateText(selector: string, expectedText: string) {
        const element = await this.page.waitForSelector(selector);
        const text = await element.textContent();
        return text?.includes(expectedText);
    }

    async takeScreenshot(name: string) {
        await this.page.screenshot({
            path: `./screenshots/${name}.png`,
            fullPage: true
        });
    }
}

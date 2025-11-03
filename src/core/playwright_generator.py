"""Playwright test automation generator"""
from typing import Dict, List
import os
import json

class PlaywrightTestGenerator:
    """Generates Playwright automation scripts from test cases"""
    
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        self.page_objects_dir = os.path.join(output_dir, 'page_objects')
        self.test_scripts_dir = os.path.join(output_dir, 'tests')
        self.utils_dir = os.path.join(output_dir, 'utils')
        
        # Create directory structure
        for directory in [self.page_objects_dir, self.test_scripts_dir, self.utils_dir]:
            os.makedirs(directory, exist_ok=True)
            
    def generate_automation_scripts(self, test_cases: List[Dict]) -> None:
        """Generate complete Playwright automation project"""
        # Generate base configuration
        self._generate_playwright_config()
        self._generate_test_utils()
        
        # Group test cases by feature
        feature_tests = {}
        for test in test_cases:
            feature = test['name'].split(' - ')[0].lower().replace(' ', '_')
            if feature not in feature_tests:
                feature_tests[feature] = []
            feature_tests[feature].append(test)
            
        # Generate page objects and test files for each feature
        for feature, tests in feature_tests.items():
            self._generate_page_object(feature, tests)
            self._generate_test_file(feature, tests)
            
    def _generate_playwright_config(self) -> None:
        """Generate Playwright configuration file"""
        config_content = """
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
"""
        with open(os.path.join(self.output_dir, 'playwright.config.ts'), 'w') as f:
            f.write(config_content)
            
    def _generate_test_utils(self) -> None:
        """Generate utility functions for tests"""
        utils_content = """
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
"""
        with open(os.path.join(self.utils_dir, 'test-utils.ts'), 'w') as f:
            f.write(utils_content)
            
    def _generate_page_object(self, feature: str, tests: List[Dict]) -> None:
        """Generate page object for a feature"""
        # Extract selectors from test cases
        selectors = self._extract_selectors(tests)
        
        page_object_content = f"""
import {{ Page }} from '@playwright/test';
import {{ TestUtils }} from '../utils/test-utils';

export class {feature.title()}Page {{
    private utils: TestUtils;

    constructor(private page: Page) {{
        this.utils = new TestUtils(page);
    }}

    // Selectors
    private selectors = {{
        {self._format_selectors(selectors)}
    }};

    // Actions
    {self._generate_page_actions(feature, tests)}

    // Validations
    {self._generate_page_validations(feature, tests)}
}}
"""
        
        with open(os.path.join(self.page_objects_dir, f'{feature}-page.ts'), 'w') as f:
            f.write(page_object_content)
            
    def _generate_test_file(self, feature: str, tests: List[Dict]) -> None:
        """Generate test file for a feature"""
        test_content = f"""
import {{ test, expect }} from '@playwright/test';
import {{ {feature.title()}Page }} from '../page-objects/{feature}-page';

test.describe('{feature.replace("_", " ").title()} Tests', () => {{
    let page;
    let {feature}Page;

    test.beforeEach(async ({{ browser }}) => {{
        page = await browser.newPage();
        {feature}Page = new {feature.title()}Page(page);
    }});

    test.afterEach(async () => {{
        await page.close();
    }});

    {self._generate_test_cases(tests)}
}});
"""
        
        with open(os.path.join(self.test_scripts_dir, f'{feature}.spec.ts'), 'w') as f:
            f.write(test_content)
            
    def _extract_selectors(self, tests: List[Dict]) -> Dict[str, str]:
        """Extract selectors from test cases"""
        selectors = {}
        
        for test in tests:
            for step in test.get('steps', []):
                # Extract potential selectors from step description
                elements = self._identify_elements(step)
                for element in elements:
                    selector_name = element.lower().replace(' ', '_')
                    selectors[selector_name] = f'[data-testid="{selector_name}"]'
                    
        return selectors
        
    def _identify_elements(self, step: str) -> List[str]:
        """Identify UI elements from step description"""
        element_indicators = ['button', 'input', 'field', 'link', 'dropdown', 'menu']
        elements = []
        
        words = step.lower().split()
        for i, word in enumerate(words):
            if word in element_indicators and i > 0:
                elements.append(words[i-1] + '_' + word)
                
        return elements
        
    def _format_selectors(self, selectors: Dict[str, str]) -> str:
        """Format selectors for page object"""
        return '\n        '.join(
            f"{name}: '{selector}',"
            for name, selector in selectors.items()
        )
        
    def _generate_page_actions(self, feature: str, tests: List[Dict]) -> str:
        """Generate action methods for page object"""
        actions = set()
        
        for test in tests:
            for step in test.get('steps', []):
                if any(action in step.lower() for action in ['click', 'fill', 'select', 'enter']):
                    action_name = self._generate_action_name(step)
                    actions.add(self._generate_action_method(action_name, step))
                    
        return '\n\n    '.join(actions)
        
    def _generate_action_name(self, step: str) -> str:
        """Generate method name from step description"""
        words = step.lower().split()
        action_words = ['click', 'fill', 'select', 'enter']
        
        for word in words:
            if word in action_words:
                return f"{word}_{words[words.index(word)+1]}"
                
        return 'perform_action'
        
    def _generate_action_method(self, name: str, step: str) -> str:
        """Generate action method code"""
        if 'click' in step.lower():
            return f"""async {name}() {{
        await this.utils.waitAndClick(this.selectors.{name}_button);
    }}"""
        elif any(action in step.lower() for action in ['fill', 'enter']):
            return f"""async {name}(value: string) {{
        await this.utils.waitAndFill(this.selectors.{name}_input, value);
    }}"""
        
        return f"""async {name}() {{
        // TODO: Implement action
    }}"""
        
    def _generate_page_validations(self, feature: str, tests: List[Dict]) -> str:
        """Generate validation methods for page object"""
        validations = set()
        
        for test in tests:
            expected_result = test.get('expected_result', '')
            validation_name = f"validate_{expected_result.lower().replace(' ', '_')}"
            validations.add(self._generate_validation_method(validation_name, expected_result))
            
        return '\n\n    '.join(validations)
        
    def _generate_validation_method(self, name: str, expected: str) -> str:
        """Generate validation method code"""
        return f"""async {name}() {{
        return await this.utils.validateText(this.selectors.result_message, '{expected}');
    }}"""
        
    def _generate_test_cases(self, tests: List[Dict]) -> str:
        """Generate test case implementations"""
        test_implementations = []
        
        for test in tests:
            test_name = test['name'].replace(' - ', '_').lower()
            steps = test.get('steps', [])
            
            implementation = f"""
    test('{test["name"]}', async () => {{
        {self._generate_test_steps(steps)}
        
        // Validate expected result
        {self._generate_test_validation(test.get('expected_result', ''))}
    }});"""
            
            test_implementations.append(implementation)
            
        return '\n'.join(test_implementations)
        
    def _generate_test_steps(self, steps: List[str]) -> str:
        """Generate test step implementations"""
        implemented_steps = []
        
        for step in steps:
            if 'click' in step.lower():
                element = step.split('click')[-1].strip()
                implemented_steps.append(
                    f"await page.click('{element}');"
                )
            elif any(action in step.lower() for action in ['fill', 'enter']):
                element = step.split('enter')[-1].strip()
                implemented_steps.append(
                    f"await page.fill('{element}', 'test_value');"
                )
            else:
                implemented_steps.append(f"// TODO: Implement - {step}")
                
        return '\n        '.join(implemented_steps)
        
    def _generate_test_validation(self, expected_result: str) -> str:
        """Generate test validation code"""
        return f"""await expect(page.locator('text={expected_result}')).toBeVisible();"""
"""Environment setup for Behave tests"""
from behave import fixture, use_fixture
from playwright.sync_api import sync_playwright

@fixture
def browser_context(context):
    """Set up browser context for tests"""
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    context.browser = browser
    context.page = browser.new_page()
    yield context.page
    browser.close()
    playwright.stop()

def before_all(context):
    """Setup before all tests"""
    use_fixture(browser_context, context)
    # Set base URL and other configurations
    context.base_url = "https://your-app-url.com"  # Replace with your application URL
    context.default_timeout = 5000  # 5 seconds timeout

def after_all(context):
    """Cleanup after all tests"""
    if hasattr(context, 'browser'):
        context.browser.close()

def before_scenario(context, scenario):
    """Setup before each scenario"""
    # Reset any scenario-specific data
    context.error_messages = []
    context.current_user = None
    context.feature_flags = {
        "welcome-screen": True
    }
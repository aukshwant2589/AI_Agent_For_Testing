"""Step definitions for Welcome screen tests"""
from behave import given, when, then
import time
from playwright.sync_api import expect

@given('the system is running')
def step_impl(context):
    context.page.goto(context.base_url)
    # Verify the page is loaded
    expect(context.page).to_have_url(context.base_url)

@given('the welcome-screen feature flag is enabled by default')
def step_impl(context):
    context.feature_flags['welcome-screen'] = True

@given('test users with different permission levels exist')
def step_impl(context):
    # This would typically be set up in your test environment
    context.test_users = {
        'admin_with_roster': {
            'username': 'admin1@test.com',
            'password': 'password123',
            'has_roster_rights': True
        },
        'admin_without_roster': {
            'username': 'admin2@test.com',
            'password': 'password123',
            'has_roster_rights': False
        }
    }

@given('I am an Ed administrator with rostering rights')
def step_impl(context):
    user = context.test_users['admin_with_roster']
    # Login implementation
    context.page.fill('#username', user['username'])
    context.page.fill('#password', user['password'])
    context.page.click('#login-button')

@given('I have never logged into the application before')
def step_impl(context):
    # This would be handled by your test data setup
    # Reset user's first login status
    pass

@when('I log into the application')
def step_impl(context):
    # Login is handled in the previous step
    # Wait for page load
    context.page.wait_for_load_state('networkidle')

@then('I should see a "Welcome {name}" message for {duration:d}ms')
def step_impl(context, name, duration):
    # Verify welcome message
    welcome_message = context.page.locator('.welcome-message')
    expect(welcome_message).to_be_visible()
    expect(welcome_message).to_contain_text(f"Welcome {name}")
    
    # Verify duration
    start_time = time.time()
    context.page.wait_for_selector('.welcome-message', state='hidden')
    end_time = time.time()
    actual_duration = (end_time - start_time) * 1000
    assert abs(actual_duration - duration) < 100  # Allow 100ms tolerance

@then('the screen transitions to "Let\'s Get Started" view')
def step_impl(context):
    start_screen = context.page.locator('.lets-get-started')
    expect(start_screen).to_be_visible()
    expect(start_screen).to_contain_text("Let's Get Started")

@when('I click the "{button_name}" button')
def step_impl(context, button_name):
    context.page.click(f'button:text("{button_name}")')

@then('I am redirected to the "{page_name}" page')
def step_impl(context, page_name):
    if page_name == "My schools → Roster":
        expect(context.page).to_have_url(f"{context.base_url}/schools/roster")
    elif page_name == "Home":
        expect(context.page).to_have_url(f"{context.base_url}/home")

@then('no welcome screen is displayed')
def step_impl(context):
    welcome_message = context.page.locator('.welcome-message')
    expect(welcome_message).not_to_be_visible()

# Add more step definitions for other scenarios...
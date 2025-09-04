import json
import secrets
import string
from datetime import datetime
from typing import Dict, List, Any, Optional
from faker import Faker
from crewai_tools import BaseTool
from ..core.config_manager import config, logger
from ..utils.edge_case_generator import EdgeCaseGenerator


class UltimateTestDataGenerator(BaseTool):
    name: str = "Ultimate Test Data Generator"
    description: str = "Advanced test data generation with ML-powered realistic data, internationalization, and edge case coverage."

    def __init__(self):
        super().__init__()
        self.faker = Faker()
        self.localized_fakers = {
            'en_US': Faker('en_US'),
            'en_GB': Faker('en_GB'),
            'de_DE': Faker('de_DE'),
            'fr_FR': Faker('fr_FR'),
            'ja_JP': Faker('ja_JP')
        }
        self.edge_case_generator = EdgeCaseGenerator()

    def _run(self, data_type: str, count: int = 1, locale: str = 'en_US',
             include_edge_cases: bool = True, custom_constraints: str = None) -> str:
        """Generate advanced test data with comprehensive options"""
        try:
            faker = self.localized_fakers.get(locale, self.faker)

            data_generators = {
                'personal': self._generate_personal_data,
                'business': self._generate_business_data,
                'contact_form': self._generate_contact_form_data,
                'registration': self._generate_registration_data,
                'payment': self._generate_payment_data,
                'address': self._generate_address_data,
                'edge_cases': self._generate_edge_cases,
                'performance_test': self._generate_performance_test_data
            }

            if data_type not in data_generators:
                return f"Unsupported data type: {data_type}. Available: {list(data_generators.keys())}"

            generated_data = []
            for i in range(count):
                base_data = data_generators[data_type](faker)

                if include_edge_cases and i % 5 == 0:
                    edge_cases = self.edge_case_generator.generate_for_type(data_type)
                    base_data.update(edge_cases)

                if custom_constraints:
                    base_data = self._apply_constraints(base_data, custom_constraints)

                generated_data.append(base_data)

            result = {
                'data': generated_data,
                'metadata': {
                    'count': count,
                    'locale': locale,
                    'data_type': data_type,
                    'includes_edge_cases': include_edge_cases,
                    'generation_time': datetime.now().isoformat()
                }
            }

            return json.dumps(result, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Error generating test data: {e}")
            return f"Error generating test data: {e}"

    def _generate_personal_data(self, faker) -> Dict:
        """Generate comprehensive personal data"""
        return {
            'firstname': faker.first_name(),
            'lastname': faker.last_name(),
            'email': faker.email(),
            'phone': faker.phone_number(),
            'date_of_birth': faker.date_of_birth(minimum_age=18, maximum_age=80).isoformat(),
            'ssn': faker.ssn() if hasattr(faker, 'ssn') else faker.random_number(digits=9),
            'username': faker.user_name(),
            'password': self._generate_secure_password(),
            'gender': faker.random_element(['Male', 'Female', 'Other']),
            'nationality': faker.country()
        }

    def _generate_secure_password(self) -> str:
        """Generate secure password meeting common requirements"""
        lowercase = secrets.choice(string.ascii_lowercase)
        uppercase = secrets.choice(string.ascii_uppercase)
        digit = secrets.choice(string.digits)
        special = secrets.choice('!@#$%^&*')

        remaining_length = secrets.randbelow(8) + 8
        remaining = ''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%^&*')
                           for _ in range(remaining_length - 4))

        password = lowercase + uppercase + digit + special + remaining
        password_list = list(password)
        secrets.SystemRandom().shuffle(password_list)
        return ''.join(password_list)

    def _generate_business_data(self, faker) -> Dict:
        """Generate business-related test data"""
        return {
            'company_name': faker.company(),
            'job_title': faker.job(),
            'work_email': faker.company_email(),
            'website': faker.url(),
            'phone': faker.phone_number(),
            'tax_id': faker.random_number(digits=9),
            'industry': faker.random_element(['Technology', 'Healthcare', 'Finance', 'Education', 'Retail']),
            'employee_count': faker.random_element(['1-10', '11-50', '51-200', '201-1000', '1000+'])
        }

    def _generate_contact_form_data(self, faker) -> Dict:
        """Generate contact form specific data"""
        return {
            'name': faker.name(),
            'email': faker.email(),
            'phone': faker.phone_number(),
            'subject': faker.catch_phrase(),
            'message': faker.paragraph(nb_sentences=5),
            'company': faker.company(),
            'interest_level': faker.random_element(['Low', 'Medium', 'High']),
            'preferred_contact': faker.random_element(['Email', 'Phone', 'Text'])
        }

    def _generate_registration_data(self, faker) -> Dict:
        """Generate registration form data"""
        password = self._generate_secure_password()
        return {
            'firstname': faker.first_name(),
            'lastname': faker.last_name(),
            'username': faker.user_name(),
            'email': faker.email(),
            'password': password,
            'confirm_password': password,
            'terms_accepted': True,
            'newsletter_signup': faker.boolean(),
            'security_question': 'What is your pet\'s name?',
            'security_answer': faker.first_name()
        }

    def _generate_payment_data(self, faker) -> Dict:
        """Generate payment form data"""
        return {
            'cardholder_name': faker.name(),
            'card_number': faker.credit_card_number(),
            'expiry_month': faker.random_int(1, 12),
            'expiry_year': faker.random_int(2024, 2030),
            'cvv': faker.random_number(digits=3),
            'billing_address': faker.address(),
            'billing_city': faker.city(),
            'billing_zip': faker.zipcode(),
            'billing_country': faker.country_code()
        }

    def _generate_address_data(self, faker) -> Dict:
        """Generate comprehensive address data"""
        return {
            'street_address': faker.street_address(),
            'apartment': faker.secondary_address(),
            'city': faker.city(),
            'state': faker.state(),
            'zip_code': faker.zipcode(),
            'country': faker.country(),
            'latitude': float(faker.latitude()),
            'longitude': float(faker.longitude())
        }

    def _generate_edge_cases(self, faker) -> Dict:
        """Generate edge case test data"""
        return self.edge_case_generator.generate_comprehensive_edge_cases()

    def _generate_performance_test_data(self, faker) -> Dict:
        """Generate data for performance testing"""
        return {
            'large_text': faker.text(max_nb_chars=10000),
            'repeated_field': faker.word() * 100,
            'special_characters': '!@#$%^&*()_+-=[]{}|;:,.<>?',
            'unicode_text': '测试数据 тестовые данные テストデータ',
            'long_email': f"{'a' * 50}@{'b' * 50}.com",
            'numeric_string': ''.join([str(faker.random_digit()) for _ in range(50)])
        }

    def _apply_constraints(self, data: Dict, constraints: str) -> Dict:
        """Apply custom constraints to generated data"""
        try:
            constraint_rules = json.loads(constraints)
            for field, rule in constraint_rules.items():
                if field in data:
                    if 'max_length' in rule:
                        data[field] = str(data[field])[:rule['max_length']]
                    if 'prefix' in rule:
                        data[field] = rule['prefix'] + str(data[field])
        except Exception as e:
            logger.warning(f"Failed to apply constraints: {e}")
        return data
from faker import Faker


class EdgeCaseGenerator:
    """Specialized generator for edge cases and boundary testing"""

    def __init__(self):
        self.faker = Faker()
        self.edge_cases = {
            'strings': [
                '',
                ' ',
                'a' * 1000,
                '!@#$%^&*()',
                '<script>alert("test")</script>',
                'SELECT * FROM users',
                '../../etc/passwd',
                '\n\r\t',
                '👨‍💻🚀🎯',
                'ñáéíóú',
            ],
            'emails': [
                '',
                'invalid',
                'test@',
                '@example.com',
                'test@example',
                'a' * 100 + '@example.com',
                'test@' + 'a' * 100 + '.com',
                'test@example.com' + 'a' * 100,
                'test+edge@example.com',
                'test..dot@example.com',
            ],
            'numbers': [
                -1,
                0,
                1,
                999999999,
                -999999999,
                3.14159,
                float('inf'),
                float('-inf'),
                float('nan')
            ],
            'dates': [
                '0000-00-00',
                '2023-02-30',
                '2023-13-01',
                '2023-01-32',
                '1970-01-01',
                '2038-01-19',
                '9999-12-31',
                '10000-01-01'
            ]
        }

    def generate_edge_cases(self, field_type: str, count: int = 5) -> list:
        """Generate edge cases for specific field types"""
        if field_type in self.edge_cases:
            return self.edge_cases[field_type][:count]
        else:
            return [self.faker.word() for _ in range(count)]

    def generate_sql_injection_payloads(self) -> list:
        """Generate SQL injection test payloads"""
        return [
            "' OR '1'='1",
            "' UNION SELECT NULL--",
            "'; DROP TABLE users; --",
            "' OR 1=1--",
            "admin'--",
            "' OR 'a'='a",
            "' OR 1=1#",
            "'/**/OR/**/1=1--",
            "' UNION SELECT username, password FROM users--",
            "' OR ASCII(SUBSTRING((SELECT TOP 1 name FROM sysobjects),1,1))>0--"
        ]

    def generate_xss_payloads(self) -> list:
        """Generate XSS test payloads"""
        return [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')",
            "<body onload=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')>",
            "<input onfocus=alert('XSS') autofocus>",
            "<details open ontoggle=alert('XSS')>",
            "<video><source onerror=alert('XSS')>",
            "<marquee onstart=alert('XSS')>"
        ]

    def generate_path_traversal_payloads(self) -> list:
        """Generate path traversal test payloads"""
        return [
            "../../../../etc/passwd",
            "..\\..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            "....//....//....//etc/passwd",
            "..\\/..\\/..\\/..\\/etc/passwd",
            "..%255c..%255c..%255c..%255cwindows\\system32\\drivers\\etc\\hosts",
            "..%c0%af..%c0%af..%c0%af..%c0%afetc/passwd"
        ]
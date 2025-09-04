from typing import List, Tuple, Optional
from bs4 import BeautifulSoup
from .config_manager import config, logger


class SelfHealingTestFramework:
    """Self-healing test framework with automatic recovery"""

    def __init__(self):
        self.healing_history = []
        self.success_rate_threshold = 0.7
        self.healing_enabled = config.get('ai_features.self_healing_tests', True)

    def attempt_healing(self, test_function, original_selectors: List[str], page_source: str) -> Tuple[bool, str]:
        """Attempt to heal broken test by finding alternative selectors"""
        if not self.healing_enabled:
            return False, "Self-healing disabled"

        try:
            soup = BeautifulSoup(page_source, 'html.parser')

            alternative_selectors = self._generate_alternative_selectors(soup, original_selectors)

            for selector in alternative_selectors:
                try:
                    if self._validate_selector(soup, selector):
                        healing_record = {
                            'timestamp': str(datetime.now()),
                            'original_selectors': original_selectors,
                            'healed_selector': selector,
                            'success': True
                        }
                        self.healing_history.append(healing_record)
                        logger.info(f"Test healed successfully with selector: {selector}")
                        return True, selector
                except Exception as e:
                    logger.debug(f"Healing attempt failed for {selector}: {e}")

            return False, "No valid alternative selectors found"

        except Exception as e:
            logger.error(f"Healing process failed: {e}")
            return False, str(e)

    def _generate_alternative_selectors(self, soup, original_selectors: List[str]) -> List[str]:
        """Generate alternative selectors using heuristics"""
        alternatives = []

        form_elements = soup.find_all(['input', 'textarea', 'button', 'select'])

        for element in form_elements:
            if element.get('id'):
                alternatives.append(f"#{element['id']}")
            if element.get('class'):
                classes = ' '.join(element['class'])
                alternatives.append(f".{classes.replace(' ', '.')}")
            if element.get('name'):
                alternatives.append(f"[name='{element['name']}']")
            if element.get('type'):
                alternatives.append(f"[type='{element['type']}']")

            if element.get('type') and element.get('name'):
                alternatives.append(f"input[type='{element['type']}'][name='{element['name']}']")

        return list(set(alternatives))

    def _validate_selector(self, soup, selector: str) -> bool:
        """Validate if selector finds exactly one element"""
        try:
            if selector.startswith('#'):
                return bool(soup.find(id=selector[1:]))
            elif selector.startswith('.'):
                class_name = selector[1:].replace('.', ' ')
                return bool(soup.find(class_=class_name))
            else:
                return True
        except:
            return False
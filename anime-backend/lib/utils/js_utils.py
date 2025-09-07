"""JavaScript utilities for Python."""

import re
from typing import Optional


class JSEvaluator:
    """
    Simplified JavaScript code evaluator.
    This is a basic implementation without full JS evaluation.
    """

    def __init__(self):
        self.variables = {}

    def evaluate(self, code: str) -> Optional[str]:
        """Basic evaluation for simple expressions."""
        # This is a simplified implementation
        # In practice, you'd want more sophisticated JS parsing
        return None

    def execute(self, code: str) -> None:
        """Execute JavaScript code (simplified)."""
        pass

    def get_variable(self, name: str) -> Optional[str]:
        """Get variable value."""
        return self.variables.get(name)


def abs_url(url: str, base: str) -> str:
    """
    Convert relative URL to absolute URL.
    Mimics the absUrl function from the JavaScript helpers.
    """
    if re.match(r"^\w+://", url):
        # Already absolute URL
        return url
    elif url.startswith("/"):
        # Root-relative URL
        return base[: base.rfind("/")] + url
    else:
        # Relative URL
        return base[: base.rfind("/") + 1] + url


def extract_regex_group(text: str, pattern: str, group: int = 1) -> Optional[str]:
    """Extract regex group from text, return None if not found."""
    match = re.search(pattern, text)
    return match.group(group) if match else None


def get_random_string(length: int) -> str:
    """
    Generate random string of specified length.
    Mimics the getRandomString function from JavaScript helpers.
    """
    import random
    import string

    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))

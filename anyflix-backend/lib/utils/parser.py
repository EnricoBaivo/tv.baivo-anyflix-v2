"""HTML parsing utilities similar to JavaScript Document class."""

from bs4 import BeautifulSoup, NavigableString, Tag


class HTMLElement:
    """Wrapper for BeautifulSoup elements to match JavaScript API."""

    def __init__(self, element: Tag | NavigableString | None) -> None:
        """Initialize with BeautifulSoup element."""
        self._element = element

    @property
    def text(self) -> str:
        """Get element text content."""
        if self._element is None:
            return ""
        if isinstance(self._element, NavigableString):
            return str(self._element).strip()
        return self._element.get_text(strip=True)

    @property
    def outer_html(self) -> str:
        """Get element outer HTML."""
        if self._element is None:
            return ""
        return str(self._element)

    @property
    def outerHtml(self) -> str:
        """Alias for outer_html to match JS API."""
        return self.outer_html

    def attr(self, name: str) -> str:
        """Get attribute value.

        Args:
            name: Attribute name

        Returns:
            Attribute value or empty string if not found
        """
        if self._element is None or isinstance(self._element, NavigableString):
            return ""
        return self._element.get(name, "")

    def select(self, selector: str) -> list["HTMLElement"]:
        """Select elements using CSS selector.

        Args:
            selector: CSS selector

        Returns:
            List of HTMLElement objects
        """
        if self._element is None or isinstance(self._element, NavigableString):
            return []
        elements = self._element.select(selector)
        return [HTMLElement(el) for el in elements]

    def select_first(self, selector: str) -> "HTMLElement":
        """Select first element using CSS selector.

        Args:
            selector: CSS selector

        Returns:
            HTMLElement object or empty element if not found
        """
        if self._element is None or isinstance(self._element, NavigableString):
            return HTMLElement(None)
        element = self._element.select_one(selector)
        return HTMLElement(element)

    def selectFirst(self, selector: str) -> "HTMLElement":
        """Alias for select_first to match JS API."""
        return self.select_first(selector)

    @property
    def get_href(self) -> str:
        """Get href attribute."""
        return self.attr("href")

    @property
    def getHref(self) -> str:
        """Alias for get_href to match JS API."""
        return self.get_href

    @property
    def get_src(self) -> str:
        """Get src attribute."""
        return self.attr("src")

    @property
    def getSrc(self) -> str:
        """Alias for get_src to match JS API."""
        return self.get_src

    def filter(self, condition) -> list["HTMLElement"]:
        """Filter elements based on condition.

        Args:
            condition: Function that takes HTMLElement and returns bool

        Returns:
            Filtered list of HTMLElement objects
        """
        # This is a simplified version - in JS this would filter a collection
        # For now, return self if condition is true, empty list otherwise
        if condition(self):
            return [self]
        return []


class HTMLParser:
    """HTML document parser similar to JavaScript Document class."""

    def __init__(self, html: str) -> None:
        """Initialize with HTML string.

        Args:
            html: HTML content to parse
        """
        self.soup = BeautifulSoup(html, "lxml")

    def select(self, selector: str) -> list[HTMLElement]:
        """Select elements using CSS selector.

        Args:
            selector: CSS selector

        Returns:
            List of HTMLElement objects
        """
        elements = self.soup.select(selector)
        return [HTMLElement(el) for el in elements]

    def select_first(self, selector: str) -> HTMLElement:
        """Select first element using CSS selector.

        Args:
            selector: CSS selector

        Returns:
            HTMLElement object or empty element if not found
        """
        element = self.soup.select_one(selector)
        return HTMLElement(element)

    def selectFirst(self, selector: str) -> HTMLElement:
        """Alias for select_first to match JS API."""
        return self.select_first(selector)


# Alias to match JavaScript API
Document = HTMLParser

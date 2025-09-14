"""HTTP client wrapper similar to the JavaScript Client class."""

import asyncio
from typing import Any

import cloudscraper
import httpx
from httpx import Response


class HTTPClient:
    """HTTP client wrapper for making requests."""

    def __init__(
        self,
        follow_redirects: bool = True,
        use_cloudscraper: bool = True,
    ) -> None:
        """Initialize HTTP client.

        Args:
            follow_redirects: Whether to follow redirects automatically
            use_cloudscraper: Whether to use cloudscraper for Cloudflare bypass
        """
        self.follow_redirects = follow_redirects
        self.use_cloudscraper = use_cloudscraper
        self._client: httpx.AsyncClient | None = None
        self._cloudscraper_session = None
        self._create_session()

    def _create_session(self):
        """Create HTTP client session."""
        self._client = httpx.AsyncClient(
            follow_redirects=self.follow_redirects,
            timeout=30.0,
        )

    async def __aenter__(self):
        """Async context manager entry."""
        if self._client is None:
            self._create_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        """Get HTTP client."""
        if self._client is None:
            self._create_session()
        return self._client

    async def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, str] | None = None,
    ) -> "ClientResponse":
        """Make GET request with Cloudflare bypass if needed.

        Args:
            url: URL to request
            headers: Optional headers
            params: Optional query parameters

        Returns:
            ClientResponse object
        """
        if headers is None:
            headers = {}

        # Add default user agent if not present
        if "User-Agent" not in headers and "user-agent" not in headers:
            headers["User-Agent"] = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0"
            )

        # Try normal request first
        try:
            response = await self.client.get(url, headers=headers, params=params)
            client_response = ClientResponse(response)

            # Check if we got blocked by Cloudflare
            if self._is_cloudflare_blocked(client_response):
                if self.use_cloudscraper:
                    # Fallback to cloudscraper
                    return await self._get_with_cloudscraper(url, headers, params)
                # Try with enhanced headers
                return await self._get_with_enhanced_headers(url, headers, params)

        except Exception:
            if self.use_cloudscraper:
                # Try cloudscraper as fallback
                return await self._get_with_cloudscraper(url, headers, params)
            raise
        return client_response

    async def post(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        data: dict[str, Any] | str | None = None,
    ) -> "ClientResponse":
        """Make POST request.

        Args:
            url: URL to request
            headers: Optional headers
            data: Optional data to send

        Returns:
            ClientResponse object
        """
        if headers is None:
            headers = {}

        response = await self.client.post(url, headers=headers, data=data)
        return ClientResponse(response)

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    def _is_cloudflare_blocked(self, response: "ClientResponse") -> bool:
        """Check if response indicates Cloudflare blocking.

        Args:
            response: HTTP response to check

        Returns:
            True if blocked by Cloudflare
        """
        if response.status_code in [403, 429, 503]:
            return True

        content = response.body.lower()

        cloudflare_indicators = [
            "challenge-platform",
            "cf-challenge",
            "checking your browser",
            "please wait",
            "security check",
            "bot",
            "ddos protection",
        ]

        return any(indicator in content for indicator in cloudflare_indicators)

    async def _get_with_cloudscraper(
        self, url: str, headers: dict[str, str], params: dict[str, str] | None = None
    ) -> "ClientResponse":
        """Make request using cloudscraper for Cloudflare bypass.

        Args:
            url: URL to request
            headers: Request headers
            params: Optional query parameters

        Returns:
            ClientResponse object
        """
        if not self._cloudscraper_session:
            self._cloudscraper_session = cloudscraper.create_scraper(
                browser={"browser": "chrome", "platform": "windows", "mobile": False}
            )

        # Run cloudscraper in thread pool since it's sync
        loop = asyncio.get_event_loop()

        def _sync_request():
            return self._cloudscraper_session.get(url, headers=headers, params=params)

        response = await loop.run_in_executor(None, _sync_request)

        # Convert to our ClientResponse format
        return CloudflareClientResponse(response)

    async def _get_with_enhanced_headers(
        self, url: str, headers: dict[str, str], params: dict[str, str] | None = None
    ) -> "ClientResponse":
        """Make request with enhanced anti-detection headers.

        Args:
            url: URL to request
            headers: Base headers
            params: Optional query parameters

        Returns:
            ClientResponse object
        """
        enhanced_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Cache-Control": "max-age=0",
        }

        # Merge with provided headers
        enhanced_headers.update(headers)

        # Add small delay to seem more human-like
        await asyncio.sleep(0.5)

        response = await self.client.get(url, headers=enhanced_headers, params=params)
        return ClientResponse(response)


class ClientResponse:
    """Wrapper for HTTP response to match JavaScript API."""

    def __init__(self, response: Response) -> None:
        """Initialize with httpx Response."""
        self._response = response

    @property
    def body(self) -> str:
        """Get response body as string."""
        return self._response.text

    @property
    def status_code(self) -> int:
        """Get response status code."""
        return self._response.status_code

    @property
    def statusCode(self) -> int:
        """Alias for status_code to match JS API."""
        return self.status_code

    @property
    def headers(self) -> dict[str, str]:
        """Get response headers."""
        return dict(self._response.headers)

    @property
    def request(self) -> "ClientRequest":
        """Get request information."""
        return ClientRequest(self._response.request)


class ClientRequest:
    """Wrapper for HTTP request information."""

    def __init__(self, request):
        """Initialize with httpx Request."""
        self._request = request

    @property
    def url(self) -> str:
        """Get request URL."""
        return str(self._request.url)


class CloudflareClientResponse(ClientResponse):
    """Wrapper for cloudscraper response to match our interface."""

    def __init__(self, response):
        """Initialize with cloudscraper response."""
        self._cs_response = response

    @property
    def body(self) -> str:
        """Get response body as string."""
        return self._cs_response.text

    @property
    def status_code(self) -> int:
        """Get response status code."""
        return self._cs_response.status_code

    @property
    def statusCode(self) -> int:
        """Alias for status_code to match JS API."""
        return self.status_code

    @property
    def headers(self) -> dict[str, str]:
        """Get response headers."""
        return dict(self._cs_response.headers)

    @property
    def request(self):
        """Get request information."""

        # Simplified request object
        class SimpleRequest:
            def __init__(self, url):
                self.url = url

        return SimpleRequest(self._cs_response.url)

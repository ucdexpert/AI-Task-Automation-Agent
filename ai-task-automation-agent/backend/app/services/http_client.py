import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class HTTPClient:
    _client: Optional[httpx.AsyncClient] = None

    @classmethod
    async def get_client(cls) -> httpx.AsyncClient:
        if cls._client is None:
            cls._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
            )
            logger.info("✅ Global HTTP Client initialized")
        return cls._client

    @classmethod
    async def close_client(cls):
        if cls._client:
            await cls._client.aclose()
            cls._client = None
            logger.info("👋 Global HTTP Client closed")

http_client = HTTPClient()

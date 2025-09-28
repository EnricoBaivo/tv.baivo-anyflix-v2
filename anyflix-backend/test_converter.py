import asyncio

from app.routers.sources import convert_to_media_spotlight
from lib.models.responses import (
    LatestMediaSpotlightResponse,
    PopularMediaSpotlightResponse,
)
from lib.providers.serienstream import SerienStreamProvider


async def main():
    provider = SerienStreamProvider()
    async with provider:
        popular_response = await provider.get_popular(page=1)
        media_spotlight_list = [
            convert_to_media_spotlight(media_item)
            for media_item in popular_response.list
        ]
        return PopularMediaSpotlightResponse(
            list=media_spotlight_list,
            type=popular_response.type,
            has_next_page=popular_response.has_next_page,
        )


if __name__ == "__main__":
    asyncio.run(main())

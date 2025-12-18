import asyncio

from lib.extractors.ytdlp_extractor import ytdlp_extractor


async def main():
    youtube_url = "https://www.youtube.com/watch?v=f9HwA5IR-sg"
    trailer_sources = await ytdlp_extractor(youtube_url)
    for source in trailer_sources:
        print(f"Source:{source.host} - {source.quality} - {source.format}")


if __name__ == "__main__":
    asyncio.run(main())

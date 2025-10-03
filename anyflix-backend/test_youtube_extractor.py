import asyncio

from lib.extractors.ytdlp_extractor import ytdlp_extractor


async def main():
    youtube_url = "https://www.youtube.com/watch?v=LHtdKWJdif4"
    trailer_response = await ytdlp_extractor(youtube_url)
    print(trailer_response)


if __name__ == "__main__":
    asyncio.run(main())

import asyncio

from lib.extractors.filemoon_extractor import filemoon_extractor
from lib.extractors.vidmoly_extractor import vidmoly_extractor
from lib.extractors.vidoza_extractor import vidoza_extractor
from lib.extractors.voe_extractor import voe_extractor
from lib.extractors.ytdlp_extractor import ytdlp_extractor


async def main():
    # videosrc = ytdlp_extractor("https://www.youtube.com/watch?v=79oqWomZ6x4")
    # print(videosrc)

    voe_source = await voe_extractor("https://voe.sx/e/nrn8djmpn2mm")
    print(voe_source)
    # filemoon_source = await filemoon_extractor("https://filemoon.to/d/iiwums6tekoj")
    # print(filemoon_source)
    # vidmoly_source = await vidmoly_extractor(
    #    "https://vidmoly.net/embed-16jl3rm2nwfj.html"
    # )
    # print(vidmoly_source)
    # vidoza_source = await vidoza_extractor("https://vidoza.net/embed-16jl3rm2nwfj.html")
    # print(vidoza_source)


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Add current directory to path so we can import lib
sys.path.append(os.getcwd())

import pydoc
print(f"Locating PydanticSerializer: {pydoc.locate('lib.utils.caching.PydanticSerializer')}")

from lib.utils.caching import cached, initialize_cache
from aiocache import caches
from pydantic import BaseModel

class MyModel(BaseModel):
    name: str

# Initialize cache explicitly
initialize_cache()

@cached(ttl=60, key_prefix="test_model")
async def get_model():
    return MyModel(name="test")

async def main():
    print("First call (should cache)...")
    res1 = await get_model()
    print(f"Res1 type: {type(res1)}")
    print(f"Res1: {res1}")
    
    # Check serializer
    cache = caches.get("default")
    print(f"Cache type: {type(cache)}")
    if hasattr(cache, "serializer"):
        print(f"Serializer: {cache.serializer}")
        if cache.serializer:
            print(f"Serializer class: {cache.serializer.__class__}")
    
    print("\nSecond call (should hit cache)...")
    res2 = await get_model()
    print(f"Res2 type: {type(res2)}")
    print(f"Res2: {res2}")

if __name__ == "__main__":
    asyncio.run(main())

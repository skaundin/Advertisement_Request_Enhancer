import asyncio
import time
import aiohttp
import json


async def invoke_inject_ad(session, url, payload):
    async with session.post(url, data=payload) as response:
        print(response)


async def call_inject_ads(url, payload, count):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(count):
            task = asyncio.ensure_future(
                invoke_inject_ad(session, url, payload))
            tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    url = "http://localhost:5000/inject_ad"
    payload = {
        "site": {
            "id": "foo123",
            "page": "http://www.foo.com/why-foo"},
        "device": {
            "ip": "69.250.196.118"
        }, "user": {
            "id": "9cb89r"}
    }
    count = 2
    start_time = time.time()
    asyncio.get_event_loop().run_until_complete(
        call_inject_ads(url, payload, count))
    duration = time.time() - start_time
    print(f"Invoked {count} sites in {duration} seconds")

import aiohttp
import asyncio

async def delete_stock(session, id):
    async with session.delete(f"http://localhost:80/stocks/{id}") as resp:
        print(f"Status: {resp.status}, Response: {await resp.text()}")

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [delete_stock(session, "67979b2b19e57c7bfc863607") for _ in range(2)]
        await asyncio.gather(*tasks)

asyncio.run(main())
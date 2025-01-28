import aiohttp
import asyncio

async def delete_stock(session, id):
    async with session.delete(f"http://localhost:80/stocks/{id}") as resp:
        print(f"Status: {resp.status}, Response: {await resp.text()}")

async def update_stock(session, stock_id, updated_data):
    async with session.put(
        f"http://localhost:80/stocks/{stock_id}",
        json=updated_data
    ) as resp:
        print(f"Status: {resp.status}, Response: {await resp.text()}")

async def insert_stock(session, data):
    async with session.post(
        "http://localhost:80/stocks",
        json=data
    ) as resp:
        print(f"Status: {resp.status}, Response: {await resp.text()}")

async def main():
    stock_id = "6797aeb11488fab922a2fe1a"
    
    # Two different payloads to update different fields
    payload_1 = {
        "symbol": "AMZN",
        "name": "Amazon Inc. 1",
        "purchase price": 400.00,
        "purchase date": "02-01-2024",
        "shares": 20  # Changed from 15 to 20
    }
    
    payload_2 = {
        "symbol": "AMZN",
        "name": "Amazon Inc. 2",
        "purchase price": 400.00,  # Changed from 400 to 410
        "purchase date": "02-01-2024",
        "shares": 20
    }
    
    async with aiohttp.ClientSession() as session:
        tasks = [
            insert_stock(session, payload_1),
            insert_stock(session, payload_2),
        ]
        await asyncio.gather(*tasks)

asyncio.run(main())
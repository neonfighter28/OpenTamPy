"""
This example demonstrates getting all students from the school and printing their ID and Names
"""

from OpenTamPy import AsyncClient
from creds import username, password, school
import asyncio

instance = AsyncClient(username, password, school)

async def main():
    resources = await instance.get_resources()
    print("ID ---- | Name ---------------------")
    for item in resources.students:
        print(f"{item.personId} | {item.name}")

asyncio.run(main())

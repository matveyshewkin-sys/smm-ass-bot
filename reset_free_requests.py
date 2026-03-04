import asyncio
from db import async_session, User

USER_ID = 1600876942  
FREE_REQUESTS = 5000  

async def reset_free_requests():
    async with async_session() as session:
        user = await session.get(User, USER_ID)
        if not user:
            print(f"Пользователь с id {USER_ID} не найден.")
            return
        user.free_requests = FREE_REQUESTS
        await session.commit()
        print(f"✅ У пользователя {USER_ID} теперь {FREE_REQUESTS} бесплатных запросов.")

if name == "__main__":
    asyncio.run(reset_free_requests())
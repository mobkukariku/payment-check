import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from services.database import init_db
from handlers import tip, paycheck, start, stats, pagination, chatgpt
from services.dependencies import get_session


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.workflow_data.update(session=await anext(get_session()))

    dp.include_router(start.router)
    dp.include_router(tip.router)
    dp.include_router(paycheck.router)
    dp.include_router(stats.router)
    dp.include_router(pagination.router)
    dp.include_router(chatgpt.router)


    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

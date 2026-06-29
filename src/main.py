import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN
from handlers import start, messages, inline


async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties())
    dp = Dispatcher()

    dp.include_router(inline.router)
    dp.include_router(start.router)
    dp.include_router(messages.router)

    print("🚀 Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
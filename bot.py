import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEB_URL = os.getenv("WEB_URL")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is missing")

if not WEB_URL:
    raise ValueError("WEB_URL environment variable is missing")

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: types.Message):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Open Mini App",
                    web_app=WebAppInfo(url=WEB_URL)
                )
            ]
        ]
    )

    await message.answer(
        "👋 Welcome to THE GYANI!\n\n"
        "📝 Data Interpretation Subject Test 1\n\n"
        "Test शुरू करने के लिए नीचे क्लिक करें 👇",
        reply_markup=keyboard
    )


async def home(request):
    return web.FileResponse("web/index.html")


async def health(request):
    return web.Response(text="OK")


async def main():

    app = web.Application()

    app.router.add_get("/", home)
    app.router.add_get("/health", health)

    port = int(os.getenv("PORT", "10000"))

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(
        runner,
        "0.0.0.0",
        port
    )

    await site.start()

    print(f"Web server running on port {port}")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

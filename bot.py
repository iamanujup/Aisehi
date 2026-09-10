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

BOT_TOKEN = os.getenv("8897171827:AAHf2DId-RH5okEpJuV3E9hvbnHNnlVglmg")
WEB_URL = os.getenv("WEB_URL")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@the_gyani")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is missing")

if not WEB_URL:
    raise ValueError("WEB_URL environment variable is missing")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# -------------------------
# Telegram /start
# -------------------------

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
        "👋 Welcome!\n\n"
        "हमारे TEST को खोलने के लिए नीचे क्लिक करें 👇",
        reply_markup=keyboard
    )


# -------------------------
# Check Channel Membership
# -------------------------

async def check_membership(user_id: int):

    try:

        member = await bot.get_chat_member(
            chat_id=CHANNEL_USERNAME,
            user_id=user_id
        )

        return member.status in {
            "creator",
            "administrator",
            "member"
        }

    except Exception as e:

        print("Membership error:", e)

        return False


# -------------------------
# Web App
# -------------------------

async def home(request):

    with open("web/index.html", "r", encoding="utf-8") as f:
        html = f.read()

    channel = CHANNEL_USERNAME.replace("@", "")

    html = html.replace(
        "__CHANNEL_USERNAME__",
        channel
    )

    return web.Response(
        text=html,
        content_type="text/html"
    )


# -------------------------
# API: Check Joined
# -------------------------

async def check_joined(request):

    user_id = request.query.get("user_id")

    if not user_id:
        return web.json_response({
            "joined": False,
            "error": "User ID missing"
        })

    try:

        user_id = int(user_id)

    except ValueError:

        return web.json_response({
            "joined": False,
            "error": "Invalid user ID"
        })

    joined = await check_membership(user_id)

    return web.json_response({
        "joined": joined
    })


# -------------------------
# Health Check
# -------------------------

async def health(request):

    return web.Response(text="OK")


# -------------------------
# Start Web Server
# -------------------------

async def start_web_server():

    app = web.Application()

    app.router.add_get("/", home)
    app.router.add_get("/health", health)
    app.router.add_get("/api/check", check_joined)

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


# -------------------------
# Main
# -------------------------

async def main():

    await start_web_server()

    print("Telegram bot started")

    await dp.start_polling(bot)


if __name__ == "__main__":

    asyncio.run(main())

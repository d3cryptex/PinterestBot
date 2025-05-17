import asyncio
from os import environ
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command

token = environ.get("TOKEN")

bot = Bot(token=token)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: Message):
    desc = "👋 Hi! I'm a bot that will help you download images and videos from Pinterest.\n\n" \
    "🔗 Just send me the link to the pin or boards and I'll do it"
    await message.answer(desc)

async def main():
    print("Бот запущено! ⚡")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

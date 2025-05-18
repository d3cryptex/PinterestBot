import asyncio
import aiohttp
import os
import yt_dlp
import uuid

from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command

token = os.environ.get("TOKEN")

bot = Bot(token=token)
dp = Dispatcher()

async def download_mp4(url: str):
    filename = f"media_{uuid.uuid4().hex[:8]}.mp4"
    output_path = os.path.join("downloads", filename)
    os.makedirs("downloads", exist_ok=True)

    ydl_opts = {
        'format': 'mp4/best',
        'outtmpl': output_path,
        'quiet': True,
        'noplaylist': True,
        'merge_output_format': 'mp4',
    }

    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(
            None,
            lambda: yt_dlp.YoutubeDL(ydl_opts).download([url])
        )
        if os.path.exists(output_path):
            return output_path
        else:
            return None
    except Exception as e:
        print(f"❌ yt-dlp download error: {e}")
        return None

async def download_image(url: str):
    async with aiohttp.ClientSession() as session:
        headers = {"User-Agent": "Mozilla/5.0"}
        async with session.get(url, headers=headers) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            img_tag = soup.find("img", {"class": "hCL kVc L4E MIw"})
            if img_tag and img_tag.get("src"):
                return img_tag["src"]
            return None

@dp.message(Command("start"))
async def start_handler(message: Message):
    desc = "👋 Hi! I'm a bot that will help you download images and videos from Pinterest.\n\n" \
    "🔗 Just send me the link to the pin or boards and I'll do it"
    await message.answer(desc)

@dp.message()
async def link_from_user(message: Message):
    user_link = message.text

    if "pin.it" not in user_link and "pinterest.com" not in user_link:
        await message.answer("❌ Please enter your pinterest link to pin\n Example: pin.it or www.pinterest.com/pin/...")
        return
    
    await message.answer("⏳ Checking link...")

    video_file = await download_mp4(user_link)
    if video_file and os.path.exists(video_file):
        video_input = FSInputFile(path=video_file)
        await message.answer_video(video=video_input, caption="🎥 Here's your video!")
        os.remove(video_file)
    else:
        image_url = await download_image(user_link)
        if image_url:
            await message.answer_photo(image_url, caption="🎴 Here's your image!")
        else:
            await message.answer("❌ Couldn't find video or image on the link.")

async def main():
    print("Bot is working!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

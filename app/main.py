import asyncio
import aiohttp
import os
import yt_dlp
import uuid
import time
import re

from urllib.parse import urlparse
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, FSInputFile, InputMediaPhoto, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command

token = os.environ.get("TOKEN")

bot = Bot(token=token)
dp = Dispatcher()

user_albums = {}

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

async def resolve_short_url(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, allow_redirects=True) as response:
                return str(response.url)
        except Exception as e:
            print(f"❌ Error resolving short URL: {e}")
            return url 

@dp.message(Command("start"))
async def start_handler(message: Message):
    desc = "👋 Hi! I'm a bot that will help you download images and videos from Pinterest.\n\n" \
    "🔗 Just send me the link to the pin or boards and I'll do it"
    await message.answer(desc)

@dp.message()
async def link_from_user(message: Message):
    user_links = re.findall(r'(https?://\S+)', message.text)

    if not user_links:
        await message.answer("❌ I didn't find any link in the message.")
        return

    await message.answer(f"🔍 Found {len(user_links)} links. Processing...")

    media_group = []

    for link in user_links:
        link = await resolve_short_url(link)

        if "pin.it" not in link and "pinterest.com" not in link:
            await message.answer(f"❌ This is not a Pinterest link: {link}")
            continue

        video_file = await download_mp4(link)
        if video_file and os.path.exists(video_file):
            media_group.append({
                "type": "video",
                "path": video_file
            })
        else:
            image_url = await download_image(link)
            if image_url:
                media_group.append({
                    "type": "photo",
                    "url": image_url
                })
            else:
                await message.answer(f"⚠️ I didn't find anything at the link: {link}")

    if media_group:
        user_albums[message.from_user.id] = {
            "media": media_group,
            "index": 0
        }
        await send_media_with_buttons(message, message.from_user.id)

async def send_media_with_buttons(message: Message, user_id: int):
    album = user_albums[user_id]
    index = album["index"]
    media_item = album["media"][index]

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️", callback_data="prev"),
            InlineKeyboardButton(text=f"{index + 1}/{len(album['media'])}", callback_data="noop"),
            InlineKeyboardButton(text="➡️", callback_data="next")
        ]
    ])

    if media_item["type"] == "photo":
        await message.answer_photo(
            photo=media_item["url"],
            caption="📸 Photo from Pinterest:",
            reply_markup=markup
        )
    elif media_item["type"] == "video":
        video_input = FSInputFile(media_item["path"])
        await message.answer_video(
            video=video_input,
            caption="🎬Video from Pinterest:",
            reply_markup=markup
        )

@dp.callback_query()
async def callback_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in user_albums:
        await callback.answer("⛔️ Album not found.")
        return

    album = user_albums[user_id]
    index = album["index"]

    if callback.data == "next":
        if index + 1 < len(album["media"]):
            album["index"] += 1
            await callback.message.delete()
            await send_media_with_buttons(callback.message, user_id)
        else:
            await callback.answer("🚫 This is the latest media.")
    elif callback.data == "prev":
        if index > 0:
            album["index"] -= 1
            await callback.message.delete()
            await send_media_with_buttons(callback.message, user_id)
        else:
            await callback.answer("🚫 This is the first media.")
    elif callback.data == "noop":
        await callback.answer()

async def main():
    print("Bot is working!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

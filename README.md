# PinterestBot

A Telegram bot that helps you download videos and images from Pinterest using just a link. Built with aiogram, yt-dlp, aiohttp, and BeautifulSoup.

## Tech Stack
- [Python 3.10+](https://www.python.org)
- [aiogram 3](https://docs.aiogram.dev/en/dev-3.x/)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [aiohttp](https://docs.aiohttp.org/)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)

## How to Run Locally
### 1. Clone the repository

```bash
git clone https://github.com/d3cryptex/pinterest-bot.git
cd pinterest-bot
```

### 2. Install dependencies

> The `requirements.txt` file is already included.

```bash
python -m venv .venv
.venv\Scripts\activate  # Use `source .venv/bin/activate` on Linux/Mac
pip install -r requirements.txt
```

### 3. Set up environment variable

You can either create a `.env` file or set the variable manually:

**`.env` file:**
```env
TOKEN=your_telegram_bot_token
```

**Or directly in terminal:**
```bash
export TOKEN=your_telegram_bot_token  # Use `set` on Windows
```

### 4. Run the bot

```bash
python app/main.py
```

### 5. Use the bot

Start a chat with your bot, send `/start`, and then paste any Pinterest link (pin or board). It will return either an image or a video.

## Auto-cleaning

The bot deletes video files right after sending them to the user. The `downloads/` directory is created automatically if it doesn’t exist.

## Docker

You can run this bot inside a Docker container.

### Build the Docker image:

```
docker build -t pinterest-bot .
```

### Run the container:

```
docker run -e TOKEN=your_bot_token pinterest-bot
```

## ⚠️ Notes

- **You may need to install `ffmpeg`** on some systems (especially Linux) for proper video handling.
- `yt-dlp` may not support some private or protected Pinterest content.

## License

MIT — free to use, learn, modify, and share!

---

Made with ❤️ to help you **learn by building**.

By **d3cryptex**

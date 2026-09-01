import os
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
import yt_dlp

BOT_TOKEN = "8861166891:AAHqaBz_gibVh9HmpYQ-Osie3COb2du_LcI"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# YouTube uchun Piped API orqali videoni olish (Bloklarni aylanib o'tadi)
async def download_youtube_piped(url: str, output_path: str) -> bool:
    try:
        # Video ID ni ajratib olish
        video_id = ""
        if "shorts/" in url:
            video_id = url.split("shorts/")[1].split("?")[0]
        elif "v=" in url:
            video_id = url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[1].split("?")[0]

        if not video_id:
            return False

        api_url = f"https://pipedapi.kavin.rocks/streams/{video_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    # Ovozli va tasvirli tayyor streamni topish
                    streams = data.get("videoStreams", [])
                    target_url = None
                    for stream in streams:
                        if stream.get("videoOnly") is False and stream.get("mimeType") == "video/mp4":
                            target_url = stream.get("url")
                            break

                    if not target_url and streams:
                        target_url = streams[0].get("url")

                    if target_url:
                        async with session.get(target_url, timeout=30) as v_resp:
                            if v_resp.status == 200:
                                with open(output_path, "wb") as f:
                                    f.write(await v_resp.read())
                                return True
    except Exception:
        pass
    return False

# Instagram/TikTok va zaxira uchun yt-dlp (Faqat 1 ta video yuklash cheklovi bilan)
def download_via_ytdlp(url: str, output_path: str):
    ydl_opts = {
        'format': 'b/best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'playlistend': 1,  # Instagram karuselida faqat 1-videoni olish
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Xush kelibsiz! Instagram, TikTok yoki YouTube video havolasini yuboring.")

@dp.message()
async def process_link(message: types.Message):
    url = message.text.strip()
    
    if not (url.startswith("http://") or url.startswith("https://")):
        await message.answer("Iltimos, to'g'ri link yuboring!")
        return

    msg = await message.answer("⏳ Video yuklanmoqda, kuting...")
    file_path = f"video_{message.from_user.id}.mp4"

    try:
        success = False
        
        # Gar YouTube bo'lsa avval Piped API orqali harakat qilamiz
        if "youtube.com" in url or "youtu.be" in url:
            success = await download_youtube_piped(url, file_path)

        # YouTube API o'xshamasa yoki Instagram/TikTok bo'lsa yt-dlp ishlaydi
        if not success:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, download_via_ytdlp, url, file_path)

        if os.path.exists(file_path):
            video = FSInputFile(file_path)
            await message.answer_video(video, caption="✅ Video tayyor!")
            os.remove(file_path)
            await msg.delete()
        else:
            await msg.edit_text("❌ Videoni saqlab bo'lmadi.")
    except Exception as e:
        await msg.edit_text("❌ Videoni yuklab bo'lmadi. Linkni tekshiring.")
        if os.path.exists(file_path):
            os.remove(file_path)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

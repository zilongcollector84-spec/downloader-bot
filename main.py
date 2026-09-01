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

# Cobalt API orqali yuklab olish (YouTube uchun eng ishonchli usul)
async def download_via_cobalt(url: str, output_path: str) -> bool:
    cobalt_url = "https://api.cobalt.tools/api/json"
    payload = {
        "url": url,
        "videoQuality": "720"
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(cobalt_url, json=payload, headers=headers) as resp:
                data = await resp.json()
                video_link = data.get("url")
                
                if not video_link:
                    return False
                
                async with session.get(video_link) as v_resp:
                    if v_resp.status == 200:
                        with open(output_path, "wb") as f:
                            f.write(await v_resp.read())
                        return True
    except Exception:
        pass
    return False

# Zaxira usul: Instagram va TikTok uchun yt-dlp
def download_via_ytdlp(url: str, output_path: str):
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
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
        # Avval Cobalt API orqali harakat qilamiz
        success = await download_via_cobalt(url, file_path)
        
        # Agar Cobalt’da o'xshamasa, yt-dlp orqali yuklaymiz
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

import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
import yt_dlp

# Bot tokeni
BOT_TOKEN = "8861166891:AAFqt-lvg6Yo782mdQNN51AYxD1OKwiHV6E"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Yuklab olingan fayllar uchun papka
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@dp.message(F.text.startswith("http"))
async def handle_url(message: Message):
    url = message.text.strip()
    status_msg = await message.answer("⏳ Video yuklab olinmoqda, kuting...")
    
    # yt-dlp sozlamalari (YouTube bloklarini aylanib o'tish bilan)
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': f'{DOWNLOAD_DIR}/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web']
            }
        }
    }
    
    filepath = None
    try:
        # Videoni yuklab olish (async fonda)
        loop = asyncio.get_event_loop()
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info)
                
        filepath = await loop.run_in_executor(None, download)
        
        # Telegramga video ko'rinishida yuborish
        video_file = FSInputFile(filepath)
        await message.answer_video(video=video_file, caption="✅ Video yuklab olindi!")
        await status_msg.delete()
        
    except Exception as e:
        logging.error(f"Yuklashda xatolik: {e}")
        await status_msg.edit_text("❌ Videoni yuklab bo'lmadi. Linkni yoki video sozlamalarini tekshiring.")
        
    finally:
        # Server joyini tejash uchun faylni o'chirish
        if filepath and os.path.exists(filepath):
            os.remove(filepath)

@dp.message()
async def start_cmd(message: Message):
    await message.answer("Salom! Menga Instagram, TikTok yoki YouTube Shorts havolasini yuboring.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

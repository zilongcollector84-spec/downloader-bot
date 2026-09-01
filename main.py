import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
import yt_dlp

# Botning yangi to'liq tokeni
BOT_TOKEN = "8861166891:AAHzojupUbGFONXSxq1FD-Q6W2Gy5Cw6o1s"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@dp.message(F.text.startswith("http"))
async def handle_url(message: Message):
    url = message.text.strip()
    status_msg = await message.answer("⏳ Video yuklab olinmoqda, kuting...")
    
    # Audio va videoni sifatli birlashtirish hamda YouTube/Instagram blokini aylanib o'tish sozlamalari
    ydl_opts = {
        'format': 'bestvideo[vcodec^=avc1][ext=mp4]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'outtmpl': f'{DOWNLOAD_DIR}/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios', 'web']
            }
        }
    }
    
    filepath = None
    try:
        loop = asyncio.get_event_loop()
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return ydl.prepare_filename(info)
                
        filepath = await loop.run_in_executor(None, download)
        
        # Format o'zgargan bo'lsa tekshirish
        if not os.path.exists(filepath):
            base, _ = os.path.splitext(filepath)
            if os.path.exists(f"{base}.mp4"):
                filepath = f"{base}.mp4"

        # Telegram fayl hajmi cheklovi (50 MB)
        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        if file_size_mb > 49:
            await status_msg.edit_text("❌ Video hajmi 50 MB dan katta bo'lgani uchun Telegram orqali yuborib bo'lmadi.")
        else:
            video_file = FSInputFile(filepath)
            await message.answer_video(video=video_file, caption="✅ Video yuklab olindi!")
            await status_msg.delete()
        
    except Exception as e:
        logging.error(f"Yuklashda xatolik: {e}")
        await status_msg.edit_text("❌ Videoni yuklab bo'lmadi. Linkni tekshiring.")
        
    finally:
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception:
                pass

@dp.message()
async def start_cmd(message: Message):
    await message.answer("Salom! Menga Instagram, TikTok yoki YouTube Shorts havolasini yuboring.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

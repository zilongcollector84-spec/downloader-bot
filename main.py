import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
import yt_dlp

BOT_TOKEN = "BOT_TOKENINGIZNI_SHUYERGA_YOZING"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def download_video(url: str, output_path: str = "video.mp4"):
    clean_url = url.split("?")[0]
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios']
            }
        }
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([clean_url])

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
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, download_video, url, file_path)

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

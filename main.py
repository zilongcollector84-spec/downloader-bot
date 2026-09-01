import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
import yt_dlp

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def download_video(url: str, output_path: str = "downloaded_video.mp4") -> str:
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return output_path

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("Salom! Menga Instagram, TikTok yoki YouTube video havolasini yuboring.")

@dp.message(F.text.startswith("http://") | F.text.startswith("https://"))
async def handle_link(message: types.Message):
    url = message.text.strip()
    status_msg = await message.answer("⏳ Video yuklanmoqda...")
    file_path = f"video_{message.from_user.id}.mp4"
    
    try:
        await asyncio.to_thread(download_video, url, file_path)
        await status_msg.edit_text("📤 Telegram'ga yuborilmoqda...")
        video_file = types.FSInputFile(file_path)
        await message.answer_video(video=video_file, caption="Video tayyor!")
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text("❌ Videoni yuklab bo'lmadi. Linkni tekshiring.")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

import os
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile
import yt_dlp

BOT_TOKEN = "8861166891:AAFqt-lvg6Yo782mdQNN51AYxD1OKwiHV6E"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Ochiq va faol Cobalt API instansiyalari ro'yxati
COBALT_INSTANCES = [
    "https://cobalt-api.kwiatek.xyz",
    "https://api.cobalt.tools",
    "https://cobalt.qtf.tw",
    "https://co.wuk.sh"
]

async def download_via_cobalt_mirrors(url: str, output_path: str) -> bool:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "url": url,
        "videoQuality": "720"
    }

    async with aiohttp.ClientSession() as session:
        for instance in COBALT_INSTANCES:
            try:
                api_url = f"{instance}/api/json" if not instance.endswith("/api/json") else instance
                async with session.post(api_url, json=payload, headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        video_link = data.get("url")
                        
                        if video_link:
                            async with session.get(video_link, timeout=30) as v_resp:
                                if v_resp.status == 200:
                                    with open(output_path, "wb") as f:
                                        f.write(await v_resp.read())
                                    return True
            except Exception:
                continue  # Bitta server ishlamasa, keyingisiga o'tadi
    return False

# Instagram va TikTok uchun yt-dlp
def download_via_ytdlp(url: str, output_path: str):
    ydl_opts = {
        'format': 'b/best',
        'outtmpl': output_path,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'playlistend': 1,
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
        # Avval instansiyalar orqali harakat qilamiz
        success = await download_via_cobalt_mirrors(url, file_path)
        
        # O'xshasa bo'ldi, bo'lmasa yt-dlp zaxiraga kiradi
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

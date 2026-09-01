FROM python:3.10-slim

# FFmpeg va kerakli paketlarni o'rnatish
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Kutubxonalarni o'rnatish va yt-dlp ni majburiy eng so'nggi versiyaga yangilash
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir --upgrade yt-dlp

COPY . .

CMD ["python", "main.py"]

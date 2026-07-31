FROM python:3.11-slim

WORKDIR /app

# Dependencias del sistema para Pillow y yt-dlp
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]

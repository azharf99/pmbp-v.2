# Gunakan Python versi ringan
FROM python:3.10-slim

# Mencegah Python membuat file .pyc dan memaksanya langsung print log ke terminal
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set direktori kerja
WORKDIR /app

# Instal dependensi sistem yang diwajibkan oleh mysqlclient Django
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Salin file requirements dan instal
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
# Pastikan gunicorn terinstal untuk server produksi
RUN pip install gunicorn 

# Salin seluruh kode aplikasi
COPY . .

# Ekspos port 8000 untuk Gunicorn
EXPOSE 8000

# Perintah dijalankan melalui docker-compose.yml agar bisa menjalankan migrasi otomatis
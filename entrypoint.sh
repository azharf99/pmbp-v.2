#!/bin/bash

# Kumpulkan file statis dan timpa yang lama
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Jalankan server (sesuaikan dengan perintah aslimu)
echo "Starting server..."
exec "$@"
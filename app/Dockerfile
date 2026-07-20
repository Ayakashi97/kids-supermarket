FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (including USB libs for python-escpos if printer used)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libusb-1.0-0-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure data directory exists for SQLite
RUN mkdir -p /app/data /app/static/images/products /app/static/images/cards

EXPOSE 5000

CMD ["python", "run.py"]

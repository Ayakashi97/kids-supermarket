FROM python:3.11-slim

WORKDIR /app_root

# Install system dependencies (including USB libs for python-escpos if printer used)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libusb-1.0-0-dev \
    && rm -rf /var/lib/apt/lists/*

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set PYTHONPATH so app package is importable
ENV PYTHONPATH=/app_root

# Ensure data directory exists for SQLite
RUN mkdir -p /app_root/app/data /app_root/app/static/images/products /app_root/app/static/images/cards

EXPOSE 80 443

CMD ["python", "app/run.py"]

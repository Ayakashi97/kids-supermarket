# 🛠️ Raspberry Pi Hardware & OS Setup Guide

Complete step-by-step setup guide for both Raspberry Pi units in the **Kinder-Supermarkt** system.

---

## 📐 Architecture Overview

| Device | Role | Recommended OS | Connected Hardware |
|---|---|---|---|
| **Raspberry Pi #1** | Backend Server (Flask, DB, Docker) | **Raspberry Pi OS Lite (64-bit)** | USB Thermal Receipt Printer |
| **Raspberry Pi #2** | NFC Reader & Terminal Display | **Raspberry Pi OS with Desktop (64-bit)** | Touchscreen Display + PN532 NFC Reader |
| **Tablet** | Cashier UI | Any OS (iOS/Android/Windows) | Connects via browser to Pi #1 |

---

## 🍓 Raspberry Pi #1 — Backend Server Setup

### 1. Flash OS
1. Download & open **Raspberry Pi Imager**.
2. Select OS: **Raspberry Pi OS Lite (64-bit)** (no desktop GUI needed).
3. Click gear icon ⚙️ (OS Customization):
   - Set Hostname: `supermarket-server`
   - Enable SSH (with password or public key)
   - Set username & password (e.g. `pi` / your password)
   - Configure Wi-Fi / LAN settings
   - Set Timezone: `Europe/Berlin`
4. Flash SD card & insert into Pi #1.

### 2. Install Docker & Docker Compose
SSH into Pi #1 (`ssh pi@supermarket-server.local` or via IP):

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker via official script
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group (run without sudo)
sudo usermod -aG docker $USER

# Install git
sudo apt install -y git

# Reboot to apply group permissions
sudo reboot
```

### 3. Deploy Application
After rebooting and logging back in:

```bash
# Clone the repository
git clone https://github.com/your-repo/supermarket.git
cd supermarket

# Create environment configuration
cp .env.example .env

# Start container via Docker Compose
docker-compose up -d
```

### 4. Connect USB Printer
1. Connect Epson USB thermal printer via USB cable.
2. Verify system detects printer:
   ```bash
   ls -l /dev/usb/lp*
   ```
3. If `/dev/usb/lp0` is present, update `.env` if needed:
   ```env
   PRINTER_DEVICE=/dev/usb/lp0
   ```
4. If permissions are needed on host:
   ```bash
   sudo usermod -aG lp $USER
   ```

---

## 💳 Raspberry Pi #2 — NFC Reader & Touchscreen Terminal Setup

### 1. Flash OS
1. Open **Raspberry Pi Imager**.
2. Select OS: **Raspberry Pi OS with Desktop (64-bit)** (desktop environment required for touchscreen kiosk mode).
3. Click gear icon ⚙️ (OS Customization):
   - Set Hostname: `supermarket-terminal`
   - Enable SSH
   - Set username & password
   - Configure Wi-Fi / LAN settings
4. Flash SD card & insert into Pi #2.

### 2. PN532 NFC Module Wiring
Set DIP switches on PN532 board to **I2C Mode** (`SEL0 = HIGH (1)`, `SEL1 = LOW (0)`).

Connect PN532 to Raspberry Pi #2 GPIO pins:

| PN532 Pin | Raspberry Pi #2 Pin | Function |
|---|---|---|
| `VCC` | Pin 1 (3.3V) or Pin 2 (5V) | Power |
| `GND` | Pin 6 (GND) | Ground |
| `SDA` | Pin 3 (GPIO 2 - SDA) | I2C Data |
| `SCL` | Pin 5 (GPIO 3 - SCL) | I2C Clock |

*Alternative (SPI Mode)*: Set DIP switches to `SEL0 = LOW (0)`, `SEL1 = HIGH (1)` and connect to SCK (Pin 23), MISO (Pin 21), MOSI (Pin 19), SSEL (Pin 24).

### 3. Enable I2C & SPI Interfaces on Pi #2
SSH into Pi #2 (`ssh pi@supermarket-terminal.local`):

```bash
sudo raspi-config
```
- Go to `Interface Options` → `I2C` → Enable `Yes`.
- Go to `Interface Options` → `SPI` → Enable `Yes`.
- Reboot: `sudo reboot`.

Verify I2C detection:
```bash
sudo apt install -y i2c-tools
sudo i2cdetect -y 1
```
*(You should see `0x24` listed for the PN532 chip)*.

### 4. Setup NFC Reader Python Service
SSH into Pi #2:

```bash
# Install git and python dependencies
sudo apt update && sudo apt install -y git python3-pip python3-venv

# Clone project
git clone https://github.com/your-repo/supermarket.git
cd supermarket/nfc_reader

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Create Systemd Auto-Start Service on Pi #2
Create service file `/etc/systemd/system/supermarkt-nfc.service`:

```ini
[Unit]
Description=Kinder-Supermarkt NFC Reader Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/supermarket/nfc_reader
ExecStart=/home/pi/supermarket/nfc_reader/venv/bin/python reader.py --server http://supermarket-server.local:5000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable & start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now supermarkt-nfc
```

### 5. Setup Touchscreen Chromium Kiosk Mode
To automatically launch the terminal UI on Pi #2's touchscreen display on boot:

1. Install unclutter (hides mouse cursor):
   ```bash
   sudo apt install -y chromium-browser unclutter
   ```

2. Edit autostart configuration (`~/.config/lxsession/LXDE-pi/autostart` or `~/.config/wayfire.ini` for Wayland):

   For X11 (`~/.config/lxsession/LXDE-pi/autostart`):
   ```bash
   @xset s off
   @xset -dpms
   @xset s noblank
   @unclutter -idle 0.1 -root
   @chromium-browser --kiosk --noerrdialogs --disable-infobars --check-for-update-interval=31536000 http://supermarket-server.local:5000/terminal
   ```

3. Reboot Pi #2. The screen will automatically boot straight into the animated terminal view!

---

## 📱 Tablet Setup (Cashier UI)

1. Connect tablet to the same Wi-Fi network as Pi #1 and Pi #2.
2. Open browser (Safari / Chrome / Firefox).
3. Navigate to `http://supermarket-server.local:5000` (or `http://<pi1-ip-address>:5000`).
4. (Optional) Add web page to Home Screen for a native full-screen app experience.

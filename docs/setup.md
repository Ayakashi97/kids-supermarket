# 🛠️ Raspberry Pi Hardware & OS Setup Guide

Complete step-by-step setup guide for both Raspberry Pi units in the **Kinder-Supermarkt** system, including display troubleshooting and hardware configuration.

---

## 📐 Architecture Overview

| Device | Role | Recommended OS | Connected Hardware | Default Access URL |
|---|---|---|---|---|
| **Raspberry Pi #1** | Backend Server (Flask, SQLite, Docker) | **Raspberry Pi OS Lite (64-bit)** | USB Thermal Receipt Printer | `http://<pi1-ip>:5050` |
| **Raspberry Pi #2** | NFC Reader & Touchscreen Terminal | **Raspberry Pi OS Desktop (64-bit)** | Touchscreen Display + PN532 NFC Module | `http://<pi1-ip>:5050/terminal` (Kiosk Mode) |
| **Tablet** | Cashier UI | Any OS (iOS / Android / Windows) | Web Browser | `http://<pi1-ip>:5050` |

---

## 🍓 Raspberry Pi #1 — Backend Server Setup

### 1. Flash OS
1. Download & open **Raspberry Pi Imager**.
2. Select OS: **Raspberry Pi OS Lite (64-bit)** (headless, no desktop GUI needed).
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
git clone https://github.com/Ayakashi97/kids-supermarket.git
cd kids-supermarket

# Create environment configuration
cp .env.example .env

# Start container via Docker Compose
docker compose up -d
```

### 4. Connect USB Printer
1. Connect Epson (or compatible ESC/POS) USB thermal printer via USB cable.
2. Verify system detects printer:
   ```bash
   ls -l /dev/usb/lp*
   ```
3. If `/dev/usb/lp0` is present, update `.env` if needed:
   ```env
   PRINTER_DEVICE=/dev/usb/lp0
   ```

---

## 💳 Raspberry Pi #2 — NFC Reader & Touchscreen Terminal Setup

### 1. Flash OS
1. Open **Raspberry Pi Imager**.
2. Select OS: **Raspberry Pi OS with Desktop (64-bit)** (desktop environment required for touchscreen kiosk display).
3. Click gear icon ⚙️ (OS Customization):
   - Set Hostname: `supermarket-terminal`
   - Enable SSH
   - Set username & password
   - Configure Wi-Fi / LAN settings
4. Flash SD card & insert into Pi #2.

---

### 🖥️ Touchscreen Setup & White Screen Troubleshooting

If your Raspberry Pi touchscreen turns on but stays **solid white** or shows **no display signal**:

#### A. Official Raspberry Pi 7" Touchscreen (DSI Ribbon Cable)
1. **Ribbon Cable Orientation**:
   - Ensure the DSI ribbon cable is connected to the `DISPLAY` port (not the `CAMERA` port!).
   - Black locking latch pulled up, blue tab on ribbon cable facing the USB/Ethernet ports, metal contacts facing PCB board.
2. **Display Drivers in `/boot/firmware/config.txt`**:
   SSH into Pi #2 (`ssh pi@supermarket-terminal.local`) and edit `/boot/firmware/config.txt` (or `/boot/config.txt` on older OS):
   ```bash
   sudo nano /boot/firmware/config.txt
   ```
   Ensure the DRM graphics driver overlay is enabled under `[all]`:
   ```ini
   # Enable DRM VC4 V3D driver
   dtoverlay=vc4-kms-v3d
   
   # For Official Raspberry Pi 7" Touchscreen DSI:
   dtoverlay=vc4-kms-dsi-7inch
   gpu_mem=128
   ```

#### B. Waveshare / Elecrow HDMI Touchscreen Displays
If using a 5-inch or 7-inch HDMI touchscreen connected via HDMI adapter:
1. Open `/boot/firmware/config.txt`:
   ```ini
   hdmi_force_hotplug=1
   config_hdmi_boost=10
   hdmi_group=2
   hdmi_mode=87
   hdmi_cvt 1024 600 60 6 0 0 0
   hdmi_drive=1
   ```
2. Reboot: `sudo reboot`.

#### C. 3.5-inch SPI GPIO Touchscreen Displays (XPT2046 Touch Controller / ILI9486)
If using a 3.5" display plugged directly into the 40-pin GPIO header (SPI bus instead of HDMI/DSI):

**1-Click Installation Driver**:
SSH into Pi #2 (`ssh pi@supermarket-terminal.local`) and run:

```bash
# Clone official LCD-show driver repository
git clone https://github.com/goodtft/LCD-show.git
chmod -R 755 LCD-show
cd LCD-show/

# Run setup script for 3.5" XPT2046 SPI display (auto-configures SPI, overlays & reboots)
sudo ./LCD35-show
```

---

### 2. PN532 NFC Module Wiring
Set DIP switches on PN532 board to **I2C Mode** (`SEL0 = HIGH (1)`, `SEL1 = LOW (0)`).

Connect PN532 to Raspberry Pi #2 GPIO pins:

| PN532 Pin | Raspberry Pi #2 Pin | Function |
|---|---|---|
| `VCC` | Pin 1 (3.3V) or Pin 2 (5V) | Power |
| `GND` | Pin 6 (GND) | Ground |
| `SDA` | Pin 3 (GPIO 2 - SDA) | I2C Data |
| `SCL` | Pin 5 (GPIO 3 - SCL) | I2C Clock |

### 3. Enable I2C & SPI Interfaces on Pi #2
SSH into Pi #2:

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

---

### 4. Setup NFC Reader Python Service
SSH into Pi #2:

```bash
# Install git and python dependencies
sudo apt update && sudo apt install -y git python3-pip python3-venv

# Clone project
git clone https://github.com/Ayakashi97/kids-supermarket.git
cd kids-supermarket/nfc_reader

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
WorkingDirectory=/home/pi/kids-supermarket/nfc_reader
ExecStart=/home/pi/kids-supermarket/nfc_reader/venv/bin/python reader.py --server http://supermarket-server.local:5050
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

---

### 5. Setup Touchscreen Chromium Kiosk Mode (Auto-Launch Terminal on Boot)

Now that the desktop is working, configure Chromium to launch full-screen in Kiosk mode on boot:

#### Method A: Raspberry Pi OS Bookworm (Labwc / Wayland - Default on Pi 4 / Pi 5)
Create autostart config file:
```bash
mkdir -p ~/.config/labwc
nano ~/.config/labwc/autostart
```

Paste the following line (replace IP with your Pi #1 IP if needed):
```bash
chromium-browser --kiosk --noerrdialogs --disable-infobars --check-for-update-interval=31536000 http://supermarket-server.local:5050/terminal &
```

#### Method B: Raspberry Pi OS Bullseye / X11 (Default on Pi 3 / Zero)
Create/edit LXDE autostart file:
```bash
mkdir -p ~/.config/lxsession/LXDE-pi
nano ~/.config/lxsession/LXDE-pi/autostart
```

Paste:
```bash
@xset s 30
@xset dpms 30 30 30
@unclutter -idle 0.1 -root
@chromium-browser --kiosk --noerrdialogs --disable-infobars --check-for-update-interval=31536000 http://supermarket-server.local:5050/terminal
```

#### Test Immediately from Command Line:
```bash
chromium-browser --kiosk http://supermarket-server.local:5050/terminal
```

Reboot Pi #2 (`sudo reboot`). It will now boot straight into the full-screen animated **Kinder-Supermarkt Terminal** view!

---

## 📱 Tablet Setup (Cashier UI)

1. Connect tablet to the same Wi-Fi network as Pi #1 and Pi #2.
2. Open browser (Safari / Chrome / Firefox).
3. Navigate to `http://supermarket-server.local:5050` (or `http://<pi1-ip-address>:5050`).
4. (Optional) Add web page to Home Screen for a native full-screen app experience.

---

## 🔐 Admin Panel Access

1. Open `http://supermarket-server.local:5050/admin` in any browser.
2. Use the touchscreen **PIN-Pad** to enter the admin PIN (default: `1234`).
3. Manage products, register/edit NFC cards with photos & PINs, configure thermal & PDF receipt layouts, set terminal PIN modes, and adjust display standby timeout (`screen_timeout`).

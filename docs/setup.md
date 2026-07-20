# 🛠️ Raspberry Pi Hardware & OS Setup Guide

Complete step-by-step setup guide for both Raspberry Pi units in the **Kinder-Supermarkt** system, including display drivers, enclosure constraints, and NFC reader hardware options.

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

## 💳 Raspberry Pi #2 — Touchscreen Terminal & NFC Reader Setup

To prevent first-time setup popups on the small 3.5" LCD screen, follow this **exact 4-step sequence**:

---

### Step 1: Flash OS & Complete First-Time Setup on HDMI Monitor
1. Flash **Raspberry Pi OS Desktop (64-bit)** using Raspberry Pi Imager.
2. Connect Pi #2 to a standard **HDMI Monitor**, keyboard, and mouse.
3. Power on Pi #2 and complete the on-screen **Raspberry Pi First-Time Setup Wizard** (Language, Wi-Fi, Timezone, User/Password -> Click Finish).
4. Alternatively, disable the setup wizard immediately via terminal:
   ```bash
   sudo systemctl disable --now rpi-initial-setup
   ```

---

### Step 2: Configure Chromium Kiosk Autostart (Auto-Boot into Supermarket Terminal)

Create an autostart script that waits for network connection before launching Chromium in kiosk mode:

1. **Create Kiosk Script**:
   ```bash
   nano /home/pi/start_kiosk.sh
   ```
   Paste the following:
   ```bash
   #!/bin/bash
   # Wait 8 seconds for Wi-Fi and display initialization
   sleep 8

   # Launch Chromium in full-screen kiosk mode
   export DISPLAY=:0
   chromium-browser --kiosk --noerrdialogs --disable-infobars --check-for-update-interval=31536000 http://10.9.3.172:5050/terminal &
   ```
   Save (`Ctrl + O`, `Enter`) and exit (`Ctrl + X`).

2. **Make Executable & Add to Crontab**:
   ```bash
   chmod +x /home/pi/start_kiosk.sh
   (crontab -l 2>/dev/null; echo "@reboot /home/pi/start_kiosk.sh") | crontab -
   ```

3. **Add Universal XDG Autostart File**:
   ```bash
   mkdir -p ~/.config/autostart
   nano ~/.config/autostart/kiosk.desktop
   ```
   Paste:
   ```ini
   [Desktop Entry]
   Type=Application
   Name=Supermarkt Kiosk
   Exec=/home/pi/start_kiosk.sh
   X-GNOME-Autostart-enabled=true
   ```

---

### Step 3: Hardware Connection (3.5" Touchscreen + PN532 NFC Reader)

![Connecting AZDelivery USB-C to TTL Serial Adapter to Raspberry Pi 4 and PN532 NFC Module](images/azdelivery_usb_connection.jpg)

When using an enclosure/case where a 3.5" Touchscreen Display plugs flush onto all 40 GPIO pins, connect the PN532 module via USB:

1. **PN532 DIP Switches**: Set to **HSU/UART Mode**: `SEL0 = 0 (LOW / OFF)`, `SEL1 = 0 (LOW / OFF)`.
2. **Connect to USB-to-TTL Adapter (AZDelivery / CP2102 / FT232)**:
   - `VCC` ➡️ `5V` (Set jumper on AZDelivery adapter to **5V**)
   - `GND` ➡️ `GND`
   - `TX`  ➡️ `RX`
   - `RX`  ➡️ `TX`
3. Plug the USB-C adapter cable into any USB port on Pi #2!

---

### Step 4: Install 3.5" Touchscreen Driver (`LCD35-show`) & Switch Display Output

Now attach the 3.5" SPI Touchscreen Display to the 40-pin GPIO header and switch graphics output from HDMI to the 3.5" LCD screen:

```bash
# Clone official LCD-show driver repository
git clone https://github.com/goodtft/LCD-show.git
chmod -R 755 LCD-show
cd LCD-show/

# Run installer script for 3.5" XPT2046 SPI display
sudo ./LCD35-show
```

> ⚙️ **What happens next**:
> - The installer configures the SPI display overlays.
> - The Raspberry Pi reboots automatically.
> - Graphics output switches from HDMI to the **3.5" Touchscreen LCD**.
> - Pi #2 boots straight into the full-screen animated **Kinder-Supermarkt Terminal** (`http://10.9.3.172:5050/terminal`)!

---

## 🛠️ Handy Display Output Commands

To switch display output between HDMI and the 3.5" Touchscreen display at any time:

- **Switch back to HDMI Monitor**:
  ```bash
  cd LCD-show/ && sudo ./LCD-hdmi
  ```
- **Switch back to 3.5" Touchscreen LCD**:
  ```bash
  cd LCD-show/ && sudo ./LCD35-show
  ```

---

## 💳 Optional: Setup Hardware NFC Reader Python Service

If using hardware NFC cards (PN532 via USB `/dev/ttyUSB0` or I2C):

```bash
# Enable I2C & SPI
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0

# Clone repo and setup python service
git clone https://github.com/Ayakashi97/kids-supermarket.git
cd kids-supermarket/nfc_reader

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create systemd auto-start service
sudo cp supermarkt-nfc.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now supermarkt-nfc
```

*(Note: If no physical NFC reader is connected, set **NFC-Lesegerät Modus** to **"Touchscreen-Kartenwahl"** in Admin Settings at `/admin/settings` so children can tap their card photos directly on the touchscreen!).*

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

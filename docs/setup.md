# 🛠️ Raspberry Pi & Smartphone Setup Guide

Complete step-by-step setup guide for the **Kinder-Supermarkt** system, including server deployment, smartphone Web NFC & PWA full-screen setup, and legacy Raspberry Pi hardware options.

---

## 📐 Architecture Overview

| Device | Role | OS / Browser | Connected Hardware | PWA App Name | Default Access URL |
|---|---|---|---|---|---|
| **Raspberry Pi #1** | Backend Server (Flask, SQLite, Docker) | **Raspberry Pi OS Lite (64-bit)** | USB Thermal Receipt Printer | — | `http://<pi1-ip>:5050` |
| **Smartphone (Empfohlen)** | NFC Reader & Terminal Display | **Android (Chrome Web NFC)** or **iOS (Safari PWA)** | Built-in NFC chip | **Supermarkt Terminal** 💳 | `http://<pi1-ip>:5050/terminal` |
| **Tablet** | Cashier UI | Any OS (iOS / Android / Windows) | Web Browser | **Supermarkt Kasse** 🛒 | `http://<pi1-ip>:5050` |
| **Raspberry Pi #2 (Legacy)** | Hardware NFC Reader & LCD | **Raspberry Pi OS Desktop** | Touchscreen LCD + PN532 USB | — | `http://<pi1-ip>:5050/terminal` |

---

## 📱 Smartphone Setup (NFC Reader & Terminal PWA)

Using an old smartphone (Android or iPhone) is the easiest and cleanest way to run the payment terminal without extra hardware!

### 1. Android Smartphone (Web NFC Scanning)
1. Ensure Wi-Fi is connected to the same network as Raspberry Pi #1.
2. Open **Google Chrome** on the Android phone.
3. Open `http://<pi1-ip>:5050/terminal`.
4. Tap the green button **`📱 NFC-Leser auf Handy aktivieren`** once and tap **"Erlauben"** when Android Chrome prompts for NFC permission.
   - *Hinweis*: Die App merkt sich diese Aktivierung im `localStorage`. Der Button verschwindet danach dauerhaft!
5. Tap the Chrome browser menu `⋮` ➡️ **"Zum Startbildschirm hinzufügen"** (Add to Home screen) or **"App installieren"**.
6. Launch **Supermarkt Terminal** from the Home Screen — it opens in **100% full screen** without browser bars!
7. **Web NFC**: Hold any NFC card or sticker against the back of the phone. Android Chrome captures the UID/text directly and triggers the payment!

### 2. iPhone (iOS Safari PWA & Touchscreen Terminal)
1. Connect iPhone to the local Wi-Fi.
2. Open **Safari** on the iPhone and navigate to `http://<pi1-ip>:5050/terminal`.
3. Tap the Share button 📤 ➡️ **"Zum Home-Bildschirm"** (Add to Home Screen).
4. Launch **Supermarkt Terminal** from the iPhone Home Screen — it opens in borderless **fullscreen app mode**.
5. *Note on iOS*: Apple blocks Web NFC in Safari, so on iOS the terminal displays in **Touchscreen Mode** where children can tap their card avatar on screen to pay or enter their PIN.

---

## 📱 Tablet Setup (Cashier PWA)

1. Open **Chrome** or **Safari** on the Tablet.
2. Navigate to `http://<pi1-ip>:5050`.
3. Tap `⋮` / Share 📤 ➡️ **"Zum Startbildschirm hinzufügen"**.
4. Launch **Supermarkt Kasse** 🛒 — opens as an independent, fullscreen cashier app with custom shop name and product grid.

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

### 4. Connect USB Printer (Optional)
1. Connect Epson (or compatible ESC/POS) USB thermal printer via USB cable.
2. Verify system detects printer:
   ```bash
   ls -l /dev/usb/lp*
   ```
3. Update `.env` if needed:
   ```env
   PRINTER_DEVICE=/dev/usb/lp0
   ```

---

## 🔐 Admin Panel & Shop Name Customization

1. Open `http://supermarket-server.local:5050/admin` in any browser.
2. Use the touchscreen **PIN-Pad** to enter the admin PIN (default: `1234`).
3. Under **Einstellungen** (`/admin/settings`):
   - **Name des Supermarkts**: Enter your custom shop name (e.g. *Emmis Kaufladen*). This name updates live across Cashier, Terminal, Receipts, Admin, and page titles!
   - **NFC-Lesegerät Modus**: Set to `web_nfc` (Smartphone Web NFC) or `touchscreen_simulation`.

# 🛠️ Raspberry Pi & Smartphone Setup Guide

Complete step-by-step setup guide for the **Kinder-Supermarkt** system, including server deployment, smartphone Web NFC & PWA full-screen setup, and legacy Raspberry Pi hardware options.

---

## 📐 Architecture Overview

| Device | Role | OS / Browser | Connected Hardware | PWA App Name | Default Access URL |
|---|---|---|---|---|---|
| **Raspberry Pi #1** | Backend Server (Flask, SQLite, Docker) | **Raspberry Pi OS Lite (64-bit)** | USB Thermal Receipt Printer | — | `http://<pi1-ip>` |
| **Smartphone (Empfohlen)** | NFC Reader & Terminal Display | **Android (Chrome Web NFC)** or **iOS (Safari PWA)** | Built-in NFC chip | **Supermarkt Terminal** 💳 | `http://<pi1-ip>/terminal` |
| **Tablet** | Cashier UI | Any OS (iOS / Android / Windows) | Web Browser | **Supermarkt Kasse** 🛒 | `http://<pi1-ip>` |
| **Raspberry Pi #2 (Legacy)** | Hardware NFC Reader & LCD | **Raspberry Pi OS Desktop** | Touchscreen LCD + PN532 USB | — | `http://<pi1-ip>/terminal` |

---

## 📱 Smartphone Setup (NFC Reader & Terminal PWA)

Using an old smartphone (Android or iPhone) is the easiest and cleanest way to run the payment terminal without extra hardware!

### 1. Android Smartphone (Web NFC Scanning)
> ⚠️ **WICHTIG (HTTPS-Pflicht):** Android Chrome erlaubt den Zugriff auf den NFC-Chip *ausschließlich* über eine sichere HTTPS-Verbindung. Richte vor dem Einrichten des Smartphones unbedingt HTTPS ein. Siehe [HTTPS Setup-Anleitung](HTTPS_SETUP.md) für alle Details.

1. Ensure Wi-Fi is connected to the same network as Raspberry Pi #1.
2. Open **Google Chrome** on the Android phone.
3. Open **`https://supermarket.local/terminal`** (bzw. deine HTTPS-URL).
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
3. Update the setting in the **Admin Settings UI** (`/admin/settings`) under **USB Drucker-Gerätepfad** (standardmäßig `/dev/usb/lp0`).
   - *Wichtig*: Du musst außerdem deine `docker-compose.yml` bearbeiten, um das USB-Gerät an den Container durchzureichen, wie im Admin-Panel unter Einstellungen beschrieben.

---

---

## 🔍 Hand-Scanner Modus & Produkt-NFC-Tags (Optional)

Das Terminal-Smartphone kann im Leerlauf als physischer **Hand-Scanner** genutzt werden, um Waren einzuscannen:

1. **Hand-Scanner aktivieren**:
   - Gehe im Admin-Panel auf **Einstellungen** (`/admin/settings`).
   - Stelle **Terminal Hand-Scanner Modus** auf `✅ Aktiviert`.
2. **NFC-Tags den Produkten zuweisen**:
   - Gehe zu **Produkte verwalten** (`/admin/products`).
   - Klicke beim gewünschten Produkt auf **Bearbeiten** (oder `Scan 🏷️` im Modal).
   - Klicke auf **`Scan 🏷️`** und halte einen beliebigen NFC-Sticker/Tag an das Terminal-Handy.
   - Die UID wird automatisch im Formularfeld eingetragen. Speichern klicken — fertig!
3. **Produkte im Spiel scannen**:
   - Im Leerlauf zeigt das Smartphone den gelben Status **"Scanner bereit!"**.
   - Halte ein Produkt mit NFC-Tag an das Handy — das Smartphone spielt den typischen Kassen-Scanner-Ton (1900 Hz), vibriert kurz und fügt den Artikel automatisch dem Einkaufskorb auf dem Kassen-Tablet hinzu!
   - Sobald auf der Kasse `Bezahlen` angetippt wird, schaltet das Terminal automatisch in den **Bezahl-Modus** um.

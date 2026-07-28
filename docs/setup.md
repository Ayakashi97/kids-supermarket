# 🛠️ Setup Guide — Kinder-Supermarkt

Schritt-für-Schritt-Anleitung für die vollständige Einrichtung des Systems auf einem **Raspberry Pi**, **Tablet** und **Smartphone**.

---

## Inhaltsverzeichnis

1. [Übersicht & Hardware](#übersicht--hardware)
2. [Raspberry Pi einrichten](#1-raspberry-pi-einrichten)
3. [App deployen](#2-app-deployen)
4. [Erstkonfiguration (Admin-Panel)](#3-erstkonfiguration-admin-panel)
5. [Tablet einrichten (Kasse)](#4-tablet-einrichten-kasse)
6. [Smartphone einrichten (Terminal)](#5-smartphone-einrichten-terminal)
7. [USB-Thermodrucker anschließen](#6-usb-thermodrucker-anschließen-optional)
8. [Hand-Scanner-Modus](#7-hand-scanner-modus-optional)
9. [HTTPS einrichten](#8-https-einrichten-für-web-nfc)
10. [Umgebungsvariablen](#9-umgebungsvariablen)

---

## Übersicht & Hardware

| Gerät | Rolle | Zugriff |
|---|---|---|
| **Raspberry Pi** | Server (Flask + Docker) | — |
| **Tablet** | Kassen-UI | `http://<pi-ip>` |
| **Smartphone** | NFC-Terminal | `http://<pi-ip>/terminal` |
| **USB-Drucker** | Thermobon-Druck | per USB am Pi |

Alle Geräte müssen im **selben WLAN** sein.

---

## 1. Raspberry Pi einrichten

### 1.1 OS flashen

1. **Raspberry Pi Imager** herunterladen und öffnen
2. OS wählen: **Raspberry Pi OS Lite (64-bit)** — kein Desktop nötig
3. Zahnrad-Icon ⚙️ klicken (OS-Anpassung):
   - Hostname: `supermarket-server`
   - SSH aktivieren (Passwort oder Public Key)
   - WLAN und Zugangsdaten eintragen
   - Timezone: `Europe/Berlin`
4. SD-Karte flashen und in den Pi einlegen

### 1.2 Dateisystem erweitern

Nach dem ersten Start den kompletten SD-Karten-Speicher freischalten:

```bash
sudo raspi-config nonint do_expand_rootfs && sudo reboot
```

Nach dem Neustart prüfen:
```bash
df -h /
```
Unter `Size` sollte die volle SD-Karten-Größe erscheinen.

### 1.3 Docker installieren

Per SSH am Pi anmelden (`ssh pi@supermarket-server.local`) und ausführen:

```bash
sudo apt update && sudo apt upgrade -y
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
sudo apt install -y git
sudo reboot
```

---

## 2. App deployen

Nach dem Neustart wieder per SSH anmelden:

```bash
git clone https://github.com/Ayakashi97/kids-supermarket.git
cd kids-supermarket

# .env erstellen und anpassen (optional — Standardwerte funktionieren sofort)
cp .env.example .env

# Starten
docker compose up -d
```

Das System ist jetzt erreichbar:

| URL | Was |
|---|---|
| `http://<pi-ip>` | Kassen-Tablet |
| `http://<pi-ip>/terminal` | Smartphone-Terminal |
| `http://<pi-ip>/admin` | Admin-Panel (Standard-PIN: `1234`) |
| `http://<pi-ip>/receipt/preview` | Muster-Bon (PDF-Test) |

> Den Pi-IP-Auflösen: `hostname -I` im Pi-Terminal oder im Router nachschauen.  
> Alternativ funktioniert `http://supermarket-server.local` wenn mDNS aktiv ist.

---

## 3. Erstkonfiguration (Admin-Panel)

1. `http://<pi-ip>/admin` im Browser öffnen — PIN `1234` eingeben
2. **Admin-PIN ändern**: Einstellungen → Admin-PIN
3. **Shop-Namen setzen**: Einstellungen → Shop-Name (z. B. *Emmis Kaufladen*)
4. **Server-URL setzen**: Einstellungen → Basis-URL (z. B. `http://192.168.1.50`) — wichtig für QR-Codes auf Bons
5. **Kundenkarten registrieren**: Karten → `+` → Name eingeben → Smartphone mit NFC-Tag tippen → Speichern
6. **Dev-Modus deaktivieren**: Einstellungen → Entwickler-Modus → Deaktiviert *(für den echten Spielbetrieb)*

---

## 4. Tablet einrichten (Kasse)

1. Tablet mit dem WLAN verbinden
2. Browser (Chrome oder Safari) öffnen → `http://<pi-ip>` aufrufen
3. **Als PWA installieren**:
   - Chrome: Menü `⋮` → *Zum Startbildschirm hinzufügen* oder *App installieren*
   - Safari: Teilen-Button 📤 → *Zum Home-Bildschirm*
4. **Supermarkt Kasse 🛒** vom Startbildschirm öffnen — startet direkt im Vollbild im Querformat

> Falls der Browser eine Quer-/Hochformat-Warnung zeigt: Tablet ins Querformat drehen.

---

## 5. Smartphone einrichten (Terminal)

### Android (mit NFC — empfohlen)

> ⚠️ Android Chrome benötigt **HTTPS** für Web NFC. Zuerst [HTTPS einrichten](#8-https-einrichten-für-web-nfc).

1. Smartphone mit WLAN verbinden
2. **Google Chrome** öffnen → `https://<pi-ip>/terminal` aufrufen
3. Grünen Button **`📱 NFC-Leser aktivieren`** tippen → *Erlauben* antippen
   - *Die App merkt sich diese Aktivierung dauerhaft — der Button verschwindet danach.*
4. Chrome-Menü `⋮` → *Zum Startbildschirm hinzufügen*
5. **Supermarkt Terminal 💳** vom Startbildschirm öffnen — Vollbild, kein Browser-Chrome

Karten bezahlen: NFC-Sticker/Karte von hinten an das Smartphone halten.

### iPhone (ohne NFC — Touchscreen-Modus)

1. iPhone mit WLAN verbinden
2. **Safari** öffnen → `http://<pi-ip>/terminal` aufrufen *(HTTP reicht für iOS)*
3. Teilen-Button 📤 → *Zum Home-Bildschirm*
4. **Supermarkt Terminal 💳** öffnen — Kinder tippen auf ihr Karten-Avatar-Bild

---

## 6. USB-Thermodrucker anschließen (optional)

1. Epson-Thermodrucker per USB am Raspberry Pi anschließen
2. Gerät prüfen:
   ```bash
   ls -l /dev/usb/lp*
   ```
   Gibt normalerweise `/dev/usb/lp0` aus.

3. `docker-compose.yml` bearbeiten — den auskommentierten `devices:`-Block aktivieren:
   ```yaml
   services:
     web:
       devices:
         - "/dev/usb/lp0:/dev/usb/lp0"
   ```

4. Container neu starten:
   ```bash
   docker compose down && docker compose up -d
   ```

5. Im Admin-Panel prüfen: **Einstellungen → USB Drucker-Gerätepfad** → `/dev/usb/lp0`

---

## 7. Hand-Scanner-Modus (optional)

Das Terminal-Smartphone kann im Leerlauf als NFC-Scanner für Waren eingesetzt werden — wie ein echter Supermarkt-Scanner.

1. **Aktivieren**: Admin → Einstellungen → *Terminal Hand-Scanner Modus* → `✅ Aktiviert`
2. **NFC-Tags Produkten zuweisen**: Admin → Produkte → Produkt bearbeiten → Feld *NFC-Tag* → `Scan 🏷️` klicken → Tag an Smartphone halten → Speichern
3. **Im Spiel**: Im Leerlauf zeigt das Terminal **„Scanner bereit!"**. NFC-Tag an das Handy halten → Kassen-Scanner-Ton + Vibration → Produkt erscheint im Warenkorb auf dem Tablet

> Sobald auf dem Tablet `Bezahlen` getippt wird, wechselt das Terminal automatisch in den Zahlungsmodus.

---

## 8. HTTPS einrichten (für Web NFC)

Android Chrome erlaubt Web NFC **nur über HTTPS**. Für den iOS-Touchscreen-Modus ist HTTPS optional.

### Option A: Direkt im Admin-Panel (empfohlen)

1. Admin → Einstellungen → Abschnitt **🔐 Web-Protokoll & SSL**
2. `.pem` Zertifikat und privaten Schlüssel hochladen
3. Optional: CA-Kette hochladen
4. Basis-URL auf `https://` aktualisieren → Speichern

Das System startet automatisch einen HTTPS-Server auf Port 443 und leitet HTTP → HTTPS weiter.

### Option B: Externe Anleitung

Für selbstsignierte Zertifikate mit eigenem Root-CA (empfohlen für lokale Netzwerke):
→ **[docs/HTTPS_SETUP.md](./HTTPS_SETUP.md)**

---

## 9. Umgebungsvariablen

Alle Werte in der `.env`-Datei (aus `.env.example` kopieren):

| Variable | Standard | Beschreibung |
|---|---|---|
| `HTTP_PORT` | `80` | HTTP-Port des Servers |
| `HTTPS_PORT` | `443` | HTTPS-Port (nur wenn Zertifikat vorhanden) |
| `FLASK_SECRET_KEY` | *(zufällig)* | Session-Schlüssel — **für Produktion ändern!** |
| `ADMIN_PIN` | `1234` | Standard-Admin-PIN (überschreibbar im Admin-Panel) |
| `SHOP_NAME` | `Kinder-Supermarkt` | Shop-Name (überschreibbar im Admin-Panel) |
| `PRINTER_DEVICE` | `/dev/usb/lp0` | USB-Pfad des Thermodruckers |
| `DEV_MODE` | `true` | Dev-Simulator anzeigen — **auf `false` setzen!** |
| `DATABASE_URL` | `sqlite:///data/supermarket.db` | Datenbank-Pfad (nicht ändern) |

> Alle Einstellungen können nach dem Start auch direkt im **Admin-Panel → Einstellungen** geändert werden — ohne Neustart.

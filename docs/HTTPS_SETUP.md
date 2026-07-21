# 🔐 HTTPS & Eigene CA einrichten (Local SSL Setup)

Dieses Handbuch beschreibt, wie du eine eigene Zertifizierungsstelle (CA) erstellst, lokale Zertifikate für `supermarket.local` signierst, diese auf deinen Endgeräten (Tablet & Smartphone) installierst und in der Kassen-App einrichtest.

---

## 🎯 Warum ist HTTPS notwendig?

1. **Android Web NFC**: Google Chrome auf Android erlaubt den Zugriff auf die Web NFC API (`window.NDEFReader`) **ausschließlich** über verschlüsselte HTTPS-Verbindungen (oder auf `localhost`). Ohne HTTPS bleibt der NFC-Leser deaktiviert.
2. **Datenschutz**: Die Übertragung der Admin-PIN und Signaturen wird verschlüsselt, um Mitlesen im Heimnetzwerk zu verhindern.
3. **PWA-Installation**: Moderne Browser erlauben das Hinzufügen zum Startbildschirm (PWA) oft nur über sichere Verbindungen.

---

## 🛠️ Schritt 1: Eigene Root-CA erstellen

Erstelle die Zertifizierungsstelle (CA) auf deinem Entwickler-Rechner (Mac, Linux oder Windows mit Git Bash/WSL). Ersetze `192.168.x.x` durch die tatsächliche IP-Adresse deines Raspberry Pi.

```bash
# 1. Privaten Schlüssel für die Root-CA erzeugen (4096 Bit)
openssl genrsa -out supermarket-ca.key 4096

# 2. Root-CA Zertifikat erstellen (10 Jahre Gültigkeit)
openssl req -x509 -new -nodes \
  -key supermarket-ca.key \
  -sha256 -days 3650 \
  -out supermarket-ca.crt \
  -subj "/CN=Kinder-Supermarkt Local CA"

# 3. Privaten Schlüssel für den Supermarkt-Server erzeugen
openssl genrsa -out supermarket.key 2048

# 4. Certificate Signing Request (CSR) erzeugen
openssl req -new \
  -key supermarket.key \
  -out supermarket.csr \
  -subj "/CN=supermarket.local"

# 5. SAN (Subject Alternative Names) Konfiguration erstellen
# ERSETZE 192.168.x.x durch die echte IP-Adresse deines Raspberry Pi!
cat > san.ext <<EOF
[SAN]
subjectAltName=DNS:supermarket.local,IP:192.168.x.x
EOF

# 6. Server-Zertifikat mit der CA signieren (1 Jahr Gültigkeit)
openssl x509 -req \
  -in supermarket.csr \
  -CA supermarket-ca.crt \
  -CAkey supermarket-ca.key \
  -CAcreateserial \
  -out supermarket.crt \
  -days 365 \
  -sha256 \
  -extfile san.ext \
  -extensions SAN
```

### Generierte Dateien:
- `supermarket-ca.crt`: Das Stammzertifikat (CA). Dieses musst du **auf den Endgeräten installieren**.
- `supermarket.crt`: Das Server-Zertifikat. Dieses lädst du **im Admin-Panel hoch**.
- `supermarket.key`: Der private Server-Schlüssel. Diesen lädst du **im Admin-Panel hoch**.

---

## 📱 Schritt 2: CA-Zertifikat auf den Endgeräten installieren

Damit Tablet und Smartphone der Domain `supermarket.local` vertrauen, musst du das Stammzertifikat (`supermarket-ca.crt`) auf allen Geräten importieren.

### 🤖 Android (für das Terminal-Handy)
1. Übertrage `supermarket-ca.crt` auf das Handy (z. B. per E-Mail, USB oder Google Drive).
2. Gehe zu **Einstellungen** ➡️ **Sicherheit** ➡️ **Zertifikate** ➡️ **CA-Zertifikat installieren** (kann je nach Android-Version unter *Verschlüsselung & Anmeldedaten* liegen).
3. Bestätige die Warnung und wähle die Datei `supermarket-ca.crt` aus.
4. Starte Google Chrome neu.

### 🍏 iOS / iPadOS (für das Kassen-Tablet)
1. Sende `supermarket-ca.crt` per AirDrop an das iPad/iPhone oder öffne es über iCloud Drive.
2. Es erscheint die Meldung *"Profil geladen"*.
3. Gehe in die **Einstellungen** ➡️ **Profil geladen** (ganz oben) und tippe auf **Installieren**.
4. **WICHTIGER ZUSATZSCHRITT**: Gehe zu **Einstellungen** ➡️ **Allgemein** ➡️ **Info** ➡️ **Zertifikatsvertrauenseinstellungen** (ganz unten).
5. Aktiviere unter *"Volles Vertrauen für Root-Zertifikate aktivieren"* den Schalter für **Kinder-Supermarkt Local CA**.

### 💻 macOS (optional)
```bash
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain supermarket-ca.crt
```

### 🪟 Windows (optional)
1. Doppelklick auf `supermarket-ca.crt`.
2. Klicke auf **Zertifikat installieren...** ➡️ **Lokaler Computer**.
3. Wähle **Zertifikat in folgendem Speicher speichern** ➡️ **Vertrauenswürdige Stammzertifizierungsstellen** aus.

---

## 🌐 Schritt 3: DNS-Auflösung für `supermarket.local` einrichten

Das Endgerät muss wissen, dass die Domain `supermarket.local` auf die IP-Adresse deines Raspberry Pi verweist.

### Option A: Fritz!Box (Empfohlen)
1. Öffne die Fritz!Box-Oberfläche (`http://fritz.box`).
2. Gehe zu **Heimnetz** ➡️ **Netzwerk** ➡️ **Netzwerkverbindungen**.
3. Suche den Raspberry Pi in der Liste, klicke auf **Bearbeiten** (Stift-Symbol).
4. Aktiviere **Diesem Netzwerkgerät immer die gleiche IPv4-Adresse zuweisen**.
5. Trage als Hostname `supermarket` ein (oder richte in den DNS-Rebind-Schutzeinstellungen unter *Netzwerk* ➡️ *Netzwerkeinstellungen* die Ausnahme `supermarket.local` ein, falls die Fritz!Box die Auflösung blockiert).

### Option B: Pi-hole oder AdGuard Home
1. Gehe zu **Local DNS** ➡️ **DNS Records**.
2. Erstelle einen Eintrag:
   - **Domain**: `supermarket.local`
   - **IP Address**: Die IP deines Raspberry Pi.

### Option C: Fallback über die `hosts`-Datei (Nur für PCs/Macs)
Trage auf deinem Computer in der Datei `/etc/hosts` (macOS/Linux) bzw. `C:\Windows\System32\drivers\etc\hosts` (Windows) Folgendes ein:
```
192.168.x.x  supermarket.local
```

---

## 🔐 Schritt 4: Zertifikate im Admin-Panel hochladen

1. Öffne das Admin-Panel im Browser unter `http://<pi-ip>:5050/admin`.
2. Gehe auf **Einstellungen** (Zertifikate & HTTPS).
3. Lade die Dateien hoch:
   - **Zertifikat**: `supermarket.crt`
   - **Privater Schlüssel**: `supermarket.key`
   - **CA-Kette (optional)**: `supermarket-ca.crt`
4. Setze **HTTPS (SSL) aktivieren** auf **Ja**.
5. Klicke am Ende der Seite auf **Speichern** (Grünes Häkchen).
6. Es erscheint ein Hinweis, dass der Server neu gestartet werden muss.

---

## 🌐 Schritt 5: Docker-Container neu starten

Logge dich per SSH auf dem Raspberry Pi ein und starte den Container neu, damit der SSL-Port aktiv wird:

```bash
cd kids-supermarket
docker compose down
docker compose up -d
```

Rufe danach die Seite unter **`https://supermarket.local:5050`** auf.

---

## 🚒 Troubleshooting & Fehlerbehebung

| Fehlerbild | Mögliche Ursache | Lösung |
|---|---|---|
| **„Nicht sicher“ / Rotes Schloss im Browser** | Das CA-Zertifikat wurde nicht installiert oder auf iOS nicht als vertrauenswürdig aktiviert. | Wiederhole **Schritt 2** sorgfältig. Stelle auf iOS sicher, dass der Haken in den *Zertifikatsvertrauenseinstellungen* gesetzt ist. |
| **Seite lädt gar nicht (Timeout)** | Die IP-Adresse in `san.ext` is falsch oder die DNS-Auflösung von `supermarket.local` funktioniert nicht. | Prüfe, ob du die IP des Pi im Browser aufrufen kannst. Falls ja, richte die DNS-Auflösung gemäß **Schritt 3** ein oder nutze das HTTPS-Zertifikat mit der IP-Adresse als Common Name. |
| **NFC-Leser auf Android lässt sich nicht aktivieren** | Die Seite wird nicht über ein sicheres Protokoll (HTTPS) geladen. | Überprüfe die Adresszeile im Browser. Es muss zwingend `https://...` dort stehen. |
| **Zertifikat nach 1 Jahr abgelaufen** | Das Server-Zertifikat hat seine Gültigkeit verloren. | Wiederhole die Schritte 3 bis 6 aus **Schritt 1**, lade die neue `supermarket.crt` im Admin-Panel hoch und starte den Container neu. Die Root-CA bleibt 10 Jahre gültig und muss nicht neu installiert werden. |

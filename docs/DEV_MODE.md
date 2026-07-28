# 🧪 Dev-Modus — Kinder-Supermarkt

Der Dev-Modus ermöglicht das vollständige Testen des Systems auf einem normalen Computer — **ohne Raspberry Pi, Smartphone oder NFC-Hardware**.

---

## Aktivieren & Deaktivieren

**Per `.env`-Datei** (vor dem Start):
```bash
DEV_MODE=true   # aktiviert
DEV_MODE=false  # deaktiviert (Produktion)
```

**Zur Laufzeit** (ohne Neustart):
→ Admin-Panel → Einstellungen → *Entwickler-Modus* → Toggle

---

## Der Dev-Simulator

Wenn `DEV_MODE` aktiv ist, erscheint auf der Kassen-Seite ein **🧪-Button** (unten rechts). Ein Klick öffnet ein Glassmorphic Drawer-Panel mit folgenden Funktionen:

### 💳 Schnell-Testkarten

| Button | Was passiert |
|---|---|
| 👧 Lena | Simuliert Tap der Karte `TEST_LENA_123` |
| 👨 Papa | Simuliert Tap der Karte `TEST_PAPA_456` |
| ❓ Unbekannt | Simuliert eine unbekannte Karte → löst Fehlermeldung aus |

Die Testkarten `TEST_LENA_123` und `TEST_PAPA_456` werden beim Seeden automatisch in der Datenbank angelegt, wenn `DEV_MODE=true` aktiv ist.

### 🔍 Custom NFC-UID

Beliebige NFC-UID manuell eingeben und auf **Tap 💳** klicken — simuliert exakt denselben Ablauf wie ein echter NFC-Tap am Smartphone.

### ⚡ Actions & Links

| Button | Was |
|---|---|
| 🔢 PIN 1234 | Simuliert die Eingabe von PIN `1234` am Terminal |
| 📄 Bon (PDF) | Öffnet den letzten Bon als PDF im Browser |
| 📺 Terminal | Öffnet das Terminal in einem neuen Tab |
| ⚙️ Admin | Öffnet das Admin-Panel in einem neuen Tab |

---

## Vollständiger Test-Ablauf (ohne Hardware)

1. System starten: `docker compose up -d` (oder `flask run` lokal)
2. Kasse öffnen: `http://localhost`
3. Produkte in den Warenkorb legen
4. **Bezahlen** tippen → Zahlungsoverlay öffnet sich
5. **🧪** klicken → **👧 Lena** antippen → Zahlung wird verarbeitet
6. Bon anschauen: **📄 Bon (PDF)** klicken

Für PIN-Test:
- Im Admin-Panel unter Einstellungen → PIN-Modus → `Spielgeld-Modus (any_4_digits)` wählen
- Schritt 4–5 wiederholen → Terminal fragt nach PIN → **🔢 PIN 1234** klicken

---

## Hinweis für den Produktionsbetrieb

> ⚠️ **Dev-Modus vor dem Spielen mit Kindern deaktivieren!**  
> Im Dev-Modus sind Test-Karten registriert und der Simulator-Button sichtbar. Das verwirrt Kinder und ist für den echten Spielbetrieb nicht gedacht.

```bash
# .env anpassen
DEV_MODE=false
docker compose restart
```

Oder direkt im Admin-Panel → Einstellungen → *Entwickler-Modus deaktivieren*.

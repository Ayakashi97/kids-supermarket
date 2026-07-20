# 💳 NFC Reader Service (Raspberry Pi #2)

Standalone Python service running on Raspberry Pi #2 to poll PN532 NFC reader module and stream `card_tapped` events to Pi #1 Flask backend.

## Hardware Setup (PN532 I2C Mode)
Set DIP switches on PN532: `SEL0 = 1 (HIGH)`, `SEL1 = 0 (LOW)`.

Connections to Pi #2 GPIO:
- `VCC` -> Pin 1 (3.3V)
- `GND` -> Pin 6 (GND)
- `SDA` -> Pin 3 (GPIO 2)
- `SCL` -> Pin 5 (GPIO 3)

## Quick Start
```bash
git clone https://github.com/Ayakashi97/kids-supermarket.git
cd kids-supermarket/nfc_reader

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run hardware reader
python reader.py --server http://<pi1-ip>:5050

# Or run simulator (interactive console)
python reader.py --server http://<pi1-ip>:5050 --simulate
```

## Systemd Auto-Start
```bash
sudo cp supermarkt-nfc.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now supermarkt-nfc
```

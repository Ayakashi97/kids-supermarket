#!/usr/bin/env python3
"""
Kinder-Supermarkt — NFC Reader Service (Pi #2)
Polls PN532 module for NFC tags and emits WebSocket events to Pi #1 server.
"""

import sys
import time
import argparse
import logging
import socketio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] NFC Reader: %(message)s"
)
logger = logging.getLogger("nfc_reader")

# Initialize SocketIO Client
sio = socketio.Client(reconnection=True, reconnection_delay=2)

last_tapped_uid = None
last_tap_time = 0
DEBOUNCE_SECONDS = 3.0  # Prevent double-tapping within 3 seconds


@sio.event
def connect():
    logger.info("Successfully connected to Flask-SocketIO server!")


@sio.event
def disconnect():
    logger.warning("Disconnected from Flask-SocketIO server. Attempting reconnect...")


@sio.event
def status(data):
    logger.info("Server status received: %s", data)


def send_card_tapped(uid: str):
    global last_tapped_uid, last_tap_time
    now = time.time()

    # Rate-limit check
    if uid == last_tapped_uid and (now - last_tap_time) < DEBOUNCE_SECONDS:
        logger.debug("Debouncing repeated tap for UID: %s", uid)
        return

    last_tapped_uid = uid
    last_tap_time = now

    logger.info(">>> CARD TAPPED: UID = %s <<<", uid)
    sio.emit("card_tapped", {"uid": uid})


def init_pn532_reader():
    """Attempt to initialize hardware PN532 NFC reader via I2C or SPI."""
    try:
        import board
        import busio
        from digitalio import Direction
        from adafruit_pn532.i2c import PN532_I2C

        i2c = busio.I2C(board.SCL, board.SDA)
        pn532 = PN532_I2C(i2c, debug=False)
        ic, ver, rev, support = pn532.firmware_version
        logger.info("Found PN532 hardware firmware ver %d.%d", ver, rev)
        pn532.SAM_configuration()
        return pn532
    except Exception as e:
        logger.warning("Could not initialize hardware PN532 I2C: %s", e)
        return None


def run_hardware_loop(pn532):
    """Main polling loop for physical PN532 NFC module."""
    logger.info("Starting hardware NFC polling loop...")
    while True:
        try:
            uid = pn532.read_passive_target(timeout=0.5)
            if uid is not None:
                hex_uid = "".join([f"{x:02X}" for x in uid])
                send_card_tapped(hex_uid)
            time.sleep(0.1)
        except Exception as e:
            logger.error("Error during NFC poll: %s", e)
            time.sleep(1)


def run_simulation_loop():
    """Console interactive loop for testing without hardware."""
    logger.info("Running in SIMULATION mode. Type an NFC UID to simulate card tap.")
    print("\n--- NFC SIMULATOR ---")
    print("Type a card UID (e.g. CARD_LENA_123) and press ENTER:")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            line = input("NFC-Sim > ").strip()
            if line.lower() == "exit":
                break
            if line:
                send_card_tapped(line)
        except (KeyboardInterrupt, EOFError):
            break


def main():
    parser = argparse.ArgumentParser(description="Kinder-Supermarkt NFC Reader Service")
    parser.add_argument(
        "--server",
        default="http://localhost:5000",
        help="URL of Pi #1 Flask Backend (default: http://localhost:5000)"
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Force simulation mode for testing without PN532 hardware"
    )
    args = parser.parse_args()

    # Connect to Socket.IO Server
    try:
        logger.info("Connecting to server at %s ...", args.server)
        sio.connect(args.server)
    except Exception as e:
        logger.error("Failed to connect to server: %s. Continuing with auto-reconnect...", e)

    # Initialize Hardware PN532 or Simulation
    if not args.simulate:
        pn532 = init_pn532_reader()
        if pn532:
            run_hardware_loop(pn532)
            return

    # Fallback to simulation mode if hardware not detected or --simulate passed
    run_simulation_loop()


if __name__ == "__main__":
    main()

# Phase 4 Documentation — Receipt Printing (USB ESC/POS)

## Summary of Completed Work
Phase 4 integrates USB thermal receipt printing via `python-escpos` with dynamic administration configuration options.

### Key Features Implemented:
1. **ESC/POS Thermal Printer Service (`app/services/printer.py`)**:
   - Formats German receipts with header, receipt number, date, time, customer card holder name, itemized list, total, and thank-you footer.
   - Triggers automatic paper cutting (`printer.cut()`).

2. **Configurable via Admin Settings**:
   - Reads configuration dynamically from the database (`Setting` model) with fallbacks to `.env`:
     - `printer_enabled`: Enables or disables printing globally.
     - `printer_device`: System path to printer (e.g. `/dev/usb/lp0`).
     - `shop_name`: Name printed on header.
     - `receipt_header`: Custom message printed at top of receipt.
     - `receipt_footer`: Custom message printed at bottom of receipt.

3. **Graceful Hardware Fallback**:
   - If the USB printer is disconnected or the device path `/dev/usb/lp0` does not exist, the system logs the full mock receipt to stdout without interrupting or crashing the child's checkout flow.

---

## Phase 4 Checklist

- [x] ESC/POS USB thermal printer service implementation (`python-escpos`)
- [x] Format receipt in German (Shop name, date, time, card holder name, items, total, thank-you message)
- [x] Dynamic admin settings support (`printer_enabled`, `printer_device`, `shop_name`, `receipt_header`, `receipt_footer`)
- [x] Device passthrough via Docker (`/dev/usb/lp0`)
- [x] Fallback logging if printer disconnected

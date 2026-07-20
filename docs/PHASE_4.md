# Phase 4 Documentation — Receipt Printing & PDF Generator (USB ESC/POS)

## Summary of Completed Work
Phase 4 integrates USB thermal receipt printing via `python-escpos` with dynamic administration configuration options and on-screen PDF receipt generation.

### Key Features Implemented:
1. **ESC/POS Thermal Printer Service (`app/services/printer.py`)**:
   - Formats German receipts with header, receipt number, date, time, customer card holder name, itemized list, total, and thank-you footer.
   - Triggers automatic paper cutting (`printer.cut()`).

2. **Fully Editable Receipt Layout via Admin Settings (`/admin/settings`)**:
   - All receipt elements are customizable by parents in the admin panel:
     - `shop_name`: Shop title header (e.g. *"Kinder-Markt"*).
     - `receipt_header`: Custom top subheader message.
     - `receipt_footer`: Custom bottom footer message.
     - `paper_width`: Thermal paper size choice (**58 mm** or **80 mm**).
     - `show_card_name`: Toggle customer name display (*"Kunde: Lena 💳"*).
     - `show_date_time`: Toggle date/time display.
     - `printer_enabled`: Enable or disable hardware printing.
     - `printer_device`: System path to USB printer device (`/dev/usb/lp0`).

3. **PDF & Web Receipt Generator (`/receipt/<tx_id>` & `/receipt/preview`)**:
   - Renders a pixel-perfect thermal receipt layout on screen matching the configured paper width.
   - Includes a **"Drucken / als PDF speichern 📄"** button to export/print receipts as PDF documents.
   - Admin settings page includes a **"Bon Vorschau / PDF 📄"** button to preview layout changes in real time.

4. **Graceful Hardware Fallback**:
   - If the USB printer is disconnected or `/dev/usb/lp0` does not exist, the system logs the mock receipt output to stdout without interrupting or crashing the child's checkout flow.

---

## Phase 4 Checklist

- [x] ESC/POS USB thermal printer service implementation (`python-escpos`)
- [x] Format receipt in German (Shop name, date, time, card holder name, items, total, thank-you message)
- [x] Dynamic admin settings support (`printer_enabled`, `printer_device`, `shop_name`, `receipt_header`, `receipt_footer`, `paper_width`, `show_card_name`, `show_date_time`)
- [x] PDF & Printable Web Receipt generator (`/receipt/<tx_id>` & `/receipt/preview`)
- [x] Device passthrough via Docker (`/dev/usb/lp0`)
- [x] Fallback logging if printer disconnected

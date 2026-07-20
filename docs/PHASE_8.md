# 📱 Phase 8 Documentation — Smartphone Web NFC, Dual PWA & Dynamic Customization

Phase 8 migrated the payment terminal from a legacy hardware Raspberry Pi #2 to any old Android Smartphone or iPhone, introducing native Web NFC scanning, dual PWA installation, persistent NFC permission state, favicons, safe area spacing, and fully dynamic shop naming.

---

## 🌟 Key Features Implemented

### 1. Web NFC API for Android Smartphones
- Integrated `window.NDEFReader` in `/terminal` and `/admin/cards`.
- Android Chrome reads physical NFC cards/tags/stickers directly via built-in smartphone NFC hardware.
- Decodes both hardware serial numbers (`event.serialNumber`) and NDEF text/URL records (`event.message.records`).

### 2. Persistent NFC Permission State (`localStorage`)
- When `NDEFReader.scan()` succeeds once, the state is persisted:
  `localStorage.setItem("nfc_permission_granted", "true");`
- The green *"NFC-Leser auf Handy aktivieren"* button is hidden permanently so users never need to re-trigger activation on subsequent visits!

### 3. Dual PWA Manifests & Fullscreen App Mode
- **Cashier PWA**: Configured in `/manifest.json` (`start_url: "/"`, name: *"Kinder-Supermarkt Kasse"*).
- **Terminal PWA**: Configured in `/manifest-terminal.json` (`start_url: "/terminal"`, name: *"Kinder-Supermarkt Terminal"*).
- Both manifests utilize `"display": "fullscreen"` to open as borderless edge-to-edge apps when launched from Android or iOS Home Screen.

### 4. Dynamic Shop Name Customization (`shop_name`)
- Admin settings (`/admin/settings`) allows updating `shop_name` (e.g. *Emmis Kaufladen*, *Kinder-Supermarkt*, *Lenas Mini-Markt*).
- The setting propagates dynamically to:
  - Cashier UI Header (`<h1>🛒 {{ shop_name }}</h1>`)
  - Terminal UI Header & Idle Screen (`<span>🛒 {{ shop_name }}</span>`)
  - Thermal ESC/POS Receipts & PDF Receipt Generator
  - Page titles and Apple Web App titles

### 5. Responsive Layout Bounds & Safe Area Spacing
- Fixed flexbox height bounds (`min-height: 0`) preventing clipped cart panels or hidden payment buttons.
- Applied safe area insets (`env(safe-area-inset-top)` / `env(safe-area-inset-bottom)`) so headers and glass cards sit comfortably below camera notches and screen edges.

### 6. Favicon Integration
- Generated `favicon.png`, `favicon.ico`, and `apple-touch-icon.png` via `app/static/images/gen_icons.py`.
- Linked icons across all views in `app/templates/base.html`.

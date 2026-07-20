# Phase 3 Documentation — Payment Flow & Card Lookup (WebSocket)

## Summary of Completed Work
Phase 3 implements the real-time WebSocket state machine and database card lookup for processing payment transactions.

### Key Components Implemented:
1. **Server State Machine (`app/services/socket_events.py`)**:
   - Maintains server modes: `idle`, `waiting_for_payment`, `waiting_for_registration`.
   - Stores `pending_cart` during payment checkout.

2. **WebSocket Event Handlers**:
   - `start_payment`: Received from tablet cashier UI with cart items (`[{ id, name, price_cents, quantity, emoji }, ...]`). Transitions server state to `waiting_for_payment` and broadcasts `waiting_for_payment` event to all connected clients (Tablet & Pi #2 Touchscreen Terminal).
   - `cancel_payment`: Resets server state to `idle` and notifies clients.
   - `card_tapped`: Received from NFC reader on Pi #2 with card UID (`{ uid: "RAW_NFC_UID" }`).

3. **Card Lookup & Transaction Persistence**:
   - Queries `Card` table by `nfc_uid`.
   - **Unknown Card**: Emits `payment_error` with `"Unbekannte Karte 😕"`.
   - **Inactive Card**: Emits `payment_error` with `"Karte ist inaktiv 🚫"`.
   - **Valid Active Card**:
     - Creates `Transaction` record (`total_cents`, `card_id`, `nfc_uid`, `status="completed"`).
     - Creates `TransactionItem` records snapshotting item names, prices, and quantities.
     - Updates `card.last_used_at` timestamp.
     - Triggers thermal receipt printing (`print_receipt`).
     - Emits `payment_success` with `{ transaction_id, total_cents, total_formatted, card_name, card_image_url }` to all clients.
     - Resets server state to `idle`.

4. **Card Registration Support**:
   - `start_registration`: Transitions state to `waiting_for_registration`.
   - On `card_tapped` during registration mode, captures UID into `server_state["captured_uid"]` and emits `card_captured` event for admin card enrollment.

---

## Phase 3 Checklist

- [x] Implement Flask-SocketIO event handlers (`start_payment`, `card_tapped`, `payment_success`, `payment_error`, `cancel_payment`, `start_registration`)
- [x] Server maintains state machine: `idle` / `waiting_for_payment` / `waiting_for_registration`
- [x] NFC card lookup in `Card` table (known card → greeting + photo; unknown card → error)
- [x] Fullscreen overlay "Karte hinhalten! 💳" with pulsing animation
- [x] Success overlay with card holder photo + "Hallo [Name]! 🎉"
- [x] Save transaction to DB (Transaction + TransactionItems linked to Card)

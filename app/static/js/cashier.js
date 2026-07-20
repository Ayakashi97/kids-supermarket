/**
 * Kinder-Supermarkt - Cashier UI & Cart System
 * Plain JavaScript (Vanilla JS) + Web Audio API + Socket.IO
 */

window.toggleFullscreen = function() {
    if (!document.fullscreenElement) {
        if (document.documentElement.requestFullscreen) {
            document.documentElement.requestFullscreen().catch(err => console.warn(err));
        } else if (document.documentElement.webkitRequestFullscreen) {
            document.documentElement.webkitRequestFullscreen();
        }
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen().catch(err => console.warn(err));
        }
    }
};

// 10-Minute Screen Wake Lock to prevent phone/tablet screen timeout during play
let cashierWakeLock = null;
let cashierWakeLockTimer = null;
const TEN_MINUTES_MS = 10 * 60 * 1000;

async function requestCashierWakeLock() {
    if ('wakeLock' in navigator) {
        try {
            if (!cashierWakeLock) {
                cashierWakeLock = await navigator.wakeLock.request('screen');
                console.log("Cashier 10-Minute Screen Wake Lock active!");
            }
            if (cashierWakeLockTimer) clearTimeout(cashierWakeLockTimer);
            cashierWakeLockTimer = setTimeout(() => {
                releaseCashierWakeLock();
            }, TEN_MINUTES_MS);
        } catch (err) {
            console.warn("Cashier Wake Lock request error:", err);
        }
    }
}

function releaseCashierWakeLock() {
    if (cashierWakeLock) {
        cashierWakeLock.release().then(() => {
            cashierWakeLock = null;
            console.log("Cashier Wake Lock released after 10 minutes.");
        }).catch(err => console.warn(err));
    }
    if (cashierWakeLockTimer) {
        clearTimeout(cashierWakeLockTimer);
        cashierWakeLockTimer = null;
    }
}

document.addEventListener("pointerdown", () => {
    requestCashierWakeLock();
});

document.addEventListener("visibilitychange", () => {
    if (document.visibilityState === "visible") {
        requestCashierWakeLock();
    }
});

document.addEventListener("DOMContentLoaded", () => {
    requestCashierWakeLock();
    // --- Audio Context for Kid Sounds ---
    let audioCtx = null;

    function initAudio() {
        if (!audioCtx) {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (audioCtx.state === "suspended") {
            audioCtx.resume();
        }
    }

    // Sound: Cheerful item add beep
    function playBeepSound() {
        initAudio();
        try {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();

            osc.type = "sine";
            osc.frequency.setValueAtTime(880, audioCtx.currentTime); // A5
            osc.frequency.exponentialRampToValueAtTime(1320, audioCtx.currentTime + 0.08); // E6

            gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);

            osc.connect(gain);
            gain.connect(audioCtx.destination);

            osc.start();
            osc.stop(audioCtx.currentTime + 0.1);
        } catch (e) {
            console.warn("Audio play error:", e);
        }
    }

    // Sound: Celebratory fanfare on payment success
    function playSuccessSound() {
        initAudio();
        try {
            const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
            notes.forEach((freq, index) => {
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();

                osc.type = "triangle";
                osc.frequency.setValueAtTime(freq, audioCtx.currentTime + index * 0.1);

                gain.gain.setValueAtTime(0.4, audioCtx.currentTime + index * 0.1);
                gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + index * 0.1 + 0.25);

                osc.connect(gain);
                gain.connect(audioCtx.destination);

                osc.start(audioCtx.currentTime + index * 0.1);
                osc.stop(audioCtx.currentTime + index * 0.1 + 0.25);
            });
        } catch (e) {
            console.warn("Success sound error:", e);
        }
    }

    // Sound: Friendly error sound
    function playErrorSound() {
        initAudio();
        try {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();

            osc.type = "sawtooth";
            osc.frequency.setValueAtTime(220, audioCtx.currentTime); // A3
            osc.frequency.setValueAtTime(180, audioCtx.currentTime + 0.15); // Lower note

            gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.3);

            osc.connect(gain);
            gain.connect(audioCtx.destination);

            osc.start();
            osc.stop(audioCtx.currentTime + 0.3);
        } catch (e) {
            console.warn("Error sound error:", e);
        }
    }

    // --- State & DOM Elements ---
    let cart = []; // Array of { id, name, price_cents, emoji, quantity }
    
    const cartContainer = document.getElementById("cartItemsContainer");
    const emptyCartMsg = document.getElementById("emptyCartMsg");
    const totalAmountEl = document.getElementById("totalAmount");
    const payBtn = document.getElementById("payBtn");
    const clearCartBtn = document.getElementById("clearCartBtn");
    const productCards = document.querySelectorAll(".product-card");
    const tabBtns = document.querySelectorAll(".tab-btn");

    // Overlays
    const paymentOverlay = document.getElementById("paymentOverlay");
    const overlayTitle = document.getElementById("overlayTitle");
    const overlaySubtitle = document.getElementById("overlaySubtitle");
    const overlayIcon = document.getElementById("overlayIcon");
    const photoContainer = document.getElementById("photoContainer");
    const cardPhoto = document.getElementById("cardPhoto");
    const cancelPayBtn = document.getElementById("cancelPayBtn");

    // --- Socket.IO Client Setup ---
    window.socket = io();
    const socket = window.socket;

    socket.on("connect", () => {
        console.log("Connected to server WebSocket!");
    });

    socket.on("waiting_for_payment", () => {
        showPaymentWaitingOverlay();
    });

    socket.on("prompt_pin", (data) => {
        showPaymentPinPromptOverlay(data);
    });

    socket.on("pin_error", (data) => {
        showPaymentPinErrorOverlay(data.message || "Falsche PIN! ❌");
    });

    let cashierAutoCloseTimer = null;

    socket.on("payment_success", (data) => {
        playSuccessSound();
        showPaymentSuccessOverlay(data);

        const barContainer = document.getElementById("successCountdownBarContainer");
        const bar = document.getElementById("successCountdownBar");
        if (barContainer && bar) {
            barContainer.style.display = "block";
            bar.style.transition = "none";
            bar.style.width = "100%";
            void bar.offsetWidth; // Force layout reflow
            bar.style.transition = "width 8s linear";
            bar.style.width = "0%";
        }

        if (cashierAutoCloseTimer) clearTimeout(cashierAutoCloseTimer);
        cashierAutoCloseTimer = setTimeout(() => {
            clearCart();
            hideOverlay();
        }, 8000);
    });

    socket.on("payment_error", (data) => {
        playErrorSound();
        showPaymentErrorOverlay(data.message || "Unbekannte Karte 😕");
        setTimeout(() => {
            hideOverlay();
        }, 2500);
    });

    // --- Cart Actions ---
    function addToCart(productId, name, priceCents, emoji) {
        playBeepSound();

        const existing = cart.find(item => item.id === productId);
        if (existing) {
            existing.quantity += 1;
        } else {
            cart.push({
                id: productId,
                name: name,
                price_cents: priceCents,
                emoji: emoji,
                quantity: 1
            });
        }
        renderCart();
    }

    function changeQuantity(productId, delta) {
        const item = cart.find(i => i.id === productId);
        if (!item) return;

        item.quantity += delta;
        if (item.quantity <= 0) {
            cart = cart.filter(i => i.id !== productId);
        }
        renderCart();
    }

    function clearCart() {
        cart = [];
        renderCart();
    }

    function formatCurrency(cents) {
        return (cents / 100).toFixed(2).replace(".", ",") + " €";
    }

    function getTotalCents() {
        return cart.reduce((sum, item) => sum + (item.price_cents * item.quantity), 0);
    }

    // Render cart items to DOM
    function renderCart() {
        if (cart.length === 0) {
            emptyCartMsg.style.display = "block";
            cartContainer.innerHTML = "";
            cartContainer.appendChild(emptyCartMsg);
            totalAmountEl.textContent = "0,00 €";
            payBtn.disabled = true;
            return;
        }

        emptyCartMsg.style.display = "none";
        cartContainer.innerHTML = "";

        cart.forEach(item => {
            const itemEl = document.createElement("div");
            itemEl.className = "cart-item";
            itemEl.innerHTML = `
                <div class="cart-item-info">
                    <span class="cart-item-emoji">${item.emoji || '🛒'}</span>
                    <div class="cart-item-details">
                        <span class="cart-item-name">${item.name}</span>
                        <span class="cart-item-price">${formatCurrency(item.price_cents * item.quantity)}</span>
                    </div>
                </div>
                <div class="qty-controls">
                    <button class="qty-btn minus" data-id="${item.id}">-</button>
                    <span class="qty-count">${item.quantity}</span>
                    <button class="qty-btn plus" data-id="${item.id}">+</button>
                </div>
            `;

            itemEl.querySelector(".minus").addEventListener("click", () => changeQuantity(item.id, -1));
            itemEl.querySelector(".plus").addEventListener("click", () => {
                playBeepSound();
                changeQuantity(item.id, 1);
            });

            cartContainer.appendChild(itemEl);
        });

        totalAmountEl.textContent = formatCurrency(getTotalCents());
        payBtn.disabled = false;
    }

    // --- Product Click Handlers ---
    productCards.forEach(card => {
        card.addEventListener("click", () => {
            const id = parseInt(card.getAttribute("data-id"));
            const name = card.getAttribute("data-name");
            const price = parseInt(card.getAttribute("data-price"));
            const emoji = card.getAttribute("data-emoji");
            addToCart(id, name, price, emoji);
        });
    });

    // --- Category Filter Tabs ---
    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            tabBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            const selectedCat = btn.getAttribute("data-category");

            productCards.forEach(card => {
                const cardCat = card.getAttribute("data-category");
                if (selectedCat === "all" || cardCat === selectedCat) {
                    card.style.display = "flex";
                } else {
                    card.style.display = "none";
                }
            });
        });
    });

    // Clear cart button
    clearCartBtn.addEventListener("click", () => {
        if (cart.length > 0) {
            clearCart();
        }
    });

    // Pay button handler
    payBtn.addEventListener("click", () => {
        if (cart.length === 0) return;
        initAudio();
        
        socket.emit("start_payment", { cart: cart });
        showPaymentWaitingOverlay();
    });

    // Cancel payment button handler
    cancelPayBtn.addEventListener("click", () => {
        socket.emit("cancel_payment");
        hideOverlay();
    });

    // --- Overlay UI Functions ---
    function showPaymentWaitingOverlay() {
        overlayTitle.textContent = "Karte hinhalten! 💳";
        overlaySubtitle.textContent = "Halte deine Supermarkt-Karte an das Lesegerät...";
        overlayIcon.textContent = "💳";
        overlayIcon.style.display = "block";
        photoContainer.style.display = "none";
        cancelPayBtn.style.display = "block";
        paymentOverlay.classList.remove("hidden");
    }

    function showPaymentPinPromptOverlay(data) {
        overlayTitle.textContent = data.card_name ? `Hallo ${data.card_name}! 🔢` : "PIN eingeben 🔢";
        overlaySubtitle.textContent = "Warte auf PIN-Eingabe am Lesegerät...";
        overlayIcon.textContent = "🔢";
        overlayIcon.style.display = "block";
        photoContainer.style.display = "none";
        cancelPayBtn.style.display = "block";
        paymentOverlay.classList.remove("hidden");
    }

    function showPaymentPinErrorOverlay(msg) {
        playErrorSound();
        overlayTitle.textContent = "Falsche PIN ❌";
        overlaySubtitle.textContent = msg || "Bitte 4-stellige Geheimzahl erneut eingeben.";
        overlayIcon.textContent = "⚠️";
        overlayIcon.style.display = "block";
        photoContainer.style.display = "none";
        cancelPayBtn.style.display = "block";
        paymentOverlay.classList.remove("hidden");
    }

    let currentTransactionId = null;

    const receiptActions = document.getElementById("receiptActions");
    const btnPrintReceiptBtn = document.getElementById("btnPrintReceiptBtn");
    const closeSuccessBtn = document.getElementById("closeSuccessBtn");
    const printStatusMsg = document.getElementById("printStatusMsg");

    if (btnPrintReceiptBtn) {
        btnPrintReceiptBtn.addEventListener("click", () => {
            if (!currentTransactionId) return;
            btnPrintReceiptBtn.disabled = true;
            btnPrintReceiptBtn.textContent = "⏳";
            socket.emit("request_print_receipt", { transaction_id: currentTransactionId });
        });
    }

    if (closeSuccessBtn) {
        closeSuccessBtn.addEventListener("click", () => {
            clearCart();
            hideOverlay();
        });
    }

    socket.on("print_result", (res) => {
        if (!btnPrintReceiptBtn || !printStatusMsg) return;
        printStatusMsg.style.display = "block";
        if (res && res.success) {
            printStatusMsg.style.color = "#2ecc71";
            printStatusMsg.textContent = res.message || "Bon gedruckt! 🧾";
            btnPrintReceiptBtn.textContent = "✅";
            btnPrintReceiptBtn.disabled = false;
        } else {
            printStatusMsg.style.color = "#f39c12";
            printStatusMsg.textContent = res.message || "Drucker nicht erreichbar";
            btnPrintReceiptBtn.textContent = "🖨️";
            btnPrintReceiptBtn.disabled = false;
        }
    });

    function showPaymentSuccessOverlay(data) {
        currentTransactionId = data.transaction_id || null;
        overlayTitle.textContent = data.card_name ? `Hallo ${data.card_name}! 🎉` : "Bezahlt! 🎉";
        overlaySubtitle.textContent = `Gesamtsumme: ${formatCurrency(data.total_cents || getTotalCents())}`;

        if (data.card_image_url) {
            cardPhoto.src = data.card_image_url;
            photoContainer.style.display = "block";
            overlayIcon.style.display = "none";
        } else {
            photoContainer.style.display = "none";
            overlayIcon.textContent = "🎉";
            overlayIcon.style.display = "block";
        }

        if (receiptActions && data.transaction_id) {
            receiptActions.style.display = "flex";
            if (btnPrintReceiptBtn) {
                btnPrintReceiptBtn.disabled = false;
                btnPrintReceiptBtn.textContent = "🖨️";
            }
            if (printStatusMsg) {
                printStatusMsg.style.display = "none";
                printStatusMsg.textContent = "";
            }
            cancelPayBtn.style.display = "none";
        } else {
            cancelPayBtn.textContent = "Fertig / Schließen ❌";
            cancelPayBtn.style.display = "block";
        }

        paymentOverlay.classList.remove("hidden");
    }

    function showPaymentErrorOverlay(msg) {
        overlayTitle.textContent = "Hoppla! 😕";
        overlaySubtitle.textContent = msg;
        overlayIcon.textContent = "⚠️";
        overlayIcon.style.display = "block";
        photoContainer.style.display = "none";
        if (receiptActions) receiptActions.style.display = "none";
        cancelPayBtn.textContent = "Schließen ❌";
        cancelPayBtn.style.display = "block";
        paymentOverlay.classList.remove("hidden");
    }

    function hideOverlay() {
        if (cashierAutoCloseTimer) {
            clearTimeout(cashierAutoCloseTimer);
            cashierAutoCloseTimer = null;
        }
        const barContainer = document.getElementById("successCountdownBarContainer");
        if (barContainer) barContainer.style.display = "none";

        paymentOverlay.classList.add("hidden");
        if (receiptActions) receiptActions.style.display = "none";
        cancelPayBtn.textContent = "Abbrechen ❌";
    }
});

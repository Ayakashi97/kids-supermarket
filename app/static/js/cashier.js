/**
 * Kinder-Supermarkt - Cashier UI & Cart System
 * Plain JavaScript (Vanilla JS) + Web Audio API + Socket.IO
 */

document.addEventListener("DOMContentLoaded", () => {
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

    socket.on("payment_success", (data) => {
        playSuccessSound();
        showPaymentSuccessOverlay(data);
        setTimeout(() => {
            clearCart();
            hideOverlay();
        }, 3500);
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

    function showPaymentSuccessOverlay(data) {
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

        cancelPayBtn.style.display = "none";
        paymentOverlay.classList.remove("hidden");
    }

    function showPaymentErrorOverlay(msg) {
        overlayTitle.textContent = "Hoppla! 😕";
        overlaySubtitle.textContent = msg;
        overlayIcon.textContent = "⚠️";
        overlayIcon.style.display = "block";
        photoContainer.style.display = "none";
        cancelPayBtn.style.display = "none";
        paymentOverlay.classList.remove("hidden");
    }

    function hideOverlay() {
        paymentOverlay.classList.add("hidden");
    }
});

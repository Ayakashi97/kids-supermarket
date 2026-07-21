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

// Prevent rubberband dragging & page scrolling when kids tap/swipe on cashier UI
document.addEventListener("touchmove", (e) => {
    if (!e.target.closest("#cartItemsContainer") && !e.target.closest("#categorySidebar")) {
        e.preventDefault();
    }
}, { passive: false });

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

    // Sound: Soft descending tone when removing an item
    function playRemoveSound() {
        initAudio();
        try {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();

            osc.type = "sine";
            osc.frequency.setValueAtTime(600, audioCtx.currentTime); // D5
            osc.frequency.exponentialRampToValueAtTime(300, audioCtx.currentTime + 0.12); // D4

            gain.gain.setValueAtTime(0.25, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.12);

            osc.connect(gain);
            gain.connect(audioCtx.destination);

            osc.start();
            osc.stop(audioCtx.currentTime + 0.12);
        } catch (e) {
            console.warn("Remove sound error:", e);
        }
    }

    // Sound: Whoosh/sweep sound when emptying the entire cart
    function playClearSound() {
        initAudio();
        try {
            const notes = [440, 330, 220]; // A4, E4, A3
            notes.forEach((freq, idx) => {
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();

                osc.type = "sine";
                osc.frequency.setValueAtTime(freq, audioCtx.currentTime + idx * 0.06);

                gain.gain.setValueAtTime(0.25, audioCtx.currentTime + idx * 0.06);
                gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + idx * 0.06 + 0.1);

                osc.connect(gain);
                gain.connect(audioCtx.destination);

                osc.start(audioCtx.currentTime + idx * 0.06);
                osc.stop(audioCtx.currentTime + idx * 0.06 + 0.1);
            });
        } catch (e) {
            console.warn("Clear sound error:", e);
        }
    }

    // Sound: Payment process started chime
    function playPaymentStartSound() {
        initAudio();
        try {
            const notes = [523.25, 659.25, 880.00]; // C5, E5, A5
            notes.forEach((freq, idx) => {
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();

                osc.type = "sine";
                osc.frequency.setValueAtTime(freq, audioCtx.currentTime + idx * 0.08);

                gain.gain.setValueAtTime(0.35, audioCtx.currentTime + idx * 0.08);
                gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + idx * 0.08 + 0.15);

                osc.connect(gain);
                gain.connect(audioCtx.destination);

                osc.start(audioCtx.currentTime + idx * 0.08);
                osc.stop(audioCtx.currentTime + idx * 0.08 + 0.15);
            });
        } catch (e) {
            console.warn("Payment start sound error:", e);
        }
    }

    // Sound: Classic supermarket barcode scanner beep (sharp, high-pitched, short)
    function playScannerSound() {
        initAudio();
        try {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = "square";
            osc.frequency.setValueAtTime(1900, audioCtx.currentTime);
            gain.gain.setValueAtTime(0.18, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.08);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + 0.08);
        } catch (e) {
            console.warn("Scanner sound error:", e);
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

    socket.on("product_scanned", (data) => {
        // Only handle when no payment process is active (overlay hidden)
        if (!paymentOverlay.classList.contains("hidden")) return;

        // Quietly add product to cart (sound is played on the terminal device)
        addToCart(data.id, data.name, data.price_cents, data.emoji, true);

        // Brief NFC scan banner at top of cashier UI
        const banner = document.getElementById('nfcScanBanner');
        if (banner) {
            banner.textContent = `🏷️ ${data.emoji || ''} ${data.name} — ${data.price_formatted} hinzugefügt!`;
            banner.classList.remove('hidden');
            clearTimeout(window._bannerTimer);
            window._bannerTimer = setTimeout(() => banner.classList.add('hidden'), 3000);
        }
    });

    // --- Cart Actions ---
    function addToCart(productId, name, priceCents, emoji, silent = false) {
        if (!silent) playBeepSound();

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

        if (delta < 0) {
            playRemoveSound();
        } else if (delta > 0) {
            playBeepSound();
        }

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

            const infoDiv = document.createElement("div");
            infoDiv.className = "cart-item-info";

            const emojiSpan = document.createElement("span");
            emojiSpan.className = "cart-item-emoji";
            emojiSpan.textContent = item.emoji || '\uD83D\uDED2';

            const detailsDiv = document.createElement("div");
            detailsDiv.className = "cart-item-details";

            const nameSpan = document.createElement("span");
            nameSpan.className = "cart-item-name";
            nameSpan.textContent = item.name;

            const priceSpan = document.createElement("span");
            priceSpan.className = "cart-item-price";
            priceSpan.textContent = formatCurrency(item.price_cents * item.quantity);

            detailsDiv.appendChild(nameSpan);
            detailsDiv.appendChild(priceSpan);
            infoDiv.appendChild(emojiSpan);
            infoDiv.appendChild(detailsDiv);

            const qtyDiv = document.createElement("div");
            qtyDiv.className = "qty-controls";

            const minusBtn = document.createElement("button");
            minusBtn.className = "qty-btn minus";
            minusBtn.dataset.id = item.id;
            minusBtn.textContent = "-";

            const qtySpan = document.createElement("span");
            qtySpan.className = "qty-count";
            qtySpan.textContent = item.quantity;

            const plusBtn = document.createElement("button");
            plusBtn.className = "qty-btn plus";
            plusBtn.dataset.id = item.id;
            plusBtn.textContent = "+";

            qtyDiv.appendChild(minusBtn);
            qtyDiv.appendChild(qtySpan);
            qtyDiv.appendChild(plusBtn);

            itemEl.appendChild(infoDiv);
            itemEl.appendChild(qtyDiv);

            attachKidTouchHandler(minusBtn, () => changeQuantity(item.id, -1));
            attachKidTouchHandler(plusBtn, () => changeQuantity(item.id, 1));

            cartContainer.appendChild(itemEl);
        });

        totalAmountEl.textContent = formatCurrency(getTotalCents());
        payBtn.disabled = false;
    }

    // --- Pagination System ---
    let currentPage = 0;
    let currentCategory = "all";
    const prevPageBtn = document.getElementById("prevPageBtn");
    const nextPageBtn = document.getElementById("nextPageBtn");
    const pageIndicator = document.getElementById("pageIndicator");
    const productGrid = document.getElementById("productGrid");

    if ('orientation' in screen && screen.orientation.lock) {
        screen.orientation.lock('landscape').catch(err => console.warn("Cashier orientation lock:", err));
    }

    function calculateItemsPerPage() {
        if (!productGrid) return 8;
        const gridWidth = productGrid.clientWidth || 600;
        const gridHeight = productGrid.clientHeight || 400;
        const cols = Math.max(1, Math.floor(gridWidth / 175));
        const rows = Math.max(1, Math.floor(gridHeight / 195));
        return Math.max(4, cols * rows);
    }

    function getVisibleCards() {
        const cards = Array.from(productCards);
        if (currentCategory === "all") return cards;
        return cards.filter(card => card.getAttribute("data-category") === currentCategory);
    }

    function renderPage() {
        const visibleCards = getVisibleCards();
        const itemsPerPage = calculateItemsPerPage();
        const totalPages = Math.max(1, Math.ceil(visibleCards.length / itemsPerPage));

        if (currentPage >= totalPages) currentPage = totalPages - 1;
        if (currentPage < 0) currentPage = 0;

        productCards.forEach(card => card.style.display = "none");

        const startIdx = currentPage * itemsPerPage;
        const endIdx = startIdx + itemsPerPage;
        const pageCards = visibleCards.slice(startIdx, endIdx);

        pageCards.forEach(card => card.style.display = "flex");

        if (pageIndicator) {
            pageIndicator.textContent = `Seite ${currentPage + 1} / ${totalPages}`;
        }

        if (prevPageBtn) prevPageBtn.disabled = (currentPage <= 0);
        if (nextPageBtn) nextPageBtn.disabled = (currentPage >= totalPages - 1);
    }

    // --- Kid-Friendly Reusable Touch Handler ---
    function attachKidTouchHandler(btn, onAction) {
        if (!btn) return;
        let isTouching = false;
        let lastActionTime = 0;

        function triggerAction(e) {
            if (e) {
                e.preventDefault();
                e.stopPropagation();
            }
            const now = Date.now();
            if (now - lastActionTime < 300) return;
            lastActionTime = now;
            onAction();
        }

        btn.addEventListener("pointerdown", () => {
            if (btn.disabled) return;
            isTouching = true;
            btn.classList.add("pressed");
        });

        btn.addEventListener("pointermove", () => {
            if (isTouching) {
                btn.classList.add("pressed");
            }
        });

        btn.addEventListener("pointerup", (e) => {
            if (isTouching) {
                isTouching = false;
                btn.classList.remove("pressed");
                if (!btn.disabled) triggerAction(e);
            }
        });

        btn.addEventListener("pointercancel", () => {
            if (isTouching) {
                isTouching = false;
                btn.classList.remove("pressed");
                if (!btn.disabled) triggerAction();
            }
        });

        btn.addEventListener("click", (e) => {
            if (!btn.disabled) triggerAction(e);
        });
    }

    if (prevPageBtn) {
        attachKidTouchHandler(prevPageBtn, () => {
            if (currentPage > 0) {
                currentPage--;
                renderPage();
                playBeepSound();
            }
        });
    }

    if (nextPageBtn) {
        attachKidTouchHandler(nextPageBtn, () => {
            const visibleCards = getVisibleCards();
            const itemsPerPage = calculateItemsPerPage();
            const totalPages = Math.max(1, Math.ceil(visibleCards.length / itemsPerPage));
            if (currentPage < totalPages - 1) {
                currentPage++;
                renderPage();
                playBeepSound();
            }
        });
    }

    window.addEventListener("resize", () => {
        renderPage();
    });

    // --- Product Click & Kid-Friendly Touch Handlers ---
    productCards.forEach(card => {
        let isTouching = false;
        let lastSelectedTime = 0;

        function handleSelectProduct() {
            const now = Date.now();
            if (now - lastSelectedTime < 300) return; // Prevent fast double-triggering
            lastSelectedTime = now;

            const id = parseInt(card.getAttribute("data-id"));
            const name = card.getAttribute("data-name");
            const price = parseInt(card.getAttribute("data-price"));
            const emoji = card.getAttribute("data-emoji");
            addToCart(id, name, price, emoji);

            card.classList.add("card-pop");
            setTimeout(() => card.classList.remove("card-pop"), 300);
        }

        card.addEventListener("pointerdown", () => {
            isTouching = true;
            card.classList.add("pressed");
        });

        card.addEventListener("pointermove", () => {
            if (isTouching) {
                card.classList.add("pressed");
            }
        });

        window.addEventListener("pointerup", () => {
            if (isTouching) {
                isTouching = false;
                card.classList.remove("pressed");
                handleSelectProduct();
            }
        });

        card.addEventListener("pointercancel", () => {
            if (isTouching) {
                isTouching = false;
                card.classList.remove("pressed");
                handleSelectProduct();
            }
        });

        card.addEventListener("click", () => {
            handleSelectProduct();
        });
    });

    // --- Category Sidebar & More Modal Navigation ---
    const btnCategoryMore = document.getElementById("btnCategoryMore");
    const categoryMoreOverlay = document.getElementById("categoryMoreOverlay");
    const closeCategoryModalBtn = document.getElementById("closeCategoryModalBtn");
    const catSidebarBtns = document.querySelectorAll(".cat-sidebar-btn:not(.cat-more-btn)");
    const catModalBtns = document.querySelectorAll(".cat-modal-btn");

    function updateCategorySidebarOverflow() {
        const categorySidebar = document.getElementById("categorySidebar");
        if (!categorySidebar) return;

        const sidebarHeight = categorySidebar.clientHeight || 400;
        const maxFit = Math.max(2, Math.floor((sidebarHeight - 10) / 83));

        if (catSidebarBtns.length > maxFit) {
            // Find index, name, and emoji of currently selected category in catSidebarBtns
            let activeIdx = -1;
            let activeCatName = "";
            let activeCatEmoji = "";

            catSidebarBtns.forEach((btn, idx) => {
                if (btn.getAttribute("data-category") === currentCategory) {
                    activeIdx = idx;
                    activeCatName = btn.querySelector(".cat-name")?.textContent || currentCategory;
                    activeCatEmoji = btn.querySelector(".cat-emoji")?.textContent || "📦";
                }
            });

            // Standard slots: 0 to maxFit - 2
            let visibleIndices = [];
            for (let i = 0; i < maxFit - 1; i++) {
                visibleIndices.push(i);
            }

            // If active category is in hidden slots (activeIdx >= maxFit - 1),
            // replace the last category slot before "Mehr..." with the active category
            if (activeIdx >= maxFit - 1) {
                visibleIndices[maxFit - 2] = activeIdx;
            }

            catSidebarBtns.forEach((btn, idx) => {
                if (visibleIndices.includes(idx)) {
                    btn.style.display = "flex";
                } else {
                    btn.style.display = "none";
                }
            });

            if (btnCategoryMore) {
                btnCategoryMore.style.display = "flex";
                const moreEmojiSpan = btnCategoryMore.querySelector(".cat-emoji");
                const moreNameSpan = btnCategoryMore.querySelector(".cat-name");

                // If a hidden category (selected via Mehr...) is active, also highlight the Mehr... button!
                if (activeIdx >= maxFit - 1) {
                    btnCategoryMore.classList.add("active");
                    if (moreEmojiSpan) moreEmojiSpan.textContent = activeCatEmoji;
                    if (moreNameSpan) moreNameSpan.textContent = activeCatName + " ➕";
                } else {
                    btnCategoryMore.classList.remove("active");
                    if (moreEmojiSpan) moreEmojiSpan.textContent = "➕";
                    if (moreNameSpan) moreNameSpan.textContent = "Mehr...";
                }
            }
        } else {
            catSidebarBtns.forEach(btn => btn.style.display = "flex");
            if (btnCategoryMore) {
                btnCategoryMore.style.display = "none";
                btnCategoryMore.classList.remove("active");
            }
        }
    }

    function selectCategory(catName) {
        currentCategory = catName;
        currentPage = 0;

        catSidebarBtns.forEach(b => {
            if (b.getAttribute("data-category") === catName) {
                b.classList.add("active");
            } else {
                b.classList.remove("active");
            }
        });

        catModalBtns.forEach(b => {
            if (b.getAttribute("data-category") === catName) {
                b.classList.add("active");
            } else {
                b.classList.remove("active");
            }
        });

        updateCategorySidebarOverflow();
        renderPage();
        playBeepSound();
    }

    catSidebarBtns.forEach(btn => {
        attachKidTouchHandler(btn, () => {
            selectCategory(btn.getAttribute("data-category"));
        });
    });

    catModalBtns.forEach(btn => {
        attachKidTouchHandler(btn, () => {
            selectCategory(btn.getAttribute("data-category"));
            if (categoryMoreOverlay) categoryMoreOverlay.classList.add("hidden");
        });
    });

    if (btnCategoryMore) {
        attachKidTouchHandler(btnCategoryMore, () => {
            playBeepSound();
            if (categoryMoreOverlay) categoryMoreOverlay.classList.remove("hidden");
        });
    }

    if (closeCategoryModalBtn) {
        attachKidTouchHandler(closeCategoryModalBtn, () => {
            if (categoryMoreOverlay) categoryMoreOverlay.classList.add("hidden");
        });
    }

    updateCategorySidebarOverflow();
    window.addEventListener("resize", updateCategorySidebarOverflow);

    // Initial page render
    renderPage();

    // Clear cart button
    if (clearCartBtn) {
        attachKidTouchHandler(clearCartBtn, () => {
            if (cart.length > 0) {
                playClearSound();
                clearCart();
            }
        });
    }

    // Pay button handler
    if (payBtn) {
        attachKidTouchHandler(payBtn, () => {
            if (cart.length === 0) return;
            playPaymentStartSound();
            socket.emit("start_payment", { cart: cart });
            showPaymentWaitingOverlay();
        });
    }

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

        const signatureContainer = document.getElementById("signatureContainer");
        const cardSignature = document.getElementById("cardSignature");
        if (data.signature_data && signatureContainer && cardSignature) {
            cardSignature.src = data.signature_data;
            signatureContainer.style.display = "block";
        } else if (signatureContainer) {
            signatureContainer.style.display = "none";
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
        const signatureContainer = document.getElementById("signatureContainer");
        if (signatureContainer) signatureContainer.style.display = "none";
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

        const signatureContainer = document.getElementById("signatureContainer");
        if (signatureContainer) signatureContainer.style.display = "none";

        paymentOverlay.classList.add("hidden");
        if (receiptActions) receiptActions.style.display = "none";
        cancelPayBtn.textContent = "Abbrechen ❌";
    }
});

/**
 * Kinder-Supermarkt Admin Panel JS
 * Visual Drag & Drop Bon-Template Builder & Live Preview Engine
 */

document.addEventListener("DOMContentLoaded", () => {
    const jsonInput = document.getElementById("receipt_layout_json_input");
    const blocksContainer = document.getElementById("receiptBlocksContainer");
    const livePreview = document.getElementById("receiptLivePreview");
    const btnAddBlock = document.getElementById("btnAddReceiptBlock");
    const btnResetLayout = document.getElementById("btnResetReceiptLayout");

    if (!jsonInput || !blocksContainer || !livePreview) return;

    // Default Receipt Layout Structure
    const DEFAULT_LAYOUT = [
        { id: "shop_name", type: "shop_name", name: "Shop-Name & Logo", enabled: true, align: "center", size: "large" },
        { id: "header_text", type: "text", name: "Kopftext / Begrüßung", enabled: true, align: "center", content: "Vielen Dank für deinen Einkauf!" },
        { id: "sep_1", type: "separator", name: "Trennlinie", enabled: true, style: "dashed" },
        { id: "meta_info", type: "meta", name: "Bon-Meta (Datum & ID)", enabled: true, show_tx_id: true, show_datetime: true },
        { id: "card_info", type: "customer", name: "Kundenname", enabled: true, show_card_name: true },
        { id: "sep_2", type: "separator", name: "Trennlinie", enabled: true, style: "dashed" },
        { id: "items_table", type: "items", name: "Artikel-Liste & Gesamtsumme", enabled: true },
        { id: "sep_3", type: "separator", name: "Trennlinie (Strich)", enabled: true, style: "solid" },
        { id: "signature", type: "signature", name: "Kunden-Unterschrift", enabled: true, title: "UNTERSCHRIFT KUNDE" },
        { id: "footer_text", type: "text", name: "Fußtext / Verabschiedung", enabled: true, align: "center", content: "Bis zum nächsten Mal!" },
        { id: "qr_code", type: "qrcode", name: "QR-Code (Bon-ID)", enabled: true, content: "tx_id" }
    ];

    let layoutBlocks = [];

    try {
        const rawJson = jsonInput.value;
        if (rawJson && rawJson.trim().length > 0) {
            layoutBlocks = JSON.parse(rawJson);
        } else {
            layoutBlocks = JSON.parse(JSON.stringify(DEFAULT_LAYOUT));
        }
    } catch (e) {
        console.warn("Failed to parse receipt_layout_json, resetting to default:", e);
        layoutBlocks = JSON.parse(JSON.stringify(DEFAULT_LAYOUT));
    }

    // Helper block labels and icons
    const BLOCK_TYPES = {
        shop_name: { label: "Shop-Name & Logo", icon: "🏷️" },
        text: { label: "Freitext / Hinweis", icon: "📝" },
        separator: { label: "Trennlinie / Abstand", icon: "➖" },
        meta: { label: "Bon-Meta (Datum & ID)", icon: "🕒" },
        customer: { label: "Kundenname", icon: "💳" },
        items: { label: "Artikel-Tabelle & Summe", icon: "🛒" },
        signature: { label: "Kunden-Unterschrift", icon: "🖋️" },
        qrcode: { label: "QR-Code / Barcode", icon: "📱" }
    };

    let draggedIndex = null;

    function saveAndRender() {
        jsonInput.value = JSON.stringify(layoutBlocks);
        renderBlocksList();
        renderLivePreview();
    }

    function renderBlocksList() {
        blocksContainer.innerHTML = "";

        layoutBlocks.forEach((block, index) => {
            const meta = BLOCK_TYPES[block.type] || { label: block.type, icon: "📦" };
            const card = document.createElement("div");
            card.className = "builder-block-card";
            card.draggable = true;
            card.dataset.index = index;

            if (!block.enabled) {
                card.style.opacity = "0.5";
            }

            card.innerHTML = `
                <div class="builder-block-header">
                    <span class="drag-handle" title="Ziehen zum Sortieren">⠿</span>
                    <div class="block-title-group">
                        <span>${meta.icon}</span>
                        <span>${block.name || meta.label}</span>
                    </div>
                    <div class="block-actions">
                        <button type="button" class="btn-toggle" title="${block.enabled ? 'Deaktivieren' : 'Aktivieren'}">
                            ${block.enabled ? '👁️' : '🙈'}
                        </button>
                        <button type="button" class="btn-up" ${index === 0 ? 'disabled' : ''} title="Nach oben">⬆️</button>
                        <button type="button" class="btn-down" ${index === layoutBlocks.length - 1 ? 'disabled' : ''} title="Nach unten">⬇️</button>
                        <button type="button" class="btn-opt" title="Optionen">⚙️</button>
                        ${block.type !== 'items' ? '<button type="button" class="btn-del" title="Entfernen">🗑️</button>' : ''}
                    </div>
                </div>
                <div class="block-options-panel" id="options_panel_${index}" style="display: none;">
                    ${renderBlockOptionsHTML(block, index)}
                </div>
            `;

            // HTML5 Drag & Drop Listeners
            card.addEventListener("dragstart", (e) => {
                draggedIndex = index;
                card.classList.add("dragging");
                e.dataTransfer.effectAllowed = "move";
            });

            card.addEventListener("dragend", () => {
                card.classList.remove("dragging");
                draggedIndex = null;
            });

            card.addEventListener("dragover", (e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = "move";
            });

            card.addEventListener("drop", (e) => {
                e.preventDefault();
                if (draggedIndex !== null && draggedIndex !== index) {
                    const movedItem = layoutBlocks.splice(draggedIndex, 1)[0];
                    layoutBlocks.splice(index, 0, movedItem);
                    saveAndRender();
                }
            });

            // Action Button Event Listeners
            card.querySelector(".btn-toggle").addEventListener("click", () => {
                block.enabled = !block.enabled;
                saveAndRender();
            });

            card.querySelector(".btn-up").addEventListener("click", () => {
                if (index > 0) {
                    const tmp = layoutBlocks[index];
                    layoutBlocks[index] = layoutBlocks[index - 1];
                    layoutBlocks[index - 1] = tmp;
                    saveAndRender();
                }
            });

            card.querySelector(".btn-down").addEventListener("click", () => {
                if (index < layoutBlocks.length - 1) {
                    const tmp = layoutBlocks[index];
                    layoutBlocks[index] = layoutBlocks[index + 1];
                    layoutBlocks[index + 1] = tmp;
                    saveAndRender();
                }
            });

            card.querySelector(".btn-opt").addEventListener("click", () => {
                const optPanel = card.querySelector(`#options_panel_${index}`);
                optPanel.style.display = optPanel.style.display === "none" ? "flex" : "none";
            });

            const delBtn = card.querySelector(".btn-del");
            if (delBtn) {
                delBtn.addEventListener("click", () => {
                    layoutBlocks.splice(index, 1);
                    saveAndRender();
                });
            }

            // Options Input Event Listeners
            bindOptionsInputs(card, block);

            blocksContainer.appendChild(card);
        });
    }

    function renderBlockOptionsHTML(block, index) {
        if (block.type === "text") {
            return `
                <label>Text-Inhalt:</label>
                <input type="text" class="opt-content" value="${block.content || ''}">
                <label>Ausrichtung:</label>
                <select class="opt-align">
                    <option value="left" ${block.align === 'left' ? 'selected' : ''}>Links</option>
                    <option value="center" ${block.align === 'center' || !block.align ? 'selected' : ''}>Zentriert</option>
                    <option value="right" ${block.align === 'right' ? 'selected' : ''}>Rechts</option>
                </select>
            `;
        }
        if (block.type === "separator") {
            return `
                <label>Stil:</label>
                <select class="opt-style">
                    <option value="dashed" ${block.style === 'dashed' ? 'selected' : ''}>Gestrichelt (---)</option>
                    <option value="solid" ${block.style === 'solid' ? 'selected' : ''}>Durchgezogen (───)</option>
                    <option value="blank" ${block.style === 'blank' ? 'selected' : ''}>Leerzeile / Abstand</option>
                </select>
            `;
        }
        if (block.type === "signature") {
            return `
                <label>Titel:</label>
                <input type="text" class="opt-title" value="${block.title || 'UNTERSCHRIFT KUNDE'}">
            `;
        }
        return `<em>Keine weiteren Einstellungen für diesen Baustein.</em>`;
    }

    function bindOptionsInputs(card, block) {
        const contentInput = card.querySelector(".opt-content");
        if (contentInput) {
            contentInput.addEventListener("input", (e) => {
                block.content = e.target.value;
                jsonInput.value = JSON.stringify(layoutBlocks);
                renderLivePreview();
            });
        }
        const alignSelect = card.querySelector(".opt-align");
        if (alignSelect) {
            alignSelect.addEventListener("change", (e) => {
                block.align = e.target.value;
                jsonInput.value = JSON.stringify(layoutBlocks);
                renderLivePreview();
            });
        }
        const styleSelect = card.querySelector(".opt-style");
        if (styleSelect) {
            styleSelect.addEventListener("change", (e) => {
                block.style = e.target.value;
                jsonInput.value = JSON.stringify(layoutBlocks);
                renderLivePreview();
            });
        }
        const titleInput = card.querySelector(".opt-title");
        if (titleInput) {
            titleInput.addEventListener("input", (e) => {
                block.title = e.target.value;
                jsonInput.value = JSON.stringify(layoutBlocks);
                renderLivePreview();
            });
        }
    }

    // Render Real-time Receipt Live Preview
    function renderLivePreview() {
        livePreview.innerHTML = "";

        const shopNameSetting = document.getElementById("shop_name") ? document.getElementById("shop_name").value : "Kinder-Supermarkt";

        layoutBlocks.forEach(block => {
            if (!block.enabled) return;

            const div = document.createElement("div");

            if (block.type === "shop_name") {
                div.className = "preview-header-title";
                div.style.textAlign = block.align || "center";
                div.textContent = `🛒 ${shopNameSetting} 🛒`;
            } else if (block.type === "text") {
                div.className = "preview-text";
                div.style.textAlign = block.align || "center";
                div.textContent = block.content || "";
            } else if (block.type === "separator") {
                if (block.style === "solid") {
                    div.className = "preview-sep-solid";
                } else if (block.style === "blank") {
                    div.style.height = "1rem";
                } else {
                    div.className = "preview-sep";
                }
            } else if (block.type === "meta") {
                div.className = "preview-text";
                div.style.textAlign = "center";
                div.style.fontSize = "0.85rem";
                div.innerHTML = `Bon #1042 &bull; 20.07.2026 19:45`;
            } else if (block.type === "customer") {
                div.className = "preview-text";
                div.style.textAlign = "center";
                div.innerHTML = `<strong>Kunde: Lena 👧</strong> 💳`;
            } else if (block.type === "items") {
                div.innerHTML = `
                    <table class="preview-table">
                        <tr><td>2x Apfel</td><td style="text-align:right">1,00 €</td></tr>
                        <tr><td>1x Schokolade</td><td style="text-align:right">0,90 €</td></tr>
                    </table>
                    <div class="preview-sep-solid"></div>
                    <div style="display:flex; justify-content:space-between; font-weight:bold; font-size:1.1rem; margin-top:0.4rem;">
                        <span>GESAMTSUMME:</span>
                        <span>1,90 €</span>
                    </div>
                `;
            } else if (block.type === "signature") {
                div.style.textAlign = "center";
                div.style.margin = "0.8rem 0";
                div.innerHTML = `
                    <div style="font-size:0.8rem; font-weight:bold;">${block.title || 'UNTERSCHRIFT KUNDE'}</div>
                    <div style="border-bottom: 2px italic #333; height: 35px; margin: 0.3rem auto; width: 80%; display: flex; align-items: flex-end; justify-content: center; font-style: italic; color: #1e293b;">
                        ✍️ Lena Signature
                    </div>
                `;
            } else if (block.type === "qrcode") {
                const baseUrlEl = document.getElementById("base_url");
                const currentBase = (baseUrlEl && baseUrlEl.value.trim()) ? baseUrlEl.value.trim() : window.location.origin;
                const sampleTarget = `${currentBase.replace(/\/$/, '')}/receipt/1042`;
                const encoded = encodeURIComponent(sampleTarget);
                
                div.className = "preview-qr";
                div.innerHTML = `
                    <img src="https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=${encoded}" alt="QR" style="width: 90px; height: 90px; border: 1px solid #cbd5e1; padding: 2px; background: white; border-radius: 6px; margin: 0 auto; display: block;">
                    <div style="font-size: 0.75rem; color: #64748b; margin-top: 4px;">Scannen für digitalen Bon 📱</div>
                `;
            }

            livePreview.appendChild(div);
        });
    }

    window.addReceiptBlockType = function(type) {
        if (type === "text") {
            layoutBlocks.push({ id: "text_" + Date.now(), type: "text", name: "Freitext", enabled: true, align: "center", content: "Vielen Dank!" });
        } else if (type === "separator") {
            layoutBlocks.push({ id: "sep_" + Date.now(), type: "separator", name: "Trennlinie", enabled: true, style: "dashed" });
        } else if (type === "qrcode") {
            layoutBlocks.push({ id: "qr_" + Date.now(), type: "qrcode", name: "QR-Code", enabled: true, content: "tx_id" });
        } else if (type === "signature") {
            layoutBlocks.push({ id: "sig_" + Date.now(), type: "signature", name: "Unterschrift", enabled: true, title: "UNTERSCHRIFT KUNDE" });
        }
        const modal = document.getElementById("addBlockModal");
        if (modal) modal.classList.add("hidden");
        saveAndRender();
    };

    if (btnAddBlock) {
        btnAddBlock.addEventListener("click", () => {
            const modal = document.getElementById("addBlockModal");
            if (modal) modal.classList.remove("hidden");
        });
    }

    const closeAddBlockModalBtn = document.getElementById("closeAddBlockModalBtn");
    if (closeAddBlockModalBtn) {
        closeAddBlockModalBtn.addEventListener("click", () => {
            const modal = document.getElementById("addBlockModal");
            if (modal) modal.classList.add("hidden");
        });
    }


    if (btnResetLayout) {
        btnResetLayout.addEventListener("click", () => {
            if (confirm("Möchtest du das Kassenbon-Layout wirklich auf den Standard zurücksetzen?")) {
                layoutBlocks = JSON.parse(JSON.stringify(DEFAULT_LAYOUT));
                saveAndRender();
            }
        });
    }

    // Initial Render
    renderBlocksList();
    renderLivePreview();
});

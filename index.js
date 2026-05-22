const AMAZON_HOSTS = ["amazon.in", "www.amazon.in", "amzn.in", "amzn.to"];
const FLIPKART_HOSTS = ["flipkart.com", "www.flipkart.com"];

const form = document.getElementById("compare-form");
const amazonInput = document.getElementById("amazon-url");
const flipkartInput = document.getElementById("flipkart-url");
const formError = document.getElementById("form-error");
const compareBtn = document.getElementById("compare-btn");
const loadingEl = document.getElementById("loading");
const resultsEl = document.getElementById("results");
const summaryEl = document.getElementById("summary");
const warningEl = document.getElementById("warning");
const amazonCard = document.getElementById("amazon-card");
const flipkartCard = document.getElementById("flipkart-card");

const API_BASE = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:5000"
    : "";

function hostMatches(url, allowedHosts) {
    try {
        const host = new URL(url.trim()).hostname.toLowerCase().replace(/^www\./, "");
        return allowedHosts.some((h) => host === h.replace(/^www\./, "") || host.endsWith("." + h.replace(/^www\./, "")));
    } catch {
        return false;
    }
}

function validateClient(amazonUrl, flipkartUrl) {
    if (!amazonUrl || !flipkartUrl) {
        return "Please paste both Amazon and Flipkart links.";
    }
    if (!hostMatches(amazonUrl, AMAZON_HOSTS)) {
        return "Amazon link must be from amazon.in or amzn.in.";
    }
    if (!hostMatches(flipkartUrl, FLIPKART_HOSTS)) {
        return "Flipkart link must be from flipkart.com.";
    }
    return null;
}

function formatPrice(value) {
    if (value == null || Number.isNaN(value)) return "—";
    return "₹" + Number(value).toLocaleString("en-IN", { maximumFractionDigits: 0 });
}

function renderProductCard(container, product, storeLabel, storeClass, isCheaper) {
    const hasPrice = product.price != null;
    const cheaperHtml = isCheaper ? '<span class="cheaper-tag">Cheaper</span>' : "";

    let priceHtml;
    if (hasPrice) {
        const mrpHtml = product.mrp && product.mrp > product.price
            ? `<span class="price-mrp">${formatPrice(product.mrp)}</span>`
            : "";
        const discountHtml = product.discount_pct
            ? `<span class="price-discount">${product.discount_pct}% off</span>`
            : "";
        priceHtml = `
            <div class="price-row">
                <span class="price-main">${formatPrice(product.price)}</span>
                ${mrpHtml}
                ${discountHtml}
            </div>`;
    } else {
        priceHtml = `<p class="price-unavailable">Price unavailable</p>`;
    }

    const errorHtml = product.error
        ? `<p class="card-error">${escapeHtml(product.error)}</p>`
        : "";

    const imageHtml = product.image
        ? `<img class="product-image" src="${escapeAttr(product.image)}" alt="" loading="lazy">`
        : "";

    container.className = `product-card card${isCheaper ? " is-cheaper" : ""}`;
    container.innerHTML = `
        <span class="store-badge ${storeClass}">${storeLabel}</span>
        ${cheaperHtml}
        ${imageHtml}
        <h2 class="product-title">${escapeHtml(product.title || "Unknown product")}</h2>
        ${priceHtml}
        ${errorHtml}
        <a class="btn-link ${storeClass}" href="${escapeAttr(product.url)}" target="_blank" rel="noopener noreferrer">
            Open on ${storeLabel}
        </a>
    `;
}

function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}

function escapeAttr(str) {
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;")
        .replace(/</g, "&lt;");
}

function showError(message) {
    formError.textContent = message;
    formError.classList.remove("hidden");
}

function hideError() {
    formError.classList.add("hidden");
    formError.textContent = "";
}

function setLoading(active) {
    loadingEl.classList.toggle("hidden", !active);
    compareBtn.disabled = active;
    if (active) resultsEl.classList.add("hidden");
}

function renderResults(data) {
    const { amazon, flipkart, comparison, warning } = data;
    const cheaper = comparison?.cheaper;

    summaryEl.className = "summary card";
    if (cheaper === "amazon") summaryEl.classList.add("cheaper-amazon");
    else if (cheaper === "flipkart") summaryEl.classList.add("cheaper-flipkart");
    else summaryEl.classList.add("cheaper-tie");

    summaryEl.innerHTML = `
        <p class="summary-message">${escapeHtml(comparison?.message || "Comparison complete")}</p>
        ${comparison?.savings > 0 ? `<p class="summary-sub">Difference: ${formatPrice(comparison.savings)}</p>` : ""}
    `;

    if (warning) {
        warningEl.textContent = warning;
        warningEl.classList.remove("hidden");
    } else {
        warningEl.classList.add("hidden");
    }

    renderProductCard(amazonCard, amazon, "Amazon", "amazon", cheaper === "amazon");
    renderProductCard(flipkartCard, flipkart, "Flipkart", "flipkart", cheaper === "flipkart");

    resultsEl.classList.remove("hidden");
}

form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideError();

    const amazonUrl = amazonInput.value.trim();
    const flipkartUrl = flipkartInput.value.trim();
    const clientError = validateClient(amazonUrl, flipkartUrl);
    if (clientError) {
        showError(clientError);
        return;
    }

    setLoading(true);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 12000);

    const compareUrl = `${API_BASE}/api/compare`;

    try {
        const res = await fetch(compareUrl, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ amazon_url: amazonUrl, flipkart_url: flipkartUrl }),
            signal: controller.signal,
        });

        const data = await res.json().catch(() => ({}));

        if (!res.ok) {
            const msg = data.error || `Request failed (${res.status})`;
            showError(msg);
            if (data.amazon && data.flipkart) {
                renderResults({
                    amazon: data.amazon,
                    flipkart: data.flipkart,
                    comparison: { message: msg, cheaper: null, savings: 0 },
                    warning: null,
                });
            }
            return;
        }

        renderResults(data);
    } catch (err) {
        if (err.name === "AbortError") {
            showError("Request timed out. Try again — Amazon pages can be slow.");
        } else {
            showError("Could not reach the server. Run the API locally or deploy to Vercel.");
        }
    } finally {
        clearTimeout(timeoutId);
        setLoading(false);
    }
});

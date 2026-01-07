function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }
    return cookieValue;
}



function applyTheme(theme) {
    const themeIcon = document.getElementById("themeIcon");
    const cartIcon = document.getElementById("cartIcon");

    if (theme === "dark") {
        document.body.setAttribute("data-theme", "dark");
        if (themeIcon) themeIcon.textContent = "☀️";
        if (cartIcon) cartIcon.src = CART_DARK;
    } else {
        document.body.removeAttribute("data-theme");
        if (themeIcon) themeIcon.textContent = "🌙";
        if (cartIcon) cartIcon.src = CART_LIGHT;
    }
}

function toggleTheme() {
    const current = document.body.getAttribute("data-theme") === "dark"
        ? "dark"
        : "light";
    const next = current === "dark" ? "light" : "dark";
    localStorage.setItem("theme", next);
    applyTheme(next);
}

document.addEventListener("DOMContentLoaded", () => {
    applyTheme(localStorage.getItem("theme") || "light");
});

document.addEventListener("DOMContentLoaded", () => {
    const savedTheme = localStorage.getItem("theme") || "light";
    applyTheme(savedTheme);
});

document.addEventListener("DOMContentLoaded", () => {
    const savedTheme = localStorage.getItem("theme") || "light";
    applyTheme(savedTheme);
});

function openLogoutModal() {
    document.getElementById("logoutOverlay").classList.add("show");
}

function confirmLogout() {
    window.location.href = "{% url 'logout' %}";
}




// Cart Quantity Management



function showQtyBox(btn, qty) {
    const wrapper = btn.closest(".qty-wrapper");
    btn.classList.add("hidden");

    const box = wrapper.querySelector(".qty-box");
    box.classList.remove("hidden");
    box.querySelector(".qty-count").textContent = qty;
}

// function addToCart(itemId, btn) {
//     fetch(`/add_to_cart/${itemId}/`, {
//         method: "POST",
//         headers: {
//             "X-CSRFToken": csrfToken
//         }
//     }).then(() => {
//         const wrapper = btn.closest(".qty-wrapper");
//         btn.classList.add("hidden");

//         const box = wrapper.querySelector(".qty-box");
//         box.classList.remove("hidden");

//         box.querySelector(".qty-count").textContent = "1";
//     });
// }

function addToCart(itemId, btn) {
    fetch(`/add_to_cart/${itemId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken
        }
    }).then(() => {
        const wrapper = btn.closest(".qty-wrapper");
        btn.classList.add("hidden");

        const box = wrapper.querySelector(".qty-box");
        box.classList.remove("hidden");
        box.querySelector(".qty-count").textContent = "1";

        updateCartCount(1); // 🔥 real-time update
    });
}


// function increaseQty(itemId, btn) {
//     fetch(`/add_to_cart/${itemId}/`, {
//         method: "POST",
//         headers: {
//             "X-CSRFToken": csrfToken
//         }
//     }).then(() => {
//         const countSpan = btn.parentElement.querySelector(".qty-count");
//         countSpan.textContent = parseInt(countSpan.textContent) + 1;
//     });
// }

function increaseQty(itemId, btn) {
    fetch(`/add_to_cart/${itemId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken
        }
    }).then(() => {
        const countSpan = btn.parentElement.querySelector(".qty-count");
        countSpan.textContent = parseInt(countSpan.textContent) + 1;

        updateCartCount(1); // 🔥 real-time update
    });
}


// function decreaseQty(itemId, btn) {
//     fetch(`/decrease_cart/${itemId}/`, {
//         method: "POST",
//         headers: {
//             "X-CSRFToken": csrfToken
//         }
//     }).then(() => {
//         const wrapper = btn.closest(".qty-wrapper");
//         const countSpan = wrapper.querySelector(".qty-count");
//         let qty = parseInt(countSpan.textContent) - 1;

//         if (qty <= 0) {
//             wrapper.querySelector(".qty-box").classList.add("hidden");
//             wrapper.querySelector(".add-btn").classList.remove("hidden");
//         } else {
//             countSpan.textContent = qty;
//         }
//     });
// }


function decreaseQty(itemId, btn) {
    fetch(`/decrease_cart/${itemId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrfToken
        }
    }).then(() => {
        const wrapper = btn.closest(".qty-wrapper");
        const countSpan = wrapper.querySelector(".qty-count");
        let qty = parseInt(countSpan.textContent) - 1;

        if (qty <= 0) {
            wrapper.querySelector(".qty-box").classList.add("hidden");
            wrapper.querySelector(".add-btn").classList.remove("hidden");
        } else {
            countSpan.textContent = qty;
        }

        updateCartCount(-1); // 🔥 real-time update
    });
}


function updateCartCount(delta) {
    const cartCountEl = document.getElementById("cartCount");
    if (!cartCountEl) return;

    let count = parseInt(cartCountEl.textContent || "0");
    count += delta;

    if (count <= 0) {
        cartCountEl.textContent = "0";
        cartCountEl.classList.add("hidden");
    } else {
        cartCountEl.textContent = count;
        cartCountEl.classList.remove("hidden");
    }
}

function setCartCount(count) {
    const el = document.getElementById("cartCount");
    if (!el) return;

    if (count > 0) {
        el.textContent = count;
        el.classList.remove("hidden");
    } else {
        el.textContent = "0";
        el.classList.add("hidden");
    }
}

function applyCoupon() {
    const code = document.getElementById("couponCode").value;
    fetch("/apply-coupon/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: `code=${code}`
    }).then(() => location.reload());
}

function removeCoupon() {
    fetch("/remove-coupon/", {
        method: "POST",
        headers: { "X-CSRFToken": getCookie("csrftoken") }
    }).then(() => location.reload());
}

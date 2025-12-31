<script src="https://checkout.razorpay.com/v1/checkout.js"></script>

var options = {
    key: "{{ razorpay_key_id }}",
    amount: "{{ grand_total|floatformat:2 }}00",
    currency: "INR",
    name: "Crave Cart",
    description: "Order Payment",
    order_id: "{{ order_id }}",
    handler: function (response) {

        fetch("{% url 'payment_success' %}", {
            method: "POST",
            headers: {
                "X-CSRFToken": "{{ csrf_token }}",
                "Content-Type": "application/json"
            },
            body: JSON.stringify(response)
        }).then(() => {
            window.location.href = "{% url 'order_history' %}";
        });
    }
};

var rzp = new Razorpay(options);
document.getElementById("rzp-button").onclick = function(e){
    rzp.open();
    e.preventDefault();
}

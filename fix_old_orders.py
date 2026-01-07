from decimal import Decimal
from delivery.models import Order

GST_RATE = Decimal("0.05")
DELIVERY_FEE = Decimal("40.00")

fixed = 0

for order in Order.objects.all():
    if order.subtotal == 0 and order.items.exists():
        subtotal = Decimal("0.00")

        for item in order.items.all():
            subtotal += Decimal(item.price) * item.quantity

        gst_amount = (subtotal * GST_RATE).quantize(Decimal("0.01"))
        total = subtotal + gst_amount + DELIVERY_FEE

        order.subtotal = float(subtotal)
        order.gst_amount = float(gst_amount)
        order.delivery_fee = float(DELIVERY_FEE)
        order.total_amount = float(total)

        order.save()
        fixed += 1

print(f"✅ Fixed {fixed} old orders")

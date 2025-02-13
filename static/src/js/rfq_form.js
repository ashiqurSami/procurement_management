document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("input[name^='order_line_unit_price_'], input[name^='order_line_delivery_charge_']").forEach(input => {
        input.addEventListener("input", function () {
            let row = this.closest("tr");

            let quantity = parseFloat(row.querySelector("td:nth-child(4)").textContent) || 0;
            let unitPrice = parseFloat(row.querySelector("input[name^='order_line_unit_price_']").value) || 0;
            let deliveryCharge = parseFloat(row.querySelector("input[name^='order_line_delivery_charge_']").value) || 0;
            let subtotal = (quantity * unitPrice) + deliveryCharge;

            row.querySelector("td:last-child").textContent = subtotal.toFixed(2);
        });
    });
});

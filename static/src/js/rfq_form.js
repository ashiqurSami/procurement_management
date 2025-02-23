document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM fully loaded and parsed');

    // Function to calculate subtotal for a row
    function calculateSubtotal(row) {
        const quantity = parseFloat(row.querySelector('td:nth-child(4)').textContent.trim()) || 0;
        const unitPrice = parseFloat(row.querySelector('input[name^="order_line_unit_price_"]').value) || 0;
        const deliveryCharge = parseFloat(row.querySelector('input[name^="order_line_delivery_charge_"]').value) || 0;

        const subtotal = (quantity * unitPrice) + deliveryCharge;
        row.querySelector('td:nth-child(7)').textContent = subtotal.toFixed(2);
    }

    // Function to calculate the total sum of all subtotals
    function calculateTotalSum() {
        const rows = document.querySelectorAll('table tbody tr');
        let totalSum = 0;

        rows.forEach(row => {
            const subtotal = parseFloat(row.querySelector('td:nth-child(7)').textContent.trim()) || 0;
            totalSum += subtotal;
        });

        // Display the total sum in the designated element
        const totalSumElement = document.getElementById('total-sum');
        if (totalSumElement) {
            totalSumElement.textContent = totalSum.toFixed(2);
        }
    }

    // Function to handle input changes
    function handleInputChange(event) {
        const input = event.target;
        const row = input.closest('tr');
        if (row) {
            calculateSubtotal(row);
            calculateTotalSum(); // Recalculate total sum after updating subtotal
        }
    }

    // Attach event listeners to all unit_price and delivery_charge inputs
    const unitPriceInputs = document.querySelectorAll('input[name^="order_line_unit_price_"]');
    const deliveryChargeInputs = document.querySelectorAll('input[name^="order_line_delivery_charge_"]');

    unitPriceInputs.forEach(input => {
        input.addEventListener('input', handleInputChange); // Use 'input' event for real-time updates
    });

    deliveryChargeInputs.forEach(input => {
        input.addEventListener('input', handleInputChange); // Use 'input' event for real-time updates
    });

    // Calculate initial subtotals and total sum on page load
    const rows = document.querySelectorAll('table tbody tr');
    rows.forEach(row => {
        calculateSubtotal(row);
    });
    calculateTotalSum();
});
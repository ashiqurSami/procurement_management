document.addEventListener('DOMContentLoaded', function() {
    // Function to calculate subtotal for a row
    function calculateSubtotal(row) {
        const quantity = parseFloat(row.querySelector('td:nth-child(4)').textContent.trim());
        const unitPrice = parseFloat(row.querySelector('input[name^="order_line_unit_price"]').value) || 0;
        const deliveryCharge = parseFloat(row.querySelector('input[name^="order_line_delivery_charge"]').value) || 0;

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
    const unitPriceInputs = document.querySelectorAll('input[name^="order_line_unit_price"]');
    const deliveryChargeInputs = document.querySelectorAll('input[name^="order_line_delivery_charge"]');

    unitPriceInputs.forEach(input => {
        input.addEventListener('change', handleInputChange); // Use 'change' event
    });

    deliveryChargeInputs.forEach(input => {
        input.addEventListener('change', handleInputChange); // Use 'change' event
    });

    // Calculate initial subtotals and total sum on page load
    const rows = document.querySelectorAll('table tbody tr');
    rows.forEach(row => {
        calculateSubtotal(row);
    });
    calculateTotalSum();
});
// static/src/js/form_navigation.js
// JavaScript for handling form step navigation
document.getElementById("next-1").onclick = function() {
    document.getElementById("step-1").style.display = "none";
    document.getElementById("step-2").style.display = "block";
};

document.getElementById("prev-2").onclick = function() {
    document.getElementById("step-2").style.display = "none";
    document.getElementById("step-1").style.display = "block";
};

document.getElementById("next-2").onclick = function() {
    document.getElementById("step-2").style.display = "none";
    document.getElementById("step-3").style.display = "block";
};

document.getElementById("prev-3").onclick = function() {
    document.getElementById("step-3").style.display = "none";
    document.getElementById("step-2").style.display = "block";
};

document.getElementById("next-3").onclick = function() {
    document.getElementById("step-3").style.display = "none";
    document.getElementById("step-4").style.display = "block";
};

document.getElementById("prev-4").onclick = function() {
    document.getElementById("step-4").style.display = "none";
    document.getElementById("step-3").style.display = "block";
};

document.getElementById("next-4").onclick = function() {
    document.getElementById("step-4").style.display = "none";
    document.getElementById("step-5").style.display = "block";
};

document.getElementById("prev-5").onclick = function() {
    document.getElementById("step-5").style.display = "none";
    document.getElementById("step-4").style.display = "block";
};

document.addEventListener("DOMContentLoaded", function () {
    const maxClients = 5;
    let clientCount = 0;
    const clientList = document.getElementById("client-list");
    const addClientBtn = document.getElementById("add-client");

    function addClient() {
        if (clientCount >= maxClients) return;

        clientCount++;
        const clientDiv = document.createElement("div");
        clientDiv.classList.add("border", "rounded-3", "p-3", "mb-3", "position-relative", "shadow-sm", "bg-light");
        clientDiv.setAttribute("id", `client_${clientCount}`);

        clientDiv.innerHTML = `
            <h5 class="text-primary fw-semibold">Client ${clientCount}</h5>
            <button type="button" class="btn-close position-absolute top-0 end-0 m-2 remove-client" data-id="client_${clientCount}"></button>
            <div class="row g-3">
                <div class="col-md-6">
                    <label class="form-label fw-semibold" for="client_${clientCount}_name">Client Name</label>
                    <input type="text" class="form-control shadow-sm" id="client_${clientCount}_name" name="client_${clientCount}_name" placeholder="Enter client name"/>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-semibold" for="client_${clientCount}_address">Client Address</label>
                    <input type="text" class="form-control shadow-sm" id="client_${clientCount}_address" name="client_${clientCount}_address" placeholder="Enter client address"/>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-semibold" for="client_${clientCount}_contact_email">Client Contact Email</label>
                    <input type="email" class="form-control shadow-sm" id="client_${clientCount}_contact_email" name="client_${clientCount}_contact_email" placeholder="Enter contact email"/>
                </div>
                <div class="col-md-6">
                    <label class="form-label fw-semibold" for="client_${clientCount}_contact_phone">Client Contact Phone</label>
                    <input type="tel" class="form-control shadow-sm" id="client_${clientCount}_contact_phone" name="client_${clientCount}_contact_phone" placeholder="Enter contact phone"/>
                </div>
            </div>
        `;

        clientList.appendChild(clientDiv);
        updateRemoveButtons();
    }

    function updateRemoveButtons() {
        document.querySelectorAll(".remove-client").forEach((btn) => {
            btn.removeEventListener("click", removeClient); // Avoid duplicate event listeners
            btn.addEventListener("click", removeClient);
        });
    }

    function removeClient(event) {
        const clientId = event.target.getAttribute("data-id");
        const clientElement = document.getElementById(clientId);
        if (clientElement) {
            clientElement.remove();
            clientCount--;
        }
    }

    addClientBtn.addEventListener("click", addClient);
    addClient(); // Add first client by default
});


document.getElementById('declaration_checkbox').addEventListener('change', function () {
        document.getElementById('submit-form').disabled = !this.checked;
    });

document.addEventListener('DOMContentLoaded', function() {
                        document.querySelectorAll('table tbody tr').forEach(function(row) {
                            // Extract quantity from the fourth cell (index 3)
                            const quantityCell = row.cells[3];
                            const quantity = parseInt(quantityCell.textContent.trim(), 10) || 0;

                            // Get unit price and delivery charge inputs
                            const inputs = row.querySelectorAll('input[type="number"]');
                            if (inputs.length < 2) return;
                            const unitPriceInput = inputs[0];
                            const deliveryChargeInput = inputs[1];

                            // Subtotal cell is the seventh column (index 6)
                            const subtotalCell = row.cells[6];

                            // Function to calculate and update subtotal
                            function updateSubtotal() {
                                const unitPrice = parseFloat(unitPriceInput.value) || 0;
                                const deliveryCharge = parseFloat(deliveryChargeInput.value) || 0;
                                const subtotal = (quantity * unitPrice) + deliveryCharge;
                                subtotalCell.textContent = subtotal.toFixed(2);
                            }

                            // Attach event listeners to inputs
                            unitPriceInput.addEventListener('input', updateSubtotal);
                            deliveryChargeInput.addEventListener('input', updateSubtotal);

                            // Calculate initial subtotal on page load
                            updateSubtotal();
                        });
                    });
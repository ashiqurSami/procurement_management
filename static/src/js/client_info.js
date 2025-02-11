<script>
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
            <button type="button" class="btn-close position-absolute top-0 end-0 m-2 remove-client" data-id="${clientCount}"></button>
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
            btn.addEventListener("click", function () {
                const clientId = this.getAttribute("data-id");
                document.getElementById(`client_${clientId}`).remove();
                clientCount--;
            });
        });
    }

    addClientBtn.addEventListener("click", addClient);
    addClient(); // Add first client by default
});
</script>
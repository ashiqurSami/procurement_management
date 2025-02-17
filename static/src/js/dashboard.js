/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class SupplierDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            suppliers: [],
            selectedSupplier: null,
            dateRange: "this_week",
            metrics: { totalRFQs: 0, totalAmount: 0, productBreakdown: [] },
        });

        onWillStart(async () => {
            // First, get suppliers with approved RFQs
            const supplierIds = await this._getSuppliersWithRFQs();
            
            // Then, fetch supplier details
            if (supplierIds.length > 0) {
                this.state.suppliers = await this.orm.searchRead("res.partner", [["id", "in", supplierIds]], ["id", "name"]);
                this.state.selectedSupplier = this.state.suppliers.length > 0 ? this.state.suppliers[0].id : null;
            }

            // Fetch metrics after setting the supplier
            this.fetchMetrics();
        });
    }

    async _getSuppliersWithRFQs() {
        const approvedRFQs = await this.orm.searchRead("purchase.order", [["state", "=", "purchase"]], ["partner_id"]);
        return [...new Set(approvedRFQs.map(po => po.partner_id[0]))];  // Extract unique supplier IDs
    }

    async fetchMetrics() {
        if (!this.state.selectedSupplier) return;
        const metrics = await this.orm.call("purchase.order", "get_supplier_metrics", [
            this.state.selectedSupplier,
            this.state.dateRange
        ]);
        this.state.metrics = metrics;
    }
}

// Register the component in Odoo's action registry
SupplierDashboard.template = "procurement_management.SupplierDashboard";
registry.category("actions").add("procurement_management.supplier_dashboard", SupplierDashboard);

/** @odoo-module **/
import { registry } from "@web/core/registry";
import { loadJS } from "@web/core/assets";
const { Component, useState, onWillStart, onMounted, useRef } = owl;
import { useService } from "@web/core/utils/hooks";

export class SupplierDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            suppliers: [],
            selectedSupplier: null,
            dateRange: "this_week",
            metrics: { totalRFQs: 0, totalAmount: 0, productBreakdown: [] },
        });

        this.chartRefBar = useRef("chartBar");
        this.chartRefPie = useRef("chartPie");
        this.chartInstanceBar = null;
        this.chartInstancePie = null;

        onWillStart(async () => {
            await loadJS("https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js");
            await this.loadSuppliers();
        });

        onMounted(this.fetchMetrics);
    }

    async loadSuppliers() {
        const suppliers = await this.orm.searchRead("res.partner", [["supplier_rank", ">", 0]], ["id", "name"]);
        this.state.suppliers = suppliers;
        if (suppliers.length > 0) {
            this.state.selectedSupplier = suppliers[0].id;
            this.fetchMetrics();
        }
    }

    async fetchMetrics() {
        if (!this.state.selectedSupplier) return;

        const metrics = await this.orm.call("purchase.order", "get_supplier_metrics", [
            this.state.selectedSupplier,
            this.state.dateRange
        ]);
        this.state.metrics = metrics;
        this.renderCharts();
    }

    clearCanvas(canvasRef) {
        const ctx = canvasRef.el.getContext("2d");
        ctx.save();
        ctx.clearRect(0, 0, canvasRef.el.width, canvasRef.el.height);
        ctx.restore();
    }

    renderCharts() {
        this.clearCanvas(this.chartRefBar);
        this.clearCanvas(this.chartRefPie);

        if (this.chartInstanceBar) {
            this.chartInstanceBar.destroy();
            this.chartInstanceBar = null;
        }
        if (this.chartInstancePie) {
            this.chartInstancePie.destroy();
            this.chartInstancePie = null;
        }

        const ctxBar = this.chartRefBar.el.getContext("2d");
        const ctxPie = this.chartRefPie.el.getContext("2d");

        const labels = this.state.metrics.productBreakdown.map(item => item.name);
        const quantities = this.state.metrics.productBreakdown.map(item => item.quantity);

        // Bar Chart
        this.chartInstanceBar = new Chart(ctxBar, {
            type: "bar",
            data: {
                labels: labels,
                datasets: [{
                    label: "Product Quantities",
                    data: quantities,
                    backgroundColor: "rgba(54, 162, 235, 0.6)",
                    borderColor: "rgba(54, 162, 235, 1)",
                    borderWidth: 1,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                    },
                },
            },
        });

        // Pie Chart
        this.chartInstancePie = new Chart(ctxPie, {
            type: "pie",
            data: {
                labels: labels,
                datasets: [{
                    label: "Product Distribution",
                    data: quantities,
                    backgroundColor: ["#ff6384", "#36a2eb", "#ffce56", "#4bc0c0", "#9966ff"],
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
            },
        });
    }

    onSupplierChange(ev) {
        this.state.selectedSupplier = parseInt(ev.target.value);
        this.fetchMetrics();
    }

    onDateRangeChange(ev) {
        this.state.dateRange = ev.target.value;
        this.fetchMetrics();
    }

    static template = "procurement_management.SupplierDashboard";
}

registry.category("actions").add("procurement_management.supplier_dashboard", SupplierDashboard);
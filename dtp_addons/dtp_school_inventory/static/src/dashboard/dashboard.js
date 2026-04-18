/** @odoo-module **/
/**
 * DTP School Inventory Dashboard – Main OWL Component
 *
 * Architecture:
 *   DtpInventoryDashboard (root)
 *     ├── FilterPanel          – PowerBI-style context filters
 *     ├── KpiCard (×6)         – Top summary metrics
 *     ├── DonutChart           – Pickings by state
 *     ├── HorizontalBarChart   – Top 8 products
 *     ├── SchoolsTable         – Per-school breakdown
 *     └── TrendLineChart       – Monthly done pickings (6 months)
 *
 * Each visual is an independent component with its own props and rendering logic.
 * Adding a new visual = create a new component, import it here, drop it in the template.
 */

import { Component, useState, onWillStart, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";

// ─── Sub-components ──────────────────────────────────────────────────────────
import { FilterPanel } from "./filter_panel/filter_panel";
import { KpiCard } from "./kpi_card/kpi_card";
import { DonutChart } from "./donut_chart/donut_chart";
import { HorizontalBarChart } from "./horizontal_bar_chart/horizontal_bar_chart";
import { SchoolsTable } from "./schools_table/schools_table";
import { TrendLineChart } from "./trend_line_chart/trend_line_chart";


export class DtpInventoryDashboard extends Component {
    static template = "dtp_school_inventory.Dashboard";
    static components = {
        FilterPanel,
        KpiCard,
        DonutChart,
        HorizontalBarChart,
        SchoolsTable,
        TrendLineChart,
    };
    static props = { ...standardActionServiceProps };

    setup() {
        this.actionService = useService("action");

        // Reactive state: filters + loaded data
        this.state = useState({
            loading: true,
            filters: {
                region: null,
                school_type: null,
                school_id: null,
            },
            // Dashboard data sections
            kpis: {},
            pickings_by_state: [],
            top_products: [],
            schools_overview: [],
            pickings_trend: [],
            filter_options: {
                regions: [],
                school_types: [],
                schools: [],
            },
        });

        onWillStart(() => this._loadDashboard());
    }

    // ── Data loading ─────────────────────────────────────────────────────────

    async _loadDashboard() {
        this.state.loading = true;
        try {
            const data = await rpc("/dtp_school_inventory/dashboard/data", {
                filters: this.state.filters,
            });
            this.state.kpis = data.kpis;
            this.state.pickings_by_state = data.pickings_by_state;
            this.state.top_products = data.top_products;
            this.state.schools_overview = data.schools_overview;
            this.state.pickings_trend = data.pickings_trend;
            this.state.filter_options = data.filter_options;
        } finally {
            this.state.loading = false;
        }
    }

    // ── Event handlers ────────────────────────────────────────────────────────

    onFilterChange(newFilters) {
        Object.assign(this.state.filters, newFilters);
        this._loadDashboard();
    }

    onResetFilters() {
        this.state.filters = { region: null, school_type: null, school_id: null };
        this._loadDashboard();
    }

    /**
     * Navigate to school form view when clicking a school row in the table.
     */
    onSchoolClick(schoolId) {
        this.actionService.doAction({
            type: "ir.actions.act_window",
            res_model: "res.partner",
            res_id: schoolId,
            views: [[false, "form"]],
            target: "current",
        });
    }

    /**
     * Get current UTC date-time string for Odoo domains.
     */
    get _now() {
        return new Date().toISOString().replace('T', ' ').split('.')[0];
    }

    /**
     * Unified KPI click handler with context-aware filtering.
     * Combines dashboard filters with KPI-specific domain.
     */
    onKpiClick(model, extraDomain = []) {
        const domain = [...extraDomain];
        const filters = this.state.filters;

        // Apply dashboard context (Region/Type/School) to the target model
        if (model === "res.partner") {
            domain.push(["is_school", "=", true]);
            if (filters.region) domain.push(["region", "=", filters.region]);
            if (filters.school_type) domain.push(["school_type", "=", filters.school_type]);
            if (filters.school_id) domain.push(["id", "=", filters.school_id]);
        } 
        else if (model === "res.partner.class") {
            if (filters.region) domain.push(["school_id.region", "=", filters.region]);
            if (filters.school_type) domain.push(["school_id.school_type", "=", filters.school_type]);
            if (filters.school_id) domain.push(["school_id", "=", filters.school_id]);
        } 
        else if (model === "stock.picking") {
            if (filters.region) domain.push(["partner_id.region", "=", filters.region]);
            if (filters.school_type) domain.push(["partner_id.school_type", "=", filters.school_type]);
            if (filters.school_id) domain.push(["partner_id", "=", filters.school_id]);
        }

        let name = "Dữ liệu chi tiết";
        if (model === "res.partner") name = "Danh sách trường học";
        if (model === "res.partner.class") name = "Danh sách lớp học";
        if (model === "stock.picking") name = "Danh sách phiếu kho";

        this.actionService.doAction({
            type: "ir.actions.act_window",
            name: name,
            res_model: model,
            view_mode: "list,form",
            views: [[false, "list"], [false, "form"]],
            domain: domain,
            target: "current",
        });
    }
}

registry.category("actions").add("dtp_school_inventory_dashboard", DtpInventoryDashboard);

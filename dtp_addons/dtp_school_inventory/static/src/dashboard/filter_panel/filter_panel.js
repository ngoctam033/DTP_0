/** @odoo-module **/
/**
 * FilterPanel – PowerBI-style context slicer panel.
 *
 * Props:
 *   options   : { regions, school_types, schools }   – available filter values
 *   filters   : { region, school_type, school_id }   – current active filters
 *   onFilterChange(newFilters)                        – callback to parent
 *
 * Each slicer is independent; selecting one re-fetches the whole dashboard.
 */

import { Component } from "@odoo/owl";

export class FilterPanel extends Component {
    static template = "dtp_school_inventory.FilterPanel";
    static props = {
        options: Object,
        filters: Object,
        onFilterChange: Function,
    };

    // ── Slicer handlers (one per dimension) ──────────────────────────────────

    onRegionChange(ev) {
        this.props.onFilterChange({ region: ev.target.value || null });
    }

    onSchoolTypeChange(ev) {
        this.props.onFilterChange({ school_type: ev.target.value || null });
    }

    onSchoolChange(ev) {
        const val = ev.target.value;
        this.props.onFilterChange({ school_id: val ? parseInt(val) : null });
    }
}

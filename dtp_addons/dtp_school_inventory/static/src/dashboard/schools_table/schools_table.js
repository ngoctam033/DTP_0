/** @odoo-module **/
/**
 * SchoolsTable – Data table listing per-school inventory statistics.
 *
 * Props:
 *   rows       : Array<Object>  – school stats rows (from backend)
 *   onRowClick : Function       – callback(schoolId) when a row is clicked
 *
 * Each column is clearly separated in the template for easy customization.
 */

import { Component } from "@odoo/owl";

export class SchoolsTable extends Component {
    static template = "dtp_school_inventory.SchoolsTable";
    static props = {
        rows: Array,
        onRowClick: { type: Function, optional: true },
    };

    get hasData() {
        return this.props.rows && this.props.rows.length > 0;
    }

    onRowClick(row) {
        if (this.props.onRowClick) {
            this.props.onRowClick(row.id);
        }
    }
}

/** @odoo-module **/
/**
 * HorizontalBarChart – SVG horizontal bar chart for top-N products.
 *
 * Props:
 *   data     : Array<Object>  – raw data
 *   labelKey : string         – key for bar label
 *   valueKey : string         – key for bar numeric value
 *
 * Renders pure SVG bars scaled to the max value. No external library.
 */

import { Component } from "@odoo/owl";

const BAR_COLOR = "#4f93f0";
const BAR_HOVER_COLOR = "#1d6fd4";

export class HorizontalBarChart extends Component {
    static template = "dtp_school_inventory.HorizontalBarChart";
    static props = {
        data: Array,
        labelKey: String,
        valueKey: String,
    };

    get hasData() {
        return this.props.data && this.props.data.length > 0;
    }

    /**
     * Returns rows with computed bar width percentage (0–100).
     */
    get rows() {
        const { data, labelKey, valueKey } = this.props;
        const max = Math.max(...data.map(d => d[valueKey] || 0), 1);
        return data.map((item, i) => ({
            label: item[labelKey],
            value: item[valueKey] || 0,
            widthPct: Math.round(((item[valueKey] || 0) / max) * 100),
            color: BAR_COLOR,
        }));
    }
}

/** @odoo-module **/
/**
 * DonutChart – SVG-based donut (pie) chart drawn entirely in OWL, no external lib.
 *
 * Props:
 *   data        : Array<Object>  – raw data array
 *   labelKey    : string         – key for the label in each data item
 *   valueKey    : string         – key for the numeric value
 *   onSliceClick: Function       – callback(item) when a slice is clicked
 *
 * How it works:
 *   - Computes each slice's start/end angles from proportional values.
 *   - Renders SVG <path> elements using arc math (no lib required).
 *   - Legend is rendered alongside.
 */

import { Component } from "@odoo/owl";

// Distinct palette (10 colors)
const PALETTE = [
    "#4f93f0", "#34c98e", "#f59e0b", "#ef4444",
    "#8b5cf6", "#06b6d4", "#f97316", "#ec4899",
    "#14b8a6", "#6366f1",
];

function polarToCartesian(cx, cy, r, angleDeg) {
    const rad = ((angleDeg - 90) * Math.PI) / 180;
    return {
        x: cx + r * Math.cos(rad),
        y: cy + r * Math.sin(rad),
    };
}

function describeArc(cx, cy, r, startAngle, endAngle) {
    const start = polarToCartesian(cx, cy, r, endAngle);
    const end = polarToCartesian(cx, cy, r, startAngle);
    const largeArc = endAngle - startAngle > 180 ? 1 : 0;
    return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArc} 0 ${end.x} ${end.y}`;
}

export class DonutChart extends Component {
    static template = "dtp_school_inventory.DonutChart";
    static props = {
        data: Array,
        labelKey: String,
        valueKey: String,
        onSliceClick: { type: Function, optional: true },
    };

    // Computed slices – called in template via getter
    get slices() {
        const { data, labelKey, valueKey } = this.props;
        const total = data.reduce((s, d) => s + (d[valueKey] || 0), 0);
        if (!total) return [];

        let startAngle = 0;
        return data.map((item, i) => {
            const pct = (item[valueKey] || 0) / total;
            const sweep = pct * 360;
            const endAngle = startAngle + sweep;
            const slice = {
                item,
                color: PALETTE[i % PALETTE.length],
                label: item[labelKey],
                value: item[valueKey],
                pct: Math.round(pct * 100),
                path: sweep < 360
                    ? describeArc(100, 100, 80, startAngle, endAngle)
                    : `M 100 20 A 80 80 0 1 0 100.001 20 Z`, // full circle
                startAngle,
                endAngle,
            };
            startAngle = endAngle;
            return slice;
        });
    }

    get hasData() {
        return this.props.data && this.props.data.length > 0;
    }

    onSliceClick(slice) {
        if (this.props.onSliceClick) {
            this.props.onSliceClick(slice.item);
        }
    }
}

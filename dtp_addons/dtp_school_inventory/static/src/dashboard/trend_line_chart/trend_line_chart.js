/** @odoo-module **/
/**
 * TrendLineChart – SVG polyline trend chart showing monthly picking counts.
 *
 * Props:
 *   data     : Array<{month: string, count: number}>
 *   labelKey : string  – key for X-axis label (e.g. 'month')
 *   valueKey : string  – key for Y value (e.g. 'count')
 *
 * Implementation: pure SVG polyline + grid lines + axis labels. No external lib.
 */

import { Component } from "@odoo/owl";

const SVG_W = 560;
const SVG_H = 160;
const PAD_L = 40;
const PAD_R = 20;
const PAD_T = 20;
const PAD_B = 30;
const LINE_COLOR = "#4f93f0";
const AREA_COLOR = "rgba(79,147,240,0.15)";
const DOT_COLOR = "#1d6fd4";

export class TrendLineChart extends Component {
    static template = "dtp_school_inventory.TrendLineChart";
    static props = {
        data: Array,
        labelKey: String,
        valueKey: String,
    };

    get hasData() {
        return this.props.data && this.props.data.length > 1;
    }

    /**
     * Precompute all SVG coordinates for points, labels, grid lines, area path.
     */
    get chartGeometry() {
        const { data, labelKey, valueKey } = this.props;
        const n = data.length;
        const maxVal = Math.max(...data.map(d => d[valueKey] || 0), 1);

        const plotW = SVG_W - PAD_L - PAD_R;
        const plotH = SVG_H - PAD_T - PAD_B;

        const points = data.map((d, i) => ({
            x: PAD_L + (i / (n - 1)) * plotW,
            y: PAD_T + plotH - ((d[valueKey] || 0) / maxVal) * plotH,
            label: d[labelKey],
            value: d[valueKey],
        }));

        const polylinePoints = points.map(p => `${p.x},${p.y}`).join(" ");

        // Area fill path: go along points then back along baseline
        const first = points[0];
        const last = points[points.length - 1];
        const areaPath =
            `M ${first.x},${PAD_T + plotH} ` +
            points.map(p => `L ${p.x},${p.y}`).join(" ") +
            ` L ${last.x},${PAD_T + plotH} Z`;

        // Y-axis grid lines (4 ticks)
        const yTicks = [0, 0.25, 0.5, 0.75, 1].map(f => ({
            y: PAD_T + plotH - f * plotH,
            label: Math.round(f * maxVal),
        }));

        return { points, polylinePoints, areaPath, yTicks, plotH };
    }
}

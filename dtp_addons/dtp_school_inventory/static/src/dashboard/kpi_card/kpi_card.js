/** @odoo-module **/
/**
 * KpiCard – Single metric tile.
 *
 * Props:
 *   label     : string   – human-readable metric name
 *   value     : number   – the metric value
 *   icon      : string   – Font Awesome icon class (e.g. 'fa-school')
 *   colorClass: string   – CSS modifier class (kpi-blue, kpi-green, kpi-red, …)
 *   clickable : boolean  – whether the card is interactive
 *   onCardClick: Function – callback when card is clicked (only if clickable)
 */

import { Component } from "@odoo/owl";

export class KpiCard extends Component {
    static template = "dtp_school_inventory.KpiCard";
    static props = {
        label: String,
        value: { type: Number, optional: true },
        icon: String,
        colorClass: String,
        clickable: { type: Boolean, optional: true },
        onCardClick: { type: Function, optional: true },
    };

    get displayValue() {
        const v = this.props.value;
        if (v === undefined || v === null) return "–";
        if (v >= 1000) return (v / 1000).toFixed(1) + "k";
        return String(v);
    }

    onClick() {
        if (this.props.clickable && this.props.onCardClick) {
            this.props.onCardClick();
        }
    }
}

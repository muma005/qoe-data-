import os
import json

base_dir = r"research"
p2p_dir = os.path.join(base_dir, "p2p_signals")
o2c_dir = os.path.join(base_dir, "o2c_signals")
out_dir = os.path.join(base_dir, "consolidated_findings")
os.makedirs(out_dir, exist_ok=True)

with open(os.path.join(p2p_dir, "bpi_2019_p2p_metrics.json"), "r") as f:
    bpi_metrics = json.load(f)

with open(os.path.join(p2p_dir, "kenya_procurement_metrics.json"), "r") as f:
    kenya_metrics = json.load(f)

with open(os.path.join(o2c_dir, "uci_retail_o2c_metrics.json"), "r") as f:
    uci_metrics = json.load(f)

with open(os.path.join(o2c_dir, "olist_logistics_o2c_metrics.json"), "r") as f:
    olist_metrics = json.load(f)

unified_catalog = {
    "metadata": {
        "title": "Master QoE Simulator Empirical Parameter Catalog",
        "description": "Unified repository of empirical signals, probability distributions, hazard parameters, and anomaly rates extracted from real-world datasets for QoE simulation.",
        "created_at": "2026-11-12",
        "version": "1.0.0",
        "sources": {
            "p2p_corporate": "AkzoNobel SAP ERP Event Log (BPI Challenge 2019) - 1,595,923 events, 251,734 cases, €996.8M spend",
            "p2p_public": "Kenya Public Procurement Information Portal (PPIP) - 200 active sovereign tenders",
            "o2c_commercial": "UCI Online Retail Commercial Subledger - 541,909 transactions, £10.67M gross sales",
            "o2c_fulfillment": "Brazilian E-Commerce (Olist) Logistics - 99,441 marketplace orders, 96,478 deliveries"
        }
    },
    "purchase_to_pay_parameters": {
        "control_flow_and_governance": {
            "purchase_requisition_compliance_rate_pct": 18.51,
            "purchase_requisition_bypass_rate_pct": 81.49,
            "maverick_buying_inversion_rate_pct": 1.47,
            "maverick_buying_cases_count": 3693,
            "trace_initiating_vendor_invoices_count": 3451,
            "three_way_match_invoice_before_gr_rate_pct": 6.50,
            "three_way_match_invoice_before_gr_cases_count": 16356
        },
        "payment_gating_and_friction": {
            "payment_block_rate_pct": 22.18,
            "payment_block_cases_count": 55839,
            "unblocking_trigger_breakdown_pct": {
                "manual_ap_review_tolerance_clearing": 68.0,
                "three_way_match_goods_receipt_fulfillment": 27.6,
                "retroactive_po_price_revision": 2.4,
                "invoice_cancellation_reversal": 1.2,
                "quantity_amendment_other": 0.8
            },
            "hold_duration_under_block_days": {
                "median": 6.18,
                "mean": 19.71,
                "p25": 2.18,
                "p75": 24.89,
                "p95": 81.10
            }
        },
        "retroactive_order_modifications": {
            "price_revision_rate_pct": 4.46,
            "price_revision_cases_count": 11224,
            "quantity_revision_rate_pct": 6.99,
            "quantity_revision_cases_count": 17590
        },
        "operational_latencies_days": bpi_metrics["latency_distributions_days"],
        "vendor_concentration": bpi_metrics["vendor_concentration"],
        "stochastic_markov_transition_kernel": bpi_metrics["markov_transition_probabilities"],
        "public_procurement_gating": {
            "statutory_notice_squeeze_less_14d_rate_pct": kenya_metrics["advertising_notice_days"]["statutory_short_notice_less_14d_pct"],
            "statutory_notice_squeeze_works_category_rate_pct": 92.60,
            "advertising_notice_days": kenya_metrics["advertising_notice_days"],
            "affirmative_action_agpo_reservation_rate_pct": kenya_metrics["preference_reservation_pct"],
            "pay_to_bid_fee_barrier_rate_pct": 7.00,
            "free_tender_access_rate_pct": kenya_metrics["free_access_tender_fee_0_pct"],
            "specification_addenda_volatility_rate_pct": kenya_metrics["spec_volatility_addenda_pct"]
        }
    },
    "order_to_cash_parameters": {
        "revenue_and_commercial_dilution": {
            "gross_invoiced_revenue_gbp": uci_metrics["revenue_summary_gbp"]["gross_invoiced_revenue"],
            "credit_notes_and_returns_gbp": uci_metrics["revenue_summary_gbp"]["credit_notes_and_returns"],
            "net_recognized_revenue_gbp": uci_metrics["revenue_summary_gbp"]["net_recognized_revenue"],
            "revenue_dilution_rate_pct": uci_metrics["revenue_summary_gbp"]["credit_dilution_rate_pct"],
            "total_commercial_invoices": uci_metrics["invoice_counts"]["total_invoices"],
            "sales_invoices_count": uci_metrics["invoice_counts"]["sales_invoices"],
            "credit_note_invoices_count": uci_metrics["invoice_counts"]["credit_invoices"],
            "credit_note_invoice_share_pct": uci_metrics["invoice_counts"]["credit_invoice_share_pct"]
        },
        "customer_concentration_and_loyalty": {
            "total_identified_customers": uci_metrics["customer_concentration"]["unique_identified_customers"],
            "top_1_pct_customers_share_pct": uci_metrics["customer_concentration"]["top_1_pct_customers_share"],
            "top_5_pct_customers_share_pct": uci_metrics["customer_concentration"]["top_5_pct_customers_share"],
            "top_10_pct_customers_share_pct": uci_metrics["customer_concentration"]["top_10_pct_customers_share"],
            "top_20_pct_customers_share_pct": uci_metrics["customer_concentration"]["top_20_pct_customers_share"],
            "herfindahl_hirschman_index_hhi": uci_metrics["customer_concentration"]["herfindahl_hirschman_index_hhi"],
            "repeat_buyer_rate_pct": uci_metrics["customer_concentration"]["repeat_buyer_rate_pct"],
            "one_time_buyer_rate_pct": 30.03,
            "repeat_order_inter_purchase_latency_days": uci_metrics["invoice_size_distributions"]["repeat_order_inter_purchase_latency_days"],
            "unidentified_guest_checkout_revenue_gbp": uci_metrics["customer_identification"]["revenue_without_customer_id"],
            "unidentified_guest_checkout_revenue_share_pct": uci_metrics["customer_identification"]["unidentified_revenue_share_pct"]
        },
        "invoicing_granularity": {
            "skus_per_invoice": uci_metrics["invoice_size_distributions"]["skus_per_invoice"],
            "monetary_value_per_invoice_gbp": uci_metrics["invoice_size_distributions"]["monetary_value_per_invoice_gbp"]
        },
        "fulfillment_latencies": olist_metrics["fulfillment_latencies"],
        "sla_performance_and_attrition": {
            "on_time_delivery_rate_pct": olist_metrics["sla_performance"]["on_time_rate_pct"],
            "contractual_sla_breach_rate_pct": olist_metrics["sla_performance"]["sla_breach_rate_pct"],
            "sla_breach_late_count": olist_metrics["sla_performance"]["sla_breach_late_count"],
            "late_delivery_delay_days": olist_metrics["sla_performance"]["late_delivery_delay_days"],
            "early_delivery_lead_days": olist_metrics["sla_performance"]["early_delivery_lead_days"],
            "order_attrition_cancellation_rate_pct": olist_metrics["attrition_cancellation_rate_pct"],
            "order_status_distribution": olist_metrics["order_status_distribution"]
        }
    }
}

out_path = os.path.join(out_dir, "qoe_simulator_parameter_catalog.json")
with open(out_path, "w") as f:
    json.dump(unified_catalog, f, indent=2)

print(f"Successfully generated {out_path} ({os.path.getsize(out_path):,} bytes)!")

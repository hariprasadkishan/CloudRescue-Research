"""Generates a preliminary 3-way ablation comparison report: CFG-A vs. CFG-B vs. CFG-C."""

from __future__ import annotations
import json
import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def load_summary(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def fmt_diff(v_new: float | None, v_old: float | None, unit: str = "", decimals: int = 2) -> str:
    if v_new is None or v_old is None:
        return "N/A"
    diff = round(v_new - v_old, decimals)
    prefix = "+" if diff > 0 else ""
    return f"{prefix}{diff}{unit}"


def main() -> None:
    cfg_a_path = os.path.join(PROJECT_ROOT, "results", "validation_run_baseline", "summary.json")
    cfg_b_path = os.path.join(PROJECT_ROOT, "results", "validation_run_brownout", "summary.json")
    cfg_c_path = os.path.join(PROJECT_ROOT, "results", "validation_run_balb", "summary.json")

    missing = []
    if not os.path.exists(cfg_a_path):
        missing.append("scripts/run_baseline.py")
    if not os.path.exists(cfg_b_path):
        missing.append("scripts/run_brownout.py")
    if not os.path.exists(cfg_c_path):
        missing.append("scripts/run_balb.py")

    if missing:
        print(f"Error: Missing summary files. Please run the following runner(s) first:\n" + "\n".join(f"  - {m}" for m in missing))
        sys.exit(1)

    data_a = load_summary(cfg_a_path)
    data_b = load_summary(cfg_b_path)
    data_c = load_summary(cfg_c_path)

    m_a = data_a["metrics"]
    m_b = data_b["metrics"]
    m_c = data_c["metrics"]

    print("=========================================================================================================================")
    print("                     CloudRescue — Preliminary 3-Way Ablation Comparison (Phase 3)                                     ")
    print("=========================================================================================================================")
    print("NOTE: Preliminary validation comparison based on single seed (Seed=42, 20s run, identical arrival streams).            ")
    print("      Statistical significance cannot and must not be claimed from a single preliminary validation run.                 ")
    print("-------------------------------------------------------------------------------------------------------------------------")
    header = f"{'Metric':<38} | {'CFG-A (Baseline)':<16} | {'CFG-B (Brownout)':<16} | {'CFG-C (BALB)':<16} | {'Delta (B-A)':<12} | {'Delta (C-B)':<12}"
    print(header)
    print("-" * len(header))

    def row(name: str, val_a, val_b, val_c, d_ba: str = "", d_cb: str = "") -> None:
        print(f"{name:<38} | {str(val_a):<16} | {str(val_b):<16} | {str(val_c):<16} | {d_ba:<12} | {d_cb:<12}")

    row("Submitted Requests (post-warmup)", m_a["n_submitted"], m_b["n_submitted"], m_c["n_submitted"])
    row("Completed Requests (N_success)", m_a["n_success"], m_b["n_success"], m_c["n_success"],
        fmt_diff(m_b["n_success"], m_a["n_success"], decimals=0),
        fmt_diff(m_c["n_success"], m_b["n_success"], decimals=0))
    row("Queue Full Drops", m_a["drop_queue_count"], m_b["drop_queue_count"], m_c["drop_queue_count"],
        fmt_diff(m_b["drop_queue_count"], m_a["drop_queue_count"], decimals=0),
        fmt_diff(m_c["drop_queue_count"], m_b["drop_queue_count"], decimals=0))
    row("HOL Timeout Drops", m_a["drop_timeout_count"], m_b["drop_timeout_count"], m_c["drop_timeout_count"],
        fmt_diff(m_b["drop_timeout_count"], m_a["drop_timeout_count"], decimals=0),
        fmt_diff(m_c["drop_timeout_count"], m_b["drop_timeout_count"], decimals=0))
    row("Latency SLA Violations (>100ms)", m_a["lat_violations_count"], m_b["lat_violations_count"], m_c["lat_violations_count"],
        fmt_diff(m_b["lat_violations_count"], m_a["lat_violations_count"], decimals=0),
        fmt_diff(m_c["lat_violations_count"], m_b["lat_violations_count"], decimals=0))

    row("Request Success Rate (Sr, %)", f"{m_a['sr_percent']}%", f"{m_b['sr_percent']}%", f"{m_c['sr_percent']}%",
        fmt_diff(m_b["sr_percent"], m_a["sr_percent"], "%"),
        fmt_diff(m_c["sr_percent"], m_b["sr_percent"], "%"))
    row("Latency SLA Violation Rate (V_lat, %)", f"{m_a['v_lat_percent']}%", f"{m_b['v_lat_percent']}%", f"{m_c['v_lat_percent']}%",
        fmt_diff(m_b["v_lat_percent"], m_a["v_lat_percent"], "%"),
        fmt_diff(m_c["v_lat_percent"], m_b["v_lat_percent"], "%"))
    row("Overall SLA Failure Rate (V_overall, %)", f"{m_a['v_overall_percent']}%", f"{m_b['v_overall_percent']}%", f"{m_c['v_overall_percent']}%",
        fmt_diff(m_b["v_overall_percent"], m_a["v_overall_percent"], "%"),
        fmt_diff(m_c["v_overall_percent"], m_b["v_overall_percent"], "%"))

    p50_a = m_a.get("p50_latency_ms")
    p50_b = m_b.get("p50_latency_ms")
    p50_c = m_c.get("p50_latency_ms")
    row("Median Latency (p50, ms)", f"{p50_a} ms" if p50_a is not None else "N/A",
        f"{p50_b} ms" if p50_b is not None else "N/A",
        f"{p50_c} ms" if p50_c is not None else "N/A",
        fmt_diff(p50_b, p50_a, " ms") if (p50_a and p50_b) else "",
        fmt_diff(p50_c, p50_b, " ms") if (p50_b and p50_c) else "")

    row("95th Percentile Latency (p95, ms)", f"{m_a['p95_latency_ms']} ms", f"{m_b['p95_latency_ms']} ms", f"{m_c['p95_latency_ms']} ms",
        fmt_diff(m_b["p95_latency_ms"], m_a["p95_latency_ms"], " ms"),
        fmt_diff(m_c["p95_latency_ms"], m_b["p95_latency_ms"], " ms"))

    p99_a = m_a.get("p99_latency_ms")
    p99_b = m_b.get("p99_latency_ms")
    p99_c = m_c.get("p99_latency_ms")
    row("99th Percentile Latency (p99, ms)", f"{p99_a} ms" if p99_a is not None else "N/A",
        f"{p99_b} ms" if p99_b is not None else "N/A",
        f"{p99_c} ms" if p99_c is not None else "N/A",
        fmt_diff(p99_b, p99_a, " ms") if (p99_a and p99_b) else "",
        fmt_diff(p99_c, p99_b, " ms") if (p99_b and p99_c) else "")

    row("Mean Latency (L_mean, ms)", f"{m_a['mean_latency_ms']} ms", f"{m_b['mean_latency_ms']} ms", f"{m_c['mean_latency_ms']} ms",
        fmt_diff(m_b["mean_latency_ms"], m_a["mean_latency_ms"], " ms"),
        fmt_diff(m_c["mean_latency_ms"], m_b["mean_latency_ms"], " ms"))

    row("Service Fidelity (F, %)", f"{m_a['fidelity_percent']}%", f"{m_b['fidelity_percent']}%", f"{m_c['fidelity_percent']}%",
        fmt_diff(m_b["fidelity_percent"], m_a["fidelity_percent"], "%"),
        fmt_diff(m_c["fidelity_percent"], m_b["fidelity_percent"], "%"))

    theta_a = m_a.get("mean_dimmer", 1.0)
    theta_b = m_b.get("mean_dimmer", 1.0)
    theta_c = m_c.get("mean_dimmer", 1.0)
    row("Mean Operational Dimmer (theta_mean)", f"{theta_a}", f"{theta_b}", f"{theta_c}",
        fmt_diff(theta_b, theta_a, decimals=4),
        fmt_diff(theta_c, theta_b, decimals=4))

    u_a = data_a["mean_utilization"]
    u_b = data_b["mean_utilization"]
    u_c = data_c["mean_utilization"]
    row("Mean Worker Utilization (U_mean, %)", f"{u_a}%", f"{u_b}%", f"{u_c}%",
        fmt_diff(u_b, u_a, "%"),
        fmt_diff(u_c, u_b, "%"))

    j_a = data_a["jains_fairness_index"]
    j_b = data_b["jains_fairness_index"]
    j_c = data_c["jains_fairness_index"]
    row("Jain's Fairness Index (J)", f"{j_a}", f"{j_b}", f"{j_c}",
        fmt_diff(j_b, j_a, decimals=4),
        fmt_diff(j_c, j_b, decimals=4))

    print("-------------------------------------------------------------------------------------------------------------------------")
    print("PER-WORKER OPERATIONAL DIMMER (theta_i):")
    pw_a = m_a.get("per_worker_theta", {str(i): 1.0 for i in range(4)})
    pw_b = m_b.get("per_worker_theta", {})
    pw_c = m_c.get("per_worker_theta", {})
    for w in sorted(set(list(pw_a.keys()) + list(pw_b.keys()) + list(pw_c.keys()))):
        print(f"  Worker {w:>2}:  CFG-A = {pw_a.get(w, 1.0):<6} | CFG-B = {pw_b.get(w, 'N/A'):<6} | CFG-C = {pw_c.get(w, 'N/A'):<6}")

    print("-------------------------------------------------------------------------------------------------------------------------")
    print("BALB ROUTING DIAGNOSTICS (CFG-C):")
    balb_diag = data_c.get("balb_diagnostics_summary", {})
    print(f"  Total Routing Decisions: {balb_diag.get('total_routing_decisions', 'N/A')}")
    print(f"  Fallback Decisions:     {balb_diag.get('fallback_decisions', 'N/A')} ({balb_diag.get('fallback_rate_percent', 'N/A')}%)")
    print("=========================================================================================================================")


if __name__ == "__main__":
    main()

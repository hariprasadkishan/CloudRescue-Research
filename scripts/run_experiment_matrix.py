"""CloudRescue Phase 4 — Master Experiment Matrix Runner (360 Runs).

Executes the pre-registered full experimental matrix:
3 Configurations x 4 Scenarios x 30 Matched Seeds = 360 Runs.

Configurations:
- CFG-A: Baseline (No brownout, JSQ)
- CFG-B: Brownout Only (Adaptive PI controller, JSQ)
- CFG-C: Full CloudRescue (Adaptive PI controller, BALB)

Scenarios:
1. Nominal: lambda_nom = 80 req/s, no burst, no failures
2. Flash crowd: 80 -> 240 req/s (300s - 450s), no failures
3. Server failure: workers 1 & 2 down (300s - 450s), no burst
4. Compound stress: 80 -> 240 req/s and workers 1 & 2 down (300s - 450s)

Duration:
T_sim = 1,000 s (1,000,000 ms), Warmup = 100 s (100,000 ms).
"""

from __future__ import annotations
import argparse
import gzip
import json
import logging
import multiprocessing
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulator.cloudrescue.config import SimulationConfig, FailureSchedule
from simulator.cloudrescue.engine.simulation import SimulationEngine
from simulator.cloudrescue.monitoring.recovery_analyzer import compute_recovery_metrics


SCENARIOS = {
    "nominal": {
        "lambda_nom": 0.08,
        "lambda_burst": 0.0,
        "burst_start_ms": 300_000.0,
        "burst_duration_ms": 0.0,
        "fail_schedules": [],
        "shock_start_ms": None,
        "shock_end_ms": None,
    },
    "flash_crowd": {
        "lambda_nom": 0.08,
        "lambda_burst": 0.24,
        "burst_start_ms": 300_000.0,
        "burst_duration_ms": 150_000.0,
        "fail_schedules": [],
        "shock_start_ms": 300_000.0,
        "shock_end_ms": 450_000.0,
    },
    "server_failure": {
        "lambda_nom": 0.08,
        "lambda_burst": 0.0,
        "burst_start_ms": 300_000.0,
        "burst_duration_ms": 0.0,
        "fail_schedules": [
            FailureSchedule(worker_ids=[1, 2], t_fail=300_000.0, t_repair=450_000.0)
        ],
        "shock_start_ms": 300_000.0,
        "shock_end_ms": 450_000.0,
    },
    "compound_stress": {
        "lambda_nom": 0.08,
        "lambda_burst": 0.24,
        "burst_start_ms": 300_000.0,
        "burst_duration_ms": 150_000.0,
        "fail_schedules": [
            FailureSchedule(worker_ids=[1, 2], t_fail=300_000.0, t_repair=450_000.0)
        ],
        "shock_start_ms": 300_000.0,
        "shock_end_ms": 450_000.0,
    },
}

CONFIGS = ["CFG-A", "CFG-B", "CFG-C"]
DEFAULT_SEEDS = list(range(1001, 1031))  # 30 seeds: 1001 to 1030


def run_single_simulation(task: Dict[str, Any]) -> Dict[str, Any]:
    """Worker task executing a single simulation run."""
    scenario_name = task["scenario"]
    config_mode = task["config"]
    seed = task["seed"]
    output_base_dir = Path(task["output_dir"])
    save_all_events = task.get("save_all_events", False)

    scen_info = SCENARIOS[scenario_name]
    t0 = time.time()

    cfg = SimulationConfig(
        mode=config_mode,
        seed=seed,
        sim_time_ms=1_000_000.0,
        warmup_ms=100_000.0,
        lambda_nom=scen_info["lambda_nom"],
        lambda_burst=scen_info["lambda_burst"],
        burst_start_ms=scen_info["burst_start_ms"],
        burst_duration_ms=scen_info["burst_duration_ms"],
        fail_schedules=scen_info["fail_schedules"],
    )

    engine = SimulationEngine(cfg)
    res = engine.run()
    elapsed_s = round(time.time() - t0, 2)

    # Completed requests for recovery analysis
    completed = [
        (e.timestamp, e.data["total_latency"])
        for e in res.logger.events
        if e.event_type == "REQUEST_COMPLETED" and e.data.get("total_latency") is not None
    ]

    ctrl_dfs = [c.get_timeseries_df() for c in res.controllers]
    ctrl_ts = pd.concat(ctrl_dfs, ignore_index=True) if ctrl_dfs else pd.DataFrame()

    rec = compute_recovery_metrics(
        completed_requests=completed,
        controller_timeseries=ctrl_ts,
        t_shock_start_ms=scen_info["shock_start_ms"],
        t_shock_end_ms=scen_info["shock_end_ms"],
        t_sim_end_ms=cfg.sim_time_ms,
        r_sla_ms=cfg.sla_threshold_ms,
        r_target_ms=cfg.target_latency_ms,
    )

    m = res.metrics

    row = {
        "scenario": scenario_name,
        "config": config_mode,
        "seed": seed,
        "n_submitted": m["n_submitted"],
        "n_success": m["n_success"],
        "drop_queue_count": m["drop_queue_count"],
        "drop_timeout_count": m["drop_timeout_count"],
        "crash_failed_count": m["crash_failed_count"],
        "lat_violations_count": m["lat_violations_count"],
        "sr_percent": m["sr_percent"],
        "v_lat_percent": m["v_lat_percent"],
        "v_overall_percent": m["v_overall_percent"],
        "mean_latency_ms": m["mean_latency_ms"],
        "p50_latency_ms": m["p50_latency_ms"],
        "p95_latency_ms": m["p95_latency_ms"],
        "p99_latency_ms": m["p99_latency_ms"],
        "fidelity_percent": m["fidelity_percent"],
        "mean_dimmer": m["mean_dimmer"],
        "mean_utilization": res.mean_utilization,
        "jains_index": res.jains_index,
        "jains_index_all_workers": res.jains_index_all_workers,
        "fairness_population_type": res.fairness_population_type,
        "fairness_status": res.fairness_status,
        "t_adapt_s": rec.t_adapt_s,
        "t_adapt_recovered": rec.t_adapt_recovered,
        "t_restore_s": rec.t_restore_s,
        "t_restore_recovered": rec.t_restore_recovered,
        "total_generated_requests": res.total_generated_requests,
        "runtime_s": elapsed_s,
    }

    # Artifacts directory for this run
    run_dir = output_base_dir / "runs" / scenario_name / f"{config_mode}_seed_{seed}"
    run_dir.mkdir(parents=True, exist_ok=True)

    # 1. summary.json
    summary_data = {
        "scenario": scenario_name,
        "config": config_mode,
        "seed": seed,
        "metrics": m,
        "worker_utilizations": res.worker_utilizations,
        "mean_utilization": res.mean_utilization,
        "jains_fairness_index": res.jains_index,
        "jains_fairness_index_all_workers": res.jains_index_all_workers,
        "fairness_population_type": res.fairness_population_type,
        "fairness_status": res.fairness_status,
        "active_workers_fairness": res.active_workers_fairness,
        "recovery_metrics": {
            "t_adapt_s": rec.t_adapt_s,
            "t_adapt_recovered": rec.t_adapt_recovered,
            "t_restore_s": rec.t_restore_s,
            "t_restore_recovered": rec.t_restore_recovered,
            "notes": rec.notes,
        },
        "runtime_s": elapsed_s,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    with open(run_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    # 2. config.json
    with open(run_dir / "config.json", "w", encoding="utf-8") as f:
        json.dump(cfg.to_dict(), f, indent=2)

    # 3. controller_timeseries.csv (if applicable)
    if not ctrl_ts.empty:
        ctrl_ts.to_csv(run_dir / "controller_timeseries.csv", index=False)

    # 4. balb_diagnostics.csv (if applicable)
    if res.balb_diagnostics is not None and not res.balb_diagnostics.empty:
        res.balb_diagnostics.to_csv(run_dir / "balb_diagnostics.csv", index=False)

    # 5. events.csv.gz (for reference seed 1001 or if save_all_events is True)
    if seed == 1001 or save_all_events:
        res.logger.save_csv(str(run_dir / "events.csv.gz"), compress=True)

    return row


def compute_aggregated_table(df: pd.DataFrame) -> pd.DataFrame:
    """Computes summary statistics (mean, std, median, IQR, min, max) for each group."""
    key_metrics = [
        "sr_percent",
        "v_lat_percent",
        "v_overall_percent",
        "mean_latency_ms",
        "p95_latency_ms",
        "p99_latency_ms",
        "fidelity_percent",
        "mean_dimmer",
        "mean_utilization",
        "jains_index",
        "t_adapt_s",
        "t_restore_s",
    ]

    records = []
    grouped = df.groupby(["scenario", "config"])

    for (scen, cfg_name), group in grouped:
        for metric in key_metrics:
            series = pd.to_numeric(group[metric], errors="coerce").dropna()
            if series.empty:
                continue

            q25 = float(np.percentile(series, 25))
            q75 = float(np.percentile(series, 75))
            records.append({
                "scenario": scen,
                "config": cfg_name,
                "metric": metric,
                "n_runs": len(series),
                "mean": round(float(series.mean()), 4),
                "std": round(float(series.std()), 4) if len(series) > 1 else 0.0,
                "median": round(float(series.median()), 4),
                "iqr": round(float(q75 - q25), 4),
                "min": round(float(series.min()), 4),
                "max": round(float(series.max()), 4),
            })

    return pd.DataFrame(records)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run CloudRescue Phase 4 Full Experiment Matrix (360 runs)."
    )
    parser.add_argument(
        "--processes",
        type=int,
        default=7,
        help="Number of parallel worker processes (default: 7).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results/experiment_360",
        help="Base directory for experiment artifacts (default: results/experiment_360).",
    )
    parser.add_argument(
        "--save-all-events",
        action="store_true",
        help="Save events.csv.gz for all 360 runs (WARNING: requires ~3.3 GB disk space).",
    )
    parser.add_argument(
        "--seeds",
        type=int,
        nargs="+",
        default=DEFAULT_SEEDS,
        help="Custom list of seeds (default: 1001..1030).",
    )
    parser.add_argument(
        "--scenarios",
        type=str,
        nargs="+",
        default=list(SCENARIOS.keys()),
        help="Custom list of scenarios to run.",
    )
    parser.add_argument(
        "--configs",
        type=str,
        nargs="+",
        default=CONFIGS,
        help="Custom list of configurations to run.",
    )

    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Setup execution logging
    log_file = output_dir / "execution.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, mode="w", encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    logger = logging.getLogger("CloudRescueMatrix")

    total_runs = len(args.scenarios) * len(args.configs) * len(args.seeds)
    logger.info("=========================================================================")
    logger.info("        CloudRescue — Phase 4 Master Experiment Matrix Runner            ")
    logger.info("=========================================================================")
    logger.info(f"Target Runs:    {total_runs} (Scenarios: {len(args.scenarios)}, Configs: {len(args.configs)}, Seeds: {len(args.seeds)})")
    logger.info(f"Parallelism:    {args.processes} worker processes")
    logger.info(f"Output Base:    {output_dir.resolve()}")
    logger.info(f"Save All Events: {args.save_all_events} (Default: seed 1001 reference runs only)")
    logger.info("-------------------------------------------------------------------------")

    tasks = []
    for scen in args.scenarios:
        for cfg_name in args.configs:
            for seed in args.seeds:
                tasks.append({
                    "scenario": scen,
                    "config": cfg_name,
                    "seed": seed,
                    "output_dir": str(output_dir),
                    "save_all_events": args.save_all_events,
                })

    start_time = time.time()
    results_rows: List[Dict[str, Any]] = []

    logger.info(f"Launching {len(tasks)} simulation jobs...")

    with multiprocessing.Pool(processes=args.processes) as pool:
        for i, row in enumerate(pool.imap_unordered(run_single_simulation, tasks), 1):
            results_rows.append(row)
            pct = round((i / total_runs) * 100.0, 1)
            logger.info(
                f"[{i:3d}/{total_runs}] ({pct:5.1f}%) "
                f"Scenario: {row['scenario']:<16} | Config: {row['config']} | Seed: {row['seed']} | "
                f"Sr: {row['sr_percent']:5.1f}% | V_lat: {row['v_lat_percent']:5.1f}% | "
                f"V_ovr: {row['v_overall_percent']:5.1f}% | Time: {row['runtime_s']:4.1f}s"
            )

    total_duration_s = round(time.time() - start_time, 2)
    logger.info("-------------------------------------------------------------------------")
    logger.info(f"All {len(results_rows)}/{total_runs} runs completed in {total_duration_s:.1f}s (~{total_duration_s/60:.1f} minutes).")

    # Master results DataFrame
    df_results = pd.DataFrame(results_rows)
    # Sort deterministically by scenario, config, seed
    scenario_order = {s: i for i, s in enumerate(args.scenarios)}
    config_order = {c: i for i, c in enumerate(args.configs)}
    df_results["scen_idx"] = df_results["scenario"].map(scenario_order)
    df_results["cfg_idx"] = df_results["config"].map(config_order)
    df_results = df_results.sort_values(["scen_idx", "cfg_idx", "seed"]).drop(columns=["scen_idx", "cfg_idx"]).reset_index(drop=True)

    master_csv_path = output_dir / "master_results.csv"
    df_results.to_csv(master_csv_path, index=False)
    logger.info(f"Saved master results to: {master_csv_path.resolve()}")

    # Aggregated metrics DataFrame
    df_agg = compute_aggregated_table(df_results)
    agg_csv_path = output_dir / "aggregated_metrics.csv"
    df_agg.to_csv(agg_csv_path, index=False)
    logger.info(f"Saved aggregated metrics to: {agg_csv_path.resolve()}")

    # Verification of complete execution
    assert len(df_results) == total_runs, f"Expected {total_runs} runs, got {len(df_results)}"
    logger.info("=========================================================================")
    logger.info(f"Verification PASSED: Exactly {total_runs}/{total_runs} runs executed with 0 failures.")
    logger.info("=========================================================================")


if __name__ == "__main__":
    main()

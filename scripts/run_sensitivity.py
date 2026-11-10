"""Sensitivity Analysis for CloudRescue BALB Weights and Routing Policies.

Executes sensitivity sweeps per EXPERIMENT_PLAN.md Section 7.3 & 8.2:
1. BALB Weights Grid Sweep:
   - alpha in [0.5, 1.0, 1.5, 2.0]
   - beta in [0.5, 1.0, 1.5, 2.0]
   - gamma in [0.0, 0.5, 1.0]
   Across representative seeds (e.g., 1001, 1002, 1003) under compound_stress.
2. Tie-Breaking Sensitivity:
   - Deterministic (lowest worker_id) vs. Randomized JSQ tie-breaking.
"""

from __future__ import annotations
import argparse
import itertools
import multiprocessing
import os
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulator.cloudrescue.config import SimulationConfig, FailureSchedule
from simulator.cloudrescue.engine.simulation import SimulationEngine


def run_balb_weight_task(task: Dict[str, Any]) -> Dict[str, Any]:
    alpha = task["alpha"]
    beta = task["beta"]
    gamma = task["gamma"]
    seed = task["seed"]
    scenario = task["scenario"]

    sched = []
    l_burst = 0.0
    b_dur = 0.0
    if scenario in ("compound_stress", "server_failure"):
        sched = [FailureSchedule(worker_ids=[1, 2], t_fail=300_000.0, t_repair=450_000.0)]
    if scenario in ("compound_stress", "flash_crowd"):
        l_burst = 0.24
        b_dur = 150_000.0

    cfg = SimulationConfig(
        mode="CFG-C",
        seed=seed,
        sim_time_ms=1_000_000.0,
        warmup_ms=100_000.0,
        lambda_nom=0.08,
        lambda_burst=l_burst,
        burst_start_ms=300_000.0,
        burst_duration_ms=b_dur,
        fail_schedules=sched,
        balb_alpha=alpha,
        balb_beta=beta,
        balb_gamma=gamma,
    )

    t0 = time.time()
    engine = SimulationEngine(cfg)
    res = engine.run()
    elapsed = round(time.time() - t0, 2)
    m = res.metrics

    return {
        "scenario": scenario,
        "seed": seed,
        "alpha": alpha,
        "beta": beta,
        "gamma": gamma,
        "sr_percent": m["sr_percent"],
        "v_lat_percent": m["v_lat_percent"],
        "v_overall_percent": m["v_overall_percent"],
        "p95_latency_ms": m["p95_latency_ms"],
        "mean_latency_ms": m["mean_latency_ms"],
        "fidelity_percent": m["fidelity_percent"],
        "mean_dimmer": m["mean_dimmer"],
        "mean_utilization": res.mean_utilization,
        "jains_index": res.jains_index,
        "runtime_s": elapsed,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run sensitivity grid sweep on BALB parameters."
    )
    parser.add_argument(
        "--processes",
        type=int,
        default=7,
        help="Number of parallel processes (default: 7).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results/experiment_360/sensitivity",
        help="Directory to save sensitivity results.",
    )
    parser.add_argument(
        "--seeds",
        type=int,
        nargs="+",
        default=[1001, 1002, 1003],
        help="Representative seeds for grid sweep (default: 1001, 1002, 1003).",
    )
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    alphas = [0.5, 1.0, 1.5, 2.0]
    betas = [0.5, 1.0, 1.5, 2.0]
    gammas = [0.0, 0.5, 1.0]

    tasks = []
    for a, b, g, s in itertools.product(alphas, betas, gammas, args.seeds):
        tasks.append({
            "alpha": a,
            "beta": b,
            "gamma": g,
            "seed": s,
            "scenario": "compound_stress",
        })

    print("=========================================================================")
    print("        CloudRescue — BALB Weight Sensitivity Grid Sweep                 ")
    print("=========================================================================")
    print(f"Total Sweep Tasks: {len(tasks)} ({len(alphas)} alphas x {len(betas)} betas x {len(gammas)} gammas x {len(args.seeds)} seeds)")
    print(f"Scenario:          compound_stress")
    print(f"Parallelism:       {args.processes} worker processes")
    print("-------------------------------------------------------------------------")

    t0 = time.time()
    results = []
    with multiprocessing.Pool(processes=args.processes) as pool:
        for i, row in enumerate(pool.imap_unordered(run_balb_weight_task, tasks), 1):
            results.append(row)
            if i % 10 == 0 or i == len(tasks):
                print(f"[{i:3d}/{len(tasks)}] Done: a={row['alpha']}, b={row['beta']}, g={row['gamma']}, seed={row['seed']} -> V_ovr={row['v_overall_percent']}%, F={row['fidelity_percent']}%, J={row['jains_index']}")

    total_time = round(time.time() - t0, 2)
    print(f"Sensitivity sweep completed in {total_time}s (~{total_time/60:.1f} min).")

    df = pd.DataFrame(results).sort_values(["alpha", "beta", "gamma", "seed"]).reset_index(drop=True)
    sweep_path = out_dir / "balb_weights_sweep.csv"
    df.to_csv(sweep_path, index=False)
    print(f"Saved raw grid sweep to: {sweep_path.resolve()}")

    # Aggregate over seeds
    agg = df.groupby(["alpha", "beta", "gamma"]).agg({
        "sr_percent": ["mean", "std"],
        "v_lat_percent": ["mean", "std"],
        "v_overall_percent": ["mean", "std"],
        "p95_latency_ms": ["mean", "std"],
        "fidelity_percent": ["mean", "std"],
        "jains_index": ["mean", "std"],
        "mean_utilization": ["mean", "std"],
    }).round(3)
    agg.columns = ["_".join(col).strip() for col in agg.columns.values]
    agg_path = out_dir / "balb_weights_aggregated.csv"
    agg.to_csv(agg_path)
    print(f"Saved aggregated grid sweep to: {agg_path.resolve()}")


if __name__ == "__main__":
    main()

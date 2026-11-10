"""CLI runner for CloudRescue Phase 1 Baseline Validation Simulation (CFG-A).

Executes a preliminary baseline simulation under Join-Shortest-Queue (JSQ) with
static feature dimmer (theta = 1.0).
Saves execution artifacts to the specified output directory.
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timezone

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from simulator.cloudrescue.config import SimulationConfig, FailureSchedule
from simulator.cloudrescue.engine.simulation import SimulationEngine


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run CloudRescue CFG-A Baseline Validation Simulation."
    )
    parser.add_argument(
        "--sim-time-s",
        type=float,
        default=20.0,
        help="Total simulation duration in seconds (default: 20.0s).",
    )
    parser.add_argument(
        "--warmup-s",
        type=float,
        default=2.0,
        help="Warm-up duration in seconds excluded from summary metrics (default: 2.0s).",
    )
    parser.add_argument(
        "--lambda-nom",
        type=float,
        default=80.0,
        help="Nominal arrival rate in requests per second (default: 80.0 req/s).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Master pseudorandom seed (default: 42).",
    )
    parser.add_argument(
        "--with-crash",
        action="store_true",
        help="Inject a server crash-stop failure during the run (workers 1 & 2 down from 8s to 14s).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results/validation_run_baseline",
        help="Directory where validation artifacts will be stored.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # Convert seconds to milliseconds for engine consistency
    sim_time_ms = args.sim_time_s * 1000.0
    warmup_ms = args.warmup_s * 1000.0
    lambda_nom_ms = args.lambda_nom / 1000.0

    fail_schedules = []
    if args.with_crash:
        fail_schedules.append(
            FailureSchedule(
                worker_ids=[1, 2],
                t_fail=8000.0,
                t_repair=14000.0,
            )
        )

    config = SimulationConfig(
        num_workers=4,
        queue_capacity=50,
        mu_mand=0.1,             # 10 ms
        mu_opt=1.0 / 30.0,       # 30 ms
        timeout_ms=200.0,
        sla_threshold_ms=100.0,
        target_latency_ms=80.0,
        lambda_nom=lambda_nom_ms,
        sim_time_ms=sim_time_ms,
        warmup_ms=warmup_ms,
        seed=args.seed,
        fail_schedules=fail_schedules,
    )

    print("=================================================================")
    print("      CloudRescue — Baseline Simulation Runner (CFG-A)          ")
    print("=================================================================")
    print(f"Configuration: CFG-A (Baseline, No Brownout, JSQ Routing)")
    print(f"Workers:       {config.num_workers} (Queue Capacity: {config.queue_capacity})")
    print(f"Duration:      {args.sim_time_s}s ({sim_time_ms:.0f} ms)")
    print(f"Warm-Up:       {args.warmup_s}s ({warmup_ms:.0f} ms)")
    print(f"Arrival Rate:  {args.lambda_nom} req/s ({lambda_nom_ms:.4f} req/ms)")
    print(f"Master Seed:   {args.seed}")
    print(f"Failures:      {'Yes (Workers 1,2 @ 8s-14s)' if args.with_crash else 'None (Nominal)'}")
    print("-----------------------------------------------------------------")
    print("Executing simulation...")

    engine = SimulationEngine(config)
    result = engine.run()

    print("Simulation completed successfully.")
    print("-----------------------------------------------------------------")
    print("PRELIMINARY BASELINE METRICS (Validation run only):")
    for k, v in result.metrics.items():
        print(f"  {k:22s}: {v}")
    print(f"  {'mean_utilization':22s}: {result.mean_utilization}%")
    print(f"  {'jains_fairness_index':22s}: {result.jains_index}")
    print("  Worker Utilizations   :")
    for wid, u in result.worker_utilizations.items():
        print(f"    Worker {wid:2d}          : {u}%")
    print("-----------------------------------------------------------------")

    # Persist artifacts
    os.makedirs(args.output_dir, exist_ok=True)

    config_path = os.path.join(args.output_dir, "config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config.to_dict(), f, indent=2)

    events_path = os.path.join(args.output_dir, "events.csv.gz")
    result.logger.save_csv(events_path, compress=True)

    summary_data = {
        "validation_metadata": {
            "status": "PRELIMINARY_BASELINE_VALIDATION",
            "note": "Phase 1 validation artifact. NOT final experimental research results.",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "python_version": sys.version,
            "seed": args.seed,
            "sim_time_s": args.sim_time_s,
            "warmup_s": args.warmup_s,
        },
        "metrics": result.metrics,
        "worker_utilizations": result.worker_utilizations,
        "mean_utilization": result.mean_utilization,
        "jains_fairness_index": result.jains_index,
        "total_generated_requests": result.total_generated_requests,
    }

    summary_path = os.path.join(args.output_dir, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    readme_path = os.path.join(args.output_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("# CloudRescue — Phase 1 Baseline Validation Run\n\n")
        f.write("> **IMPORTANT NOTICE:** This directory contains preliminary validation run artifacts generated during Phase 1 engine verification. These are **NOT** final experimental research findings.\n\n")
        f.write(f"- **Configuration:** CFG-A (Baseline, $\\theta=1.0$, Join-Shortest-Queue)\n")
        f.write(f"- **Simulation Time:** {args.sim_time_s} s ({sim_time_ms:.0f} ms)\n")
        f.write(f"- **Warm-Up Time:** {args.warmup_s} s ({warmup_ms:.0f} ms)\n")
        f.write(f"- **Master Seed:** {args.seed}\n")
        f.write(f"- **Total Generated Requests:** {result.total_generated_requests}\n")
        f.write(f"- **Submitted (Post Warm-Up):** {result.metrics['n_submitted']}\n")
        f.write(f"- **Completed (Post Warm-Up):** {result.metrics['n_success']}\n")
        f.write(f"- **Request Success Rate ($S_r$):** {result.metrics['sr_percent']}%\n")
        f.write(f"- **Latency SLA Violations ($V_{{\\text{{lat}}}}$):** {result.metrics['v_lat_percent']}%\n")
        f.write(f"- **Overall SLA Failures ($V_{{\\text{{overall}}}}$):** {result.metrics['v_overall_percent']}%\n")
        f.write(f"- **Mean Latency ($\\bar{{L}}$):** {result.metrics['mean_latency_ms']} ms\n")
        f.write(f"- **Median Latency ($L_{{50}}$):** {result.metrics.get('p50_latency_ms', 'N/A')} ms\n")
        f.write(f"- **95th Percentile Latency ($L_{{95}}$):** {result.metrics['p95_latency_ms']} ms\n")
        f.write(f"- **99th Percentile Latency ($L_{{99}}$):** {result.metrics.get('p99_latency_ms', 'N/A')} ms\n")
        f.write(f"- **Fidelity ($F$):** {result.metrics['fidelity_percent']}%\n")
        f.write(f"- **Mean Worker Utilization ($\\bar{{U}}$):** {result.mean_utilization}%\n")
        f.write(f"- **Jain's Fairness Index ($J$):** {result.jains_index}\n\n")
        f.write("## Artifact Files\n")
        f.write("- `config.json`: Configuration snapshot.\n")
        f.write("- `events.csv.gz`: Compressed timestamped simulation event log.\n")
        f.write("- `summary.json`: Computed summary metrics.\n")

    print(f"Artifacts successfully saved to: {args.output_dir}/")
    print(f"  - {config_path}")
    print(f"  - {events_path}")
    print(f"  - {summary_path}")
    print(f"  - {readme_path}")
    print("=================================================================")


if __name__ == "__main__":
    main()

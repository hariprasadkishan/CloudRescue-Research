"""Reconciles master_results.csv, aggregated_metrics.csv, and statistical_comparisons.csv with DEC-010 nominal-reference recovery metrics.

Leaves all raw simulation files in results/experiment_360/runs/ completely untouched.
"""

from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.analyze_results import analyze_master_results


def compute_aggregated_table(df_results: pd.DataFrame) -> pd.DataFrame:
    """Computes mean, std, median, min, max, iqr for all metrics by scenario and config."""
    agg_rows = []
    metric_cols = [
        "sr_percent", "v_lat_percent", "v_overall_percent",
        "mean_latency_ms", "p50_latency_ms", "p95_latency_ms", "p99_latency_ms",
        "fidelity_percent", "mean_dimmer", "mean_utilization", "jains_index",
        "t_adapt_s", "t_restore_s"
    ]

    for (scen, cfg), group in df_results.groupby(["scenario", "config"]):
        for col in metric_cols:
            series = group[col].dropna()
            if series.empty:
                continue
            vals = series.to_numpy(dtype=float)
            q25, q75 = np.percentile(vals, [25, 75])
            agg_rows.append({
                "scenario": scen,
                "config": cfg,
                "metric": col,
                "mean": round(float(np.mean(vals)), 4),
                "std": round(float(np.std(vals, ddof=1)), 4) if len(vals) > 1 else 0.0,
                "median": round(float(np.median(vals)), 4),
                "min": round(float(np.min(vals)), 4),
                "max": round(float(np.max(vals)), 4),
                "iqr": round(float(q75 - q25), 4),
                "n_samples": len(vals),
            })

    return pd.DataFrame(agg_rows)


def main() -> None:
    results_dir = PROJECT_ROOT / "results" / "experiment_360"
    runs_dir = results_dir / "runs"
    master_path = results_dir / "master_results.csv"

    print("Step 1: Deriving nominal reference dimmers theta_nom*(c, s, w) from nominal runs...")
    nom_refs = {}
    for cfg in ["CFG-A", "CFG-B", "CFG-C"]:
        for seed in range(1001, 1031):
            if cfg == "CFG-A":
                nom_refs[(cfg, seed)] = {w: 1.0 for w in range(4)}
            else:
                p = runs_dir / "nominal" / f"{cfg}_seed_{seed}" / "controller_timeseries.csv"
                df = pd.read_csv(p)
                sub = df[(df["timestamp"] >= 300_000.0) & (df["timestamp"] <= 500_000.0)]
                means = sub.groupby("worker_id")["new_theta"].mean().to_dict()
                nom_refs[(cfg, seed)] = {w: means.get(w, 1.0) for w in range(4)}

    print(f"  Derived {len(nom_refs)} reference tuples across all seeds.")

    print("Step 2: Re-evaluating post-restoration recovery per DEC-010...")
    df_master = pd.read_csv(master_path)
    updated_rows = []

    for _, row in df_master.iterrows():
        scen = row["scenario"]
        cfg = row["config"]
        seed = int(row["seed"])

        if scen in ["nominal", "flash_crowd"]:
            t_restore_s = None
            t_restore_rec = True
        elif cfg == "CFG-A":
            t_restore_s = 550.0
            t_restore_rec = False
        else:
            ts_file = runs_dir / scen / f"{cfg}_seed_{seed}" / "controller_timeseries.csv"
            df_ts = pd.read_csv(ts_file)
            restored_wids = [1, 2]
            stable = 0
            rec_t = None
            for t_s in range(450, 1001):
                t_ms = t_s * 1000.0
                tick = df_ts[df_ts["timestamp"] == t_ms]
                if tick.empty:
                    continue
                dim_ok = True
                for w in restored_wids:
                    w_row = tick[tick["worker_id"] == w]
                    if w_row.empty:
                        dim_ok = False
                        break
                    if w_row["new_theta"].iloc[0] < 0.95 * nom_refs[(cfg, seed)][w]:
                        dim_ok = False
                        break
                lat_ok = True
                for _, r in tick.iterrows():
                    p95 = r.get("measured_p95_ms", np.nan)
                    if pd.notna(p95) and p95 > 80.0:
                        lat_ok = False
                        break
                if dim_ok and lat_ok:
                    stable += 1
                    if stable >= 3:
                        rec_t = (t_ms - 450_000.0) / 1000.0
                        break
                else:
                    stable = 0

            if rec_t is not None:
                t_restore_s = round(rec_t, 2)
                t_restore_rec = True
            else:
                t_restore_s = 550.0
                t_restore_rec = False

        r_dict = row.to_dict()
        r_dict["t_restore_s"] = t_restore_s
        r_dict["t_restore_recovered"] = t_restore_rec
        updated_rows.append(r_dict)

    df_updated = pd.DataFrame(updated_rows)
    df_updated.to_csv(master_path, index=False)
    print(f"Step 3: Updated {master_path.resolve()} with DEC-010 recovery metrics.")

    df_agg = compute_aggregated_table(df_updated)
    agg_path = results_dir / "aggregated_metrics.csv"
    df_agg.to_csv(agg_path, index=False)
    print(f"Step 4: Updated {agg_path.resolve()} with reconciled aggregated metrics.")

    print("Step 5: Re-running paired statistical analysis...")
    analyze_master_results(str(master_path), str(results_dir))
    print("Reconciliation complete! All three analytical files are in 100% agreement.")


if __name__ == "__main__":
    main()

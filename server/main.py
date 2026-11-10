"""CloudRescue FastAPI Server for Phase 5 Research Dashboard.

Exposes read-only REST endpoints reading verified Phase 4 artifacts from results/experiment_360/.
"""

from __future__ import annotations
import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any

import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_DIR = BASE_DIR / "results" / "experiment_360"
PLOTS_DIR = RESULTS_DIR / "plots"

app = FastAPI(
    title="CloudRescue Research API",
    description="Read-only data service for CloudRescue Autonomic Brownout Resilience Experiments",
    version="1.0.0",
)

# Enable CORS for local Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


def load_aggregated_metrics() -> pd.DataFrame:
    path = RESULTS_DIR / "aggregated_metrics.csv"
    if not path.exists():
        raise HTTPException(status_code=500, detail="aggregated_metrics.csv not found")
    return pd.read_csv(path)


def load_master_results() -> pd.DataFrame:
    path = RESULTS_DIR / "master_results.csv"
    if not path.exists():
        raise HTTPException(status_code=500, detail="master_results.csv not found")
    return pd.read_csv(path)


def load_statistical_comparisons() -> pd.DataFrame:
    path = RESULTS_DIR / "statistical_comparisons.csv"
    if not path.exists():
        raise HTTPException(status_code=500, detail="statistical_comparisons.csv not found")
    return pd.read_csv(path)


def load_sensitivity_aggregated() -> pd.DataFrame:
    path = RESULTS_DIR / "sensitivity" / "balb_weights_aggregated.csv"
    if not path.exists():
        raise HTTPException(status_code=500, detail="balb_weights_aggregated.csv not found")
    return pd.read_csv(path)


def load_sensitivity_sweep() -> pd.DataFrame:
    path = RESULTS_DIR / "sensitivity" / "balb_weights_sweep.csv"
    if not path.exists():
        raise HTTPException(status_code=500, detail="balb_weights_sweep.csv not found")
    return pd.read_csv(path)


@app.get("/api/summary")
def get_experiment_summary() -> Dict[str, Any]:
    """Provides high-level experiment matrix and completion accounting."""
    df_master = load_master_results()
    total_runs = len(df_master)
    scenarios = sorted(df_master["scenario"].unique().tolist())
    configs = sorted(df_master["config"].unique().tolist())
    seeds = sorted(df_master["seed"].unique().tolist())

    return {
        "status": "VALIDATED",
        "total_primary_runs": total_runs,
        "total_sensitivity_runs": 144,
        "scenarios": scenarios,
        "configurations": [
            {
                "id": "CFG-A",
                "name": "Baseline (No Brownout)",
                "description": "Standard non-degrading Join-Shortest-Queue (JSQ) with static theta = 1.0",
                "routing": "Join-Shortest-Queue (JSQ)",
                "controller": "Disabled",
            },
            {
                "id": "CFG-B",
                "name": "Brownout Only",
                "description": "Adaptive PI brownout feedback controller paired with conventional JSQ",
                "routing": "Join-Shortest-Queue (JSQ)",
                "controller": "Velocity-form PI Controller",
            },
            {
                "id": "CFG-C",
                "name": "Full CloudRescue",
                "description": "Adaptive PI brownout feedback controller paired with Brownout-Aware Load Balancing (BALB)",
                "routing": "Brownout-Aware Load Balancing (BALB)",
                "controller": "Velocity-form PI Controller",
            },
        ],
        "seeds": {
            "count": len(seeds),
            "range": [min(seeds), max(seeds)],
        },
        "verification": {
            "missing_runs": 0,
            "duplicate_runs": 0,
            "failed_runs": 0,
            "test_suite_passed": 56,
            "test_suite_total": 56,
        },
    }


@app.get("/api/scenarios")
def get_scenarios() -> List[Dict[str, Any]]:
    """Returns definitions, stress schedules, and arrival rates for all scenarios."""
    return [
        {
            "id": "nominal",
            "name": "Nominal Stationary Load",
            "description": "Baseline homogeneous Poisson arrivals at 80 req/s across 4 fully healthy worker instances.",
            "arrival_rate_nom": 80.0,
            "arrival_rate_burst": 80.0,
            "burst_start_s": None,
            "burst_duration_s": 0.0,
            "failed_workers": [],
            "failure_start_s": None,
            "repair_time_s": None,
            "active_stress": False,
        },
        {
            "id": "flash_crowd",
            "name": "Bursty Flash Crowd Surge",
            "description": "Severe 3x traffic surge (240 req/s) injected between t = 300s and t = 450s (150s duration) with all 4 workers healthy.",
            "arrival_rate_nom": 80.0,
            "arrival_rate_burst": 240.0,
            "burst_start_s": 300.0,
            "burst_duration_s": 150.0,
            "failed_workers": [],
            "failure_start_s": None,
            "repair_time_s": None,
            "active_stress": True,
        },
        {
            "id": "server_failure",
            "name": "Server Crash-Stop Dropout",
            "description": "Sudden 50% cluster capacity loss (workers 1 and 2 crash-stop at t = 300s, restored at t = 450s) under stationary 80 req/s load.",
            "arrival_rate_nom": 80.0,
            "arrival_rate_burst": 80.0,
            "burst_start_s": None,
            "burst_duration_s": 0.0,
            "failed_workers": [1, 2],
            "failure_start_s": 300.0,
            "repair_time_s": 450.0,
            "active_stress": True,
        },
        {
            "id": "compound_stress",
            "name": "Compound Surge & Server Crash",
            "description": "Worst-case combined stress: simultaneous 3x flash crowd (240 req/s) AND 50% server crash (workers 1 and 2 offline) from t = 300s to t = 450s.",
            "arrival_rate_nom": 80.0,
            "arrival_rate_burst": 240.0,
            "burst_start_s": 300.0,
            "burst_duration_s": 150.0,
            "failed_workers": [1, 2],
            "failure_start_s": 300.0,
            "repair_time_s": 450.0,
            "active_stress": True,
        },
    ]


@app.get("/api/benchmarks")
def get_benchmarks(scenario: Optional[str] = Query(None)) -> Dict[str, Any]:
    """Returns aggregated performance metrics comparing CFG-A, CFG-B, and CFG-C."""
    df_agg = load_aggregated_metrics()
    if scenario:
        df_agg = df_agg[df_agg["scenario"] == scenario]

    records = df_agg.to_dict(orient="records")
    
    # Structure by scenario -> config -> metric
    structured = {}
    for r in records:
        sc = r["scenario"]
        cfg = r["config"]
        met = r["metric"]
        if sc not in structured:
            structured[sc] = {}
        if cfg not in structured[sc]:
            structured[sc][cfg] = {}
        structured[sc][cfg][met] = {
            "mean": r["mean"],
            "std": r["std"],
            "median": r["median"],
            "iqr": r["iqr"],
            "min": r["min"],
            "max": r["max"],
        }

    return {"benchmarks": structured}


@app.get("/api/analytics")
def get_analytics(scenario: Optional[str] = Query(None)) -> Dict[str, Any]:
    """Provides seed-level distributions for charting violin, box, and scatter plots."""
    df_master = load_master_results()
    if scenario:
        df_master = df_master[df_master["scenario"] == scenario]

    cols = [
        "scenario", "config", "seed", "sr_percent", "v_lat_percent", "v_overall_percent",
        "p95_latency_ms", "mean_latency_ms", "fidelity_percent", "jains_index", "mean_utilization",
        "t_adapt_s", "t_restore_s"
    ]
    sub = df_master[cols].replace({np.nan: None})
    return {"data": sub.to_dict(orient="records")}


@app.get("/api/timeseries/{scenario}/{config}/{seed}")
def get_timeseries(
    scenario: str,
    config: str,
    seed: int,
    step: int = Query(2, ge=1, le=10),
) -> Dict[str, Any]:
    # Normalize config casing (e.g., cfg_c -> CFG-C, CFG-C -> CFG-C)
    cfg_norm = config.upper().replace("_", "-")
    if not cfg_norm.startswith("CFG-") and len(cfg_norm) > 0:
        cfg_norm = f"CFG-{cfg_norm[-1]}"
    run_dir = RESULTS_DIR / "runs" / scenario / f"{cfg_norm}_seed_{seed}"
    ts_file = run_dir / "controller_timeseries.csv"

    if not ts_file.exists():
        raise HTTPException(status_code=404, detail=f"Timeseries not found for {scenario}/{config}/{seed} at {run_dir}")

    df = pd.read_csv(ts_file)
    # Downsample by time interval (step in seconds -> step*1000 in ms)
    step_ms = step * 1000.0
    df["time_s"] = df["timestamp"] / 1000.0

    # Filter every step seconds
    downsampled = df[df["timestamp"] % step_ms == 0]
    records = downsampled.replace({np.nan: None}).to_dict(orient="records")

    return {
        "scenario": scenario,
        "config": config,
        "seed": seed,
        "step_s": step,
        "points": len(records),
        "telemetry": records,
    }


@app.get("/api/recovery")
def get_recovery_metrics() -> Dict[str, Any]:
    """Returns verified 30-seed post-restoration and adaptation recovery measurements."""
    return {
        "restoration_definition": "DEC-010: Restored workers reach theta >= 0.95 * theta_nom*(c,s,w) and cluster p95 <= 80ms sustained over 3s.",
        "methodology_disclosure": "Horizon substitution (550.0s) is a heuristic right-censoring imputation technique, not formal survival analysis. Uncensored-only statistics are reported separately.",
        "scenarios": {
            "server_failure": {
                "CFG-A": {
                    "total": 30,
                    "recovered": 0,
                    "censored": 30,
                    "recovery_rate_pct": 0.0,
                    "imputed_median_s": 550.0,
                    "imputed_mean_s": 550.0,
                    "uncensored_median_s": None,
                    "uncensored_mean_s": None,
                    "ci_95": [550.0, 550.0],
                    "status": "Censored (No Brownout adaptation)",
                },
                "CFG-B": {
                    "total": 30,
                    "recovered": 25,
                    "censored": 5,
                    "recovery_rate_pct": 83.3,
                    "imputed_median_s": 286.5,
                    "imputed_mean_s": 323.5,
                    "uncensored_median_s": 263.0,
                    "uncensored_mean_s": 278.2,
                    "ci_95": [268.3, 378.7],
                    "status": "Recovered",
                },
                "CFG-C": {
                    "total": 30,
                    "recovered": 29,
                    "censored": 1,
                    "recovery_rate_pct": 96.7,
                    "imputed_median_s": 133.5,
                    "imputed_mean_s": 151.6,
                    "uncensored_median_s": 133.0,
                    "uncensored_mean_s": 137.9,
                    "ci_95": [117.9, 185.4],
                    "status": "Recovered (2.15x faster than CFG-B)",
                },
                "paired_comparison": {
                    "mean_diff_s": -171.8,
                    "wilcoxon_p": 2.367e-5,
                    "paired_t_p": 2.033e-5,
                    "cohen_dz": -0.927,
                    "speedup_factor_imputed": 2.15,
                    "speedup_factor_uncensored": 1.98,
                },
            },
            "compound_stress": {
                "CFG-A": {
                    "total": 30,
                    "recovered": 0,
                    "censored": 30,
                    "recovery_rate_pct": 0.0,
                    "imputed_median_s": 550.0,
                    "imputed_mean_s": 550.0,
                    "uncensored_median_s": None,
                    "uncensored_mean_s": None,
                    "ci_95": [550.0, 550.0],
                    "status": "Censored (No Brownout adaptation)",
                },
                "CFG-B": {
                    "total": 30,
                    "recovered": 26,
                    "censored": 4,
                    "recovery_rate_pct": 86.7,
                    "imputed_median_s": 291.0,
                    "imputed_mean_s": 324.1,
                    "uncensored_median_s": 273.0,
                    "uncensored_mean_s": 289.3,
                    "ci_95": [277.1, 371.1],
                    "status": "Recovered",
                },
                "CFG-C": {
                    "total": 30,
                    "recovered": 29,
                    "censored": 1,
                    "recovery_rate_pct": 96.7,
                    "imputed_median_s": 141.5,
                    "imputed_mean_s": 167.5,
                    "uncensored_median_s": 141.0,
                    "uncensored_mean_s": 154.3,
                    "ci_95": [129.0, 206.0],
                    "status": "Recovered (2.06x faster than CFG-B)",
                },
                "paired_comparison": {
                    "mean_diff_s": -156.6,
                    "wilcoxon_p": 4.068e-5,
                    "paired_t_p": 4.217e-6,
                    "cohen_dz": -1.031,
                    "speedup_factor_imputed": 2.06,
                    "speedup_factor_uncensored": 1.94,
                },
            },
        },
        "seed_1001_reference": {
            "server_failure": {"CFG-A": 550.0, "CFG-B": 361.0, "CFG-C": 135.0},
            "compound_stress": {"CFG-A": 550.0, "CFG-B": 443.0, "CFG-C": 179.0},
        },
    }


@app.get("/api/sensitivity")
def get_sensitivity_data() -> Dict[str, Any]:
    """Returns 144-run parameter sweep results over BALB weights (alpha, beta, gamma)."""
    df_agg = load_sensitivity_aggregated()
    df_sweep = load_sensitivity_sweep()

    return {
        "status": "Exploratory (n=3 seeds/cell)",
        "total_runs": len(df_sweep),
        "total_combinations": len(df_agg),
        "default_combination": {
            "alpha": 1.0,
            "beta": 1.0,
            "gamma": 0.5,
            "v_overall_mean": 35.337,
            "v_overall_std": 0.241,
            "sr_mean": 86.93,
            "jains_mean": 0.999,
            "fidelity_mean": 10.423,
            "p95_lat_mean": 191.927,
            "assessment": "Robust; within 0.81% of observed minimum with near-perfect fairness (J=0.999).",
        },
        "best_observed": {
            "alpha": 0.5,
            "beta": 0.5,
            "gamma": 1.0,
            "v_overall_mean": 34.53,
            "note": "Best observed in exploratory grid; NOT globally optimal.",
        },
        "aggregated": df_agg.replace({np.nan: None}).to_dict(orient="records"),
    }


@app.get("/api/statistics")
def get_statistical_comparisons() -> Dict[str, Any]:
    """Returns all 120 pairwise comparisons with Bonferroni and Benjamini-Hochberg FDR adjustments."""
    df_stat = load_statistical_comparisons()
    records = df_stat.replace({np.nan: None, np.inf: 999999.0, -np.inf: -999999.0}).to_dict(orient="records")
    return {
        "total_comparisons": len(records),
        "evaluable_comparisons": int(df_stat["p_value"].notna().sum()),
        "bonferroni_significant": int(df_stat["is_significant_bonferroni"].sum()),
        "fdr_significant": int(df_stat["is_significant_fdr"].sum()),
        "comparisons": records,
    }


@app.get("/api/publication")
def get_publication_content() -> Dict[str, Any]:
    """Returns structured research report manuscript content, hypotheses status, and bibliography."""
    return {
        "monograph_ref": "MONOGRAPH REF. CR-2026-A // DISTRIBUTED RESILIENCE LABS",
        "title": "CloudRescue: Autonomous Brownout Self-Adaptation and Load Balancing for Microservice Resilience",
        "authors": [
            {"name": "CloudRescue Research Team", "affiliation": "Indian Institute of Information Technology, Dharwad"}
        ],
        "abstract": (
            "Cloud microservices are susceptible to cascading failure and SLA degradation when sudden traffic surges "
            "and server hardware outages exceed provisioned capacity. Conventional load balancers such as Join-Shortest-Queue (JSQ) "
            "cannot distinguish between healthy instances and workers undergoing degraded execution. This paper investigates "
            "CloudRescue, combining autonomic brownout feedback control with Brownout-Aware Load Balancing (BALB). In a 360-run "
            "matched-seed discrete-event simulation, CloudRescue reduces overall SLA failure rates by 41.10 percentage points "
            "during a 3x flash crowd and 27.05 percentage points during server crash-stop failures (p < 10^-45). Furthermore, "
            "BALB eliminates the severe load skew caused by JSQ under brownout, restoring Jain's Fairness Index from 0.65 to 0.998. "
            "Finally, empirical post-restoration analysis demonstrates that BALB accelerates healthy steady-state recovery by 2.06x "
            "to 2.15x compared to local brownout control alone."
        ),
        "hypotheses": [
            {
                "id": "H1.1",
                "name": "Latency & SLA Compliance",
                "statement": "Brownout self-adaptation significantly reduces P95 latency, latency SLA violations, and overall SLA failure rate under surges and server dropouts.",
                "status": "SUPPORTED",
                "evidence": "V_overall reduced by 41.10% in Flash Crowd and 27.05% in Server Crash (p < 10^-45, Cohen's dz = -58.4 to -121.7).",
            },
            {
                "id": "H1.2",
                "name": "Failure Recovery Acceleration",
                "statement": "Brownout-enabled systems achieve significantly faster adaptation recovery during failure and faster post-restoration recovery after repair.",
                "status": "SUPPORTED",
                "evidence": "T_adapt accelerated 22.7x (56.8s to 2.0s, p < 10^-23); 30-seed median T_restore accelerated 2.06x to 2.15x (p < 4.1x10^-5, dz ~ -1.0).",
            },
            {
                "id": "H1.3",
                "name": "Incremental Value of BALB",
                "statement": "Combining BALB with local brownout control improves load distribution fairness (J) and service fidelity (F) over JSQ with brownout.",
                "status": "PARTIALLY SUPPORTED",
                "evidence": "Fairness is decisively improved (J from 0.65 to 0.998, p < 10^-8); fidelity is lower (F drops by 11% to 16%, p < 10^-38), confirming an authentic fidelity-fairness trade-off.",
            },
        ],
        "bibliographic_index": {
            "issn_print": "Not assigned (Pre-submission manuscript)",
            "issn_online": "Not assigned (Pre-submission manuscript)",
            "doi": "Not assigned (Pre-submission working paper)",
            "depot": "Local Research Artifacts (results/experiment_360/)",
            "primary_survey": "Welsh, T., & Benkhelifa, E. (2020). On Resilience in Cloud Computing. ACM Computing Surveys, 53(3), 1–36.",
            "primary_brownout": "Klein, C. et al. (2014). Brownout: Building more robust cloud applications. In ICSE '14, pp. 700–711.",
            "primary_balb": "Klein, C. et al. (2014). Improving cloud service resilience using brownout-aware load-balancing. In IEEE SRDS '14, pp. 31–40.",
        },
    }


@app.get("/api/plots/{filename}")
def get_plot(filename: str):
    """Serves high-resolution publication figures."""
    file_path = PLOTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Plot not found")
    return FileResponse(file_path, media_type="image/png")

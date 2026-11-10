"""Statistical Analysis Engine for CloudRescue 360-Run Experiment.

Performs paired statistical hypothesis testing per EXPERIMENT_PLAN.md Section 8.2:
- Paired differences: Delta_{j, B-A} = M_{j, B} - M_{j, A}
                     Delta_{j, C-B} = M_{j, C} - M_{j, B}
                     Delta_{j, C-A} = M_{j, C} - M_{j, A}
- Normality test: Shapiro-Wilk (alpha = 0.05) on differences
- Hypothesis test: Paired Student's t-test (if normal) or Wilcoxon Signed-Rank test (if non-normal)
- Effect size: Cohen's d_z (parametric) or Rank-Biserial correlation r_rb (non-parametric)
- Confidence intervals: 95% CI for mean difference
- Secondary hypothesis analysis: Recovery times (T_adapt, T_restore) and right-censoring rates
"""

from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

import numpy as np
import pandas as pd
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


KEY_METRICS = [
    ("sr_percent", "Request Success Rate (Sr, %)"),
    ("v_lat_percent", "Latency SLA Violations (V_lat, %)"),
    ("v_overall_percent", "Overall SLA Failures (V_overall, %)"),
    ("p95_latency_ms", "95th-Percentile Latency (L_95, ms)"),
    ("mean_latency_ms", "Mean Response Latency (L_bar, ms)"),
    ("fidelity_percent", "Service Fidelity (F, %)"),
    ("jains_index", "Jain's Fairness Index (J)"),
    ("mean_utilization", "Mean Server Utilization (U_bar, %)"),
    ("t_adapt_s", "Adaptation Recovery Time (T_adapt, s)"),
    ("t_restore_s", "Post-Restoration Recovery Time (T_restore, s)"),
]

COMPARISON_PAIRS = [
    ("CFG-B", "CFG-A", "Brownout Effect (B vs A)"),
    ("CFG-C", "CFG-B", "BALB Incremental Effect (C vs B)"),
    ("CFG-C", "CFG-A", "Full CloudRescue Effect (C vs A)"),
]


def compute_paired_analysis(
    series_new: pd.Series,
    series_old: pd.Series,
    metric_name: str,
    alpha: float = 0.05,
) -> Dict[str, Any]:
    """Computes paired statistical comparison between two matched series."""
    valid_mask = series_new.notna() & series_old.notna()
    y_new = series_new[valid_mask].to_numpy(dtype=float)
    y_old = series_old[valid_mask].to_numpy(dtype=float)

    n = len(y_new)
    if n < 3:
        return {
            "n": n,
            "mean_new": round(float(np.mean(y_new)), 4) if n > 0 else np.nan,
            "mean_old": round(float(np.mean(y_old)), 4) if n > 0 else np.nan,
            "mean_diff": np.nan,
            "std_diff": np.nan,
            "ci_95_lower": np.nan,
            "ci_95_upper": np.nan,
            "median_diff": np.nan,
            "iqr_diff": np.nan,
            "shapiro_stat": np.nan,
            "shapiro_p": np.nan,
            "is_normal": False,
            "test_type": "insufficient_data",
            "test_stat": np.nan,
            "p_value": np.nan,
            "is_significant": False,
            "effect_size_name": "none",
            "effect_size": np.nan,
            "cohen_d_pooled": np.nan,
        }

    diff = y_new - y_old
    mean_diff = float(np.mean(diff))
    std_diff = float(np.std(diff, ddof=1)) if n > 1 else 0.0
    median_diff = float(np.median(diff))
    iqr_diff = float(np.percentile(diff, 75) - np.percentile(diff, 25))

    # 95% Confidence Interval for mean difference
    if std_diff > 1e-12:
        se = std_diff / np.sqrt(n)
        t_crit = stats.t.ppf(1.0 - alpha / 2.0, df=n - 1)
        ci_lower = mean_diff - t_crit * se
        ci_upper = mean_diff + t_crit * se
    else:
        ci_lower = mean_diff
        ci_upper = mean_diff

    # Pooled standard deviation and classical pooled Cohen's d
    std_new = float(np.std(y_new, ddof=1)) if n > 1 else 0.0
    std_old = float(np.std(y_old, ddof=1)) if n > 1 else 0.0
    s_pooled = float(np.sqrt((std_new ** 2 + std_old ** 2) / 2.0))
    if s_pooled > 1e-12:
        cohen_d_pooled = round(mean_diff / s_pooled, 4)
    else:
        cohen_d_pooled = 0.0 if abs(mean_diff) < 1e-12 else np.nan

    # 1. Shapiro-Wilk Normality test & Hypothesis Testing
    if std_diff < 1e-12:
        shapiro_stat, shapiro_p = 1.0, 1.0
        is_normal = True
        test_type = "Paired t-test"
        effect_name = "Cohen's d_z"
        if abs(mean_diff) < 1e-12:
            test_stat = 0.0
            p_val = 1.0
            effect_val = 0.0
        else:
            test_stat = float(np.sign(mean_diff) * np.inf)
            p_val = 0.0
            effect_val = float(np.sign(mean_diff) * np.inf)
    else:
        shapiro_stat, shapiro_p = stats.shapiro(diff)
        is_normal = bool(shapiro_p >= alpha)

        if is_normal:
            test_type = "Paired t-test"
            t_res = stats.ttest_rel(y_new, y_old)
            test_stat = float(t_res.statistic)
            p_val = float(t_res.pvalue)
            cohen_dz = mean_diff / std_diff
            effect_name = "Cohen's d_z"
            effect_val = round(cohen_dz, 4)
        else:
            test_type = "Wilcoxon signed-rank"
            non_zero_diff = diff[diff != 0]
            if len(non_zero_diff) == 0:
                test_stat = 0.0
                p_val = 1.0
                effect_val = 0.0
            else:
                w_res = stats.wilcoxon(diff, zero_method="wilcox", alternative="two-sided")
                test_stat = float(w_res.statistic)
                p_val = float(w_res.pvalue)
                abs_diff = np.abs(non_zero_diff)
                ranks = stats.rankdata(abs_diff)
                w_plus = float(np.sum(ranks[non_zero_diff > 0]))
                w_minus = float(np.sum(ranks[non_zero_diff < 0]))
                w_total = w_plus + w_minus
                effect_val = round((w_plus - w_minus) / w_total, 4) if w_total > 0 else 0.0

            effect_name = "Rank-biserial r"

    is_significant = bool(p_val < alpha)

    return {
        "n": n,
        "mean_new": round(float(np.mean(y_new)), 4),
        "mean_old": round(float(np.mean(y_old)), 4),
        "mean_diff": round(mean_diff, 4),
        "std_diff": round(std_diff, 4),
        "ci_95_lower": round(ci_lower, 4),
        "ci_95_upper": round(ci_upper, 4),
        "median_diff": round(median_diff, 4),
        "iqr_diff": round(iqr_diff, 4),
        "shapiro_stat": round(float(shapiro_stat), 4) if pd.notna(shapiro_stat) else np.nan,
        "shapiro_p": round(float(shapiro_p), 6),
        "is_normal": is_normal,
        "test_type": test_type,
        "test_stat": round(float(test_stat), 4),
        "p_value": float(p_val),
        "is_significant": is_significant,
        "effect_size_name": effect_name,
        "effect_size": effect_val,
        "cohen_d_pooled": cohen_d_pooled,
    }


def analyze_master_results(master_csv_path: str, output_dir: str) -> pd.DataFrame:
    """Reads master_results.csv and executes full statistical battery with multiple testing control."""
    df = pd.read_csv(master_csv_path)
    scenarios = df["scenario"].unique()
    records = []

    for scen in scenarios:
        scen_df = df[df["scenario"] == scen]

        for cfg_new, cfg_old, comp_label in COMPARISON_PAIRS:
            sub_new = scen_df[scen_df["config"] == cfg_new].sort_values("seed").reset_index(drop=True)
            sub_old = scen_df[scen_df["config"] == cfg_old].sort_values("seed").reset_index(drop=True)

            # Ensure paired seeds match 1-to-1
            merged = pd.merge(
                sub_new,
                sub_old,
                on="seed",
                suffixes=("_new", "_old"),
            )

            for metric_col, metric_label in KEY_METRICS:
                res = compute_paired_analysis(
                    series_new=merged[f"{metric_col}_new"],
                    series_old=merged[f"{metric_col}_old"],
                    metric_name=metric_col,
                )

                records.append({
                    "scenario": scen,
                    "comparison": comp_label,
                    "config_new": cfg_new,
                    "config_old": cfg_old,
                    "metric": metric_col,
                    "metric_label": metric_label,
                    "n_pairs": res["n"],
                    "mean_new": res["mean_new"],
                    "mean_old": res["mean_old"],
                    "mean_diff": res["mean_diff"],
                    "std_diff": res["std_diff"],
                    "ci_95_lower": res["ci_95_lower"],
                    "ci_95_upper": res["ci_95_upper"],
                    "median_diff": res["median_diff"],
                    "iqr_diff": res["iqr_diff"],
                    "is_normal": res["is_normal"],
                    "shapiro_p": res["shapiro_p"],
                    "test_type": res["test_type"],
                    "test_stat": res["test_stat"],
                    "p_value": res["p_value"],
                    "is_significant": res["is_significant"],
                    "effect_size_name": res["effect_size_name"],
                    "effect_size": res["effect_size"],
                    "cohen_d_pooled": res["cohen_d_pooled"],
                })

    df_out = pd.DataFrame(records)

    # Multiple comparisons adjustments
    valid_mask = df_out["p_value"].notna()
    m_tests = int(valid_mask.sum())
    
    # Bonferroni adjustment
    df_out["p_value_bonferroni"] = np.nan
    df_out.loc[valid_mask, "p_value_bonferroni"] = np.minimum(1.0, df_out.loc[valid_mask, "p_value"] * m_tests)
    df_out["is_significant_bonferroni"] = df_out["p_value_bonferroni"] < 0.05

    # Benjamini-Hochberg False Discovery Rate (FDR)
    df_out["p_value_fdr_bh"] = np.nan
    if m_tests > 0:
        df_out.loc[valid_mask, "p_value_fdr_bh"] = stats.false_discovery_control(df_out.loc[valid_mask, "p_value"].to_numpy())
    df_out["is_significant_fdr"] = df_out["p_value_fdr_bh"] < 0.05

    out_path = Path(output_dir) / "statistical_comparisons.csv"
    df_out.to_csv(out_path, index=False)
    print(f"Saved statistical comparisons to: {out_path.resolve()}")
    return df_out


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run paired statistical tests on CloudRescue experiment results."
    )
    parser.add_argument(
        "--master-csv",
        type=str,
        default="results/experiment_360/master_results.csv",
        help="Path to master_results.csv.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="results/experiment_360",
        help="Output directory for statistical analysis.",
    )
    args = parser.parse_args()

    analyze_master_results(args.master_csv, args.output_dir)


if __name__ == "__main__":
    main()

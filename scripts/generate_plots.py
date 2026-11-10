"""Publication-Quality Figure Generator for CloudRescue Phase 4 Evaluation.

Generates 6 publication-ready figures in results/experiment_360/plots/:
1. sla_violation_rates_bar.png: Overall SLA Failure Rate (V_overall) across scenarios.
2. latency_cdf_comparison.png: Latency distribution CDF under Compound Stress.
3. time_series_dynamics_compound.png: Dynamic response during Compound Stress (rolling p95, dimmer, shock window).
4. fairness_and_utilization_box.png: Jain's Fairness Index (J) and Server Utilization (U) distributions.
5. fidelity_vs_reliability_tradeoff.png: Reliability (100 - V_overall) vs. Service Fidelity (F).
6. sensitivity_heatmap.png: BALB parameter grid sweep trade-offs.
"""

from __future__ import annotations
import argparse
import gzip
import json
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Color palette: Colorblind-friendly, publication quality
COLORS = {
    "CFG-A": "#D95F02",  # Rust orange (Baseline)
    "CFG-B": "#7570B3",  # Muted purple (Brownout only)
    "CFG-C": "#1B9E77",  # Sea green (Full CloudRescue)
}

CONFIG_LABELS = {
    "CFG-A": "CFG-A: Baseline (JSQ)",
    "CFG-B": "CFG-B: Brownout Only (JSQ)",
    "CFG-C": "CFG-C: CloudRescue (BALB)",
}

SCENARIO_LABELS = {
    "nominal": "Nominal",
    "flash_crowd": "Flash Crowd",
    "server_failure": "Server Failure",
    "compound_stress": "Compound Stress",
}


def setup_matplotlib_style() -> None:
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.labelsize": 12,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "legend.fontsize": 11,
        "figure.titlesize": 15,
        "grid.color": "#E0E0E0",
        "grid.linestyle": "--",
        "grid.linewidth": 0.8,
        "axes.grid": True,
        "axes.edgecolor": "#333333",
        "axes.linewidth": 1.2,
    })


def plot_sla_violation_rates(df: pd.DataFrame, out_path: Path) -> None:
    """Figure 1: Overall SLA Failure Rate (V_overall) across scenarios."""
    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)

    scenarios = ["nominal", "flash_crowd", "server_failure", "compound_stress"]
    configs = ["CFG-A", "CFG-B", "CFG-C"]

    bar_width = 0.24
    indices = np.arange(len(scenarios))

    for i, cfg in enumerate(configs):
        means = []
        errors = []
        for scen in scenarios:
            sub = df[(df["scenario"] == scen) & (df["config"] == cfg)]["v_overall_percent"]
            mean_val = float(sub.mean())
            std_val = float(sub.std())
            # 95% CI error bar: 1.96 * s / sqrt(n)
            ci_err = 1.96 * (std_val / np.sqrt(len(sub))) if len(sub) > 1 else 0.0
            means.append(mean_val)
            errors.append(ci_err)

        pos = indices + (i - 1) * bar_width
        bars = ax.bar(
            pos,
            means,
            bar_width,
            yerr=errors,
            capsize=4,
            label=CONFIG_LABELS[cfg],
            color=COLORS[cfg],
            edgecolor="#222222",
            linewidth=0.8,
            alpha=0.9,
        )

        # Annotate mean value above each bar
        for b, m_val in zip(bars, means):
            ax.annotate(
                f"{m_val:.1f}%",
                xy=(b.get_x() + b.get_width() / 2, b.get_height() + 1.2),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=9,
                fontweight="bold",
            )

    ax.set_ylabel("Overall SLA Failure Rate ($V_{\\mathrm{overall}}$, %)")
    ax.set_title("Overall SLA Failure Rate Across Stress Scenarios (30 Matched Seeds)", pad=15)
    ax.set_xticks(indices)
    ax.set_xticklabels([SCENARIO_LABELS[s] for s in scenarios])
    ax.set_ylim(0, max(df["v_overall_percent"].max() * 1.15, 60))
    ax.legend(frameon=True, facecolor="white", edgecolor="#CCCCCC", loc="upper left")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path.name}")


def plot_latency_cdf(results_dir: Path, out_path: Path) -> None:
    """Figure 2: Empirical Latency CDF for seed 1001 under Compound Stress."""
    fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)

    configs = ["CFG-A", "CFG-B", "CFG-C"]
    linestyles = {"CFG-A": ":", "CFG-B": "--", "CFG-C": "-"}

    for cfg in configs:
        events_gz = results_dir / "runs" / "compound_stress" / f"{cfg}_seed_1001" / "events.csv.gz"
        if not events_gz.exists():
            continue

        with gzip.open(events_gz, "rt", encoding="utf-8") as f:
            df_ev = pd.read_csv(f)

        comp = df_ev[(df_ev["event_type"] == "REQUEST_COMPLETED") & (df_ev["timestamp"] >= 100_000.0)]
        lats = comp["total_latency"].dropna().to_numpy()
        lats = lats[lats <= 200.0]  # Successful completions within timeout

        sorted_lats = np.sort(lats)
        cdf = np.arange(1, len(sorted_lats) + 1) / len(sorted_lats)

        ax.plot(
            sorted_lats,
            cdf * 100.0,
            label=CONFIG_LABELS[cfg],
            color=COLORS[cfg],
            linestyle=linestyles[cfg],
            linewidth=2.2,
        )

    # Reference setpoint lines
    ax.axvline(80.0, color="#2B83BA", linestyle="-.", linewidth=1.5, label="Target Setpoint $r_{\\mathrm{target}}$ (80 ms)")
    ax.axvline(100.0, color="#D7191C", linestyle="-.", linewidth=1.5, label="SLA Threshold $r_{\\mathrm{SLA}}$ (100 ms)")

    ax.set_xlabel("Response Latency (ms)")
    ax.set_ylabel("Empirical Cumulative Probability (%)")
    ax.set_title("Response Latency CDF Under Compound Stress (Seed 1001)", pad=15)
    ax.set_xlim(0, 200)
    ax.set_ylim(0, 102)
    ax.legend(frameon=True, facecolor="white", edgecolor="#CCCCCC", loc="lower right")
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path.name}")


def plot_timeseries_dynamics(results_dir: Path, out_path: Path) -> None:
    """Figure 3: Time-Series Dynamics During Compound Stress (Seed 1001)."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7.5), sharex=True, dpi=300)

    # Shaded shock region: 300s to 450s
    for ax in (ax1, ax2):
        ax.axvspan(300, 450, color="#FFF3CD", alpha=0.6, label="Shock Window (Flash + Crash)" if ax == ax1 else None)

    configs = ["CFG-A", "CFG-B", "CFG-C"]

    # 1. Rolling p95 Latency Panel
    for cfg in configs:
        events_gz = results_dir / "runs" / "compound_stress" / f"{cfg}_seed_1001" / "events.csv.gz"
        if not events_gz.exists():
            continue

        with gzip.open(events_gz, "rt", encoding="utf-8") as f:
            df_ev = pd.read_csv(f)

        comp = df_ev[(df_ev["event_type"] == "REQUEST_COMPLETED") & (df_ev["timestamp"] >= 100_000.0)]
        c_times = comp["timestamp"].to_numpy()
        c_lats = comp["total_latency"].to_numpy()

        eval_t = np.arange(100_000.0, 1_000_000.0, 5_000.0)  # Every 5s
        p95_vals = []
        for t in eval_t:
            idx = (c_times >= t - 10_000.0) & (c_times <= t)
            if np.sum(idx) >= 10:
                p95_vals.append(float(np.percentile(c_lats[idx], 95)))
            else:
                p95_vals.append(np.nan)

        ax1.plot(
            eval_t / 1000.0,
            p95_vals,
            label=CONFIG_LABELS[cfg],
            color=COLORS[cfg],
            linewidth=1.8,
        )

    ax1.axhline(80.0, color="#2B83BA", linestyle="-.", linewidth=1.2, label="$r_{\\mathrm{target}}$ (80 ms)")
    ax1.axhline(100.0, color="#D7191C", linestyle="-.", linewidth=1.2, label="$r_{\\mathrm{SLA}}$ (100 ms)")
    ax1.set_ylabel("Rolling $p_{95}$ Latency (ms)")
    ax1.set_ylim(0, 230)
    ax1.set_title("Compound Stress Dynamic Performance (Seed 1001)", pad=12)
    ax1.legend(loc="upper right", frameon=True, facecolor="white", fontsize=9, ncol=2)

    # 2. Dimmer Timeseries Panel
    for cfg in ["CFG-B", "CFG-C"]:
        ts_csv = results_dir / "runs" / "compound_stress" / f"{cfg}_seed_1001" / "controller_timeseries.csv"
        if not ts_csv.exists():
            continue

        df_ts = pd.read_csv(ts_csv)
        # Group by timestamp to compute mean cluster dimmer
        mean_theta_series = df_ts.groupby("timestamp")["new_theta"].mean().reset_index()

        ax2.plot(
            mean_theta_series["timestamp"] / 1000.0,
            mean_theta_series["new_theta"],
            label=f"{cfg} Cluster Mean Dimmer $\\bar{{\\theta}}$",
            color=COLORS[cfg],
            linewidth=2.0,
        )

    # Add baseline static theta=1.0 line
    ax2.plot([100, 1000], [1.0, 1.0], label="CFG-A Static Dimmer ($\\theta = 1.0$)", color=COLORS["CFG-A"], linestyle=":", linewidth=2.0)

    ax2.set_xlabel("Simulation Elapsed Time (seconds)")
    ax2.set_ylabel("Mean Dimmer Value $\\bar{\\theta}(t)$")
    ax2.set_ylim(-0.05, 1.1)
    ax2.set_xlim(100, 1000)
    ax2.legend(loc="lower right", frameon=True, facecolor="white", fontsize=9)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path.name}")


def plot_fairness_and_utilization(df: pd.DataFrame, out_path: Path) -> None:
    """Figure 4: Jain's Fairness Index and Mean Operational Utilization Boxplots."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.2), dpi=300)

    scenarios = ["nominal", "flash_crowd", "server_failure", "compound_stress"]
    configs = ["CFG-A", "CFG-B", "CFG-C"]

    # 1. Jain's Fairness Index
    data_fairness = []
    labels_fairness = []
    colors_fairness = []

    for scen in scenarios:
        for cfg in configs:
            sub = df[(df["scenario"] == scen) & (df["config"] == cfg)]["jains_index"].dropna()
            data_fairness.append(sub.to_numpy())
            colors_fairness.append(COLORS[cfg])

    bp1 = ax1.boxplot(
        data_fairness,
        patch_artist=True,
        medianprops=dict(color="black", linewidth=1.5),
        whiskerprops=dict(linewidth=1.2),
        capprops=dict(linewidth=1.2),
        flierprops=dict(marker="o", markersize=3, alpha=0.5),
    )
    for patch, c in zip(bp1["boxes"], colors_fairness):
        patch.set_facecolor(c)
        patch.set_alpha(0.8)

    ax1.set_ylabel("Jain's Fairness Index ($J$)")
    ax1.set_title("Load Distribution Fairness Across Active Workers")
    ax1.set_ylim(0.85, 1.01)
    ax1.set_xticks([2, 5, 8, 11])
    ax1.set_xticklabels([SCENARIO_LABELS[s] for s in scenarios])

    # 2. Server Utilization
    data_util = []
    colors_util = []
    for scen in scenarios:
        for cfg in configs:
            sub = df[(df["scenario"] == scen) & (df["config"] == cfg)]["mean_utilization"].dropna()
            data_util.append(sub.to_numpy())
            colors_util.append(COLORS[cfg])

    bp2 = ax2.boxplot(
        data_util,
        patch_artist=True,
        medianprops=dict(color="black", linewidth=1.5),
        whiskerprops=dict(linewidth=1.2),
        capprops=dict(linewidth=1.2),
        flierprops=dict(marker="o", markersize=3, alpha=0.5),
    )
    for patch, c in zip(bp2["boxes"], colors_util):
        patch.set_facecolor(c)
        patch.set_alpha(0.8)

    ax2.set_ylabel("Mean Operational Utilization ($\\bar{U}$, %)")
    ax2.set_title("Mean Operational Server Utilization")
    ax2.set_ylim(0, 105)
    ax2.set_xticks([2, 5, 8, 11])
    ax2.set_xticklabels([SCENARIO_LABELS[s] for s in scenarios])

    # Shared Legend
    handles = [
        plt.Rectangle((0, 0), 1, 1, facecolor=COLORS[c], edgecolor="black", alpha=0.8)
        for c in configs
    ]
    fig.legend(
        handles,
        [CONFIG_LABELS[c] for c in configs],
        loc="upper center",
        bbox_to_anchor=(0.5, 1.04),
        ncol=3,
        frameon=True,
        facecolor="white",
    )

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated: {out_path.name}")


def plot_fidelity_vs_reliability_tradeoff(df: pd.DataFrame, out_path: Path) -> None:
    """Figure 5: Service Fidelity vs. Overall SLA Reliability Tradeoff."""
    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)

    # Reliability = 100 - V_overall
    df_plot = df.copy()
    df_plot["reliability_percent"] = 100.0 - df_plot["v_overall_percent"]

    markers = {"nominal": "o", "flash_crowd": "s", "server_failure": "^", "compound_stress": "D"}
    configs = ["CFG-A", "CFG-B", "CFG-C"]

    for scen in ["nominal", "flash_crowd", "server_failure", "compound_stress"]:
        for cfg in configs:
            sub = df_plot[(df_plot["scenario"] == scen) & (df_plot["config"] == cfg)]
            rel_mean = sub["reliability_percent"].mean()
            fid_mean = sub["fidelity_percent"].mean()
            rel_std = sub["reliability_percent"].std()
            fid_std = sub["fidelity_percent"].std()

            ax.errorbar(
                fid_mean,
                rel_mean,
                xerr=fid_std,
                yerr=rel_std,
                fmt=markers[scen],
                color=COLORS[cfg],
                ecolor=COLORS[cfg],
                elinewidth=1.2,
                capsize=3,
                markersize=9,
                markeredgecolor="#222222",
                markeredgewidth=1.0,
                alpha=0.9,
                label=f"{cfg} ({SCENARIO_LABELS[scen]})",
            )

    ax.set_xlabel("Service Fidelity ($F$, % of Successful Requests with Optional Tasks)")
    ax.set_ylabel("Overall SLA Reliability ($100 - V_{\\mathrm{overall}}$, %)")
    ax.set_title("Fidelity vs. Reliability Pareto Trade-Off Across Stress Conditions", pad=15)
    ax.set_xlim(-5, 105)
    ax.set_ylim(40, 102)

    # Annotate Pareto ideal corner
    ax.annotate(
        "Ideal Operating Corner\n(High Fidelity & High Reliability)",
        xy=(98, 98),
        xytext=(55, 92),
        arrowprops=dict(facecolor="#333333", shrink=0.08, width=1.2, headwidth=6),
        fontsize=10,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#EBF5FB", edgecolor="#2B83BA"),
    )

    # Custom legend: Configs and Scenarios separately
    cfg_handles = [
        plt.Line2D([0], [0], marker="o", color="w", markerfacecolor=COLORS[c], markeredgecolor="#222", markersize=9, label=CONFIG_LABELS[c])
        for c in configs
    ]
    scen_handles = [
        plt.Line2D([0], [0], marker=markers[s], color="#555555", linestyle="None", markersize=8, label=SCENARIO_LABELS[s])
        for s in markers
    ]

    leg1 = ax.legend(handles=cfg_handles, loc="lower left", frameon=True, facecolor="white", title="Configuration")
    ax.add_artist(leg1)
    ax.legend(handles=scen_handles, loc="center left", frameon=True, facecolor="white", title="Scenario")

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    print(f"Generated: {out_path.name}")


def plot_sensitivity_heatmap(sens_csv: Path, out_path: Path) -> None:
    """Figure 6: BALB Weights Sensitivity Heatmap across alpha, beta, gamma."""
    if not sens_csv.exists():
        print(f"Skipping sensitivity heatmap: {sens_csv} not found.")
        return

    df_sens = pd.read_csv(sens_csv)
    gammas = sorted(df_sens["gamma"].unique())

    fig, axes = plt.subplots(1, len(gammas), figsize=(4.5 * len(gammas), 4.5), dpi=300, sharey=True)
    if len(gammas) == 1:
        axes = [axes]

    for ax, g_val in zip(axes, gammas):
        sub = df_sens[df_sens["gamma"] == g_val]
        piv = sub.groupby(["alpha", "beta"])["v_overall_percent"].mean().unstack(level="beta")

        im = ax.imshow(piv.values, cmap="YlGnBu_r", vmin=30, vmax=50, origin="lower")
        ax.set_title(f"Utilization Weight $\\gamma = {g_val}$")
        ax.set_xlabel("Queue Penalty Weight ($\\beta$)")
        if ax == axes[0]:
            ax.set_ylabel("Dimmer Weight ($\\alpha$)")

        ax.set_xticks(np.arange(len(piv.columns)))
        ax.set_xticklabels([f"{c:.1f}" for c in piv.columns])
        ax.set_yticks(np.arange(len(piv.index)))
        ax.set_yticklabels([f"{r:.1f}" for r in piv.index])

        # Annotate cell values
        for i in range(len(piv.index)):
            for j in range(len(piv.columns)):
                val = piv.iloc[i, j]
                ax.text(j, i, f"{val:.1f}%", ha="center", va="center", color="black" if val > 40 else "white", fontsize=9)

    fig.subplots_adjust(right=0.88)
    cbar_ax = fig.add_axes([0.91, 0.2, 0.02, 0.6])
    cbar = fig.colorbar(im, cax=cbar_ax)
    cbar.set_label("Mean Overall SLA Failure Rate ($V_{\\mathrm{overall}}$, %)")

    fig.suptitle("BALB Parameter Sensitivity: Overall SLA Failure Rate ($V_{\\mathrm{overall}}$) Under Compound Stress", y=1.03)
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Generated: {out_path.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate publication plots for CloudRescue.")
    parser.add_argument(
        "--results-dir",
        type=str,
        default="results/experiment_360",
        help="Base results directory (default: results/experiment_360).",
    )
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    plots_dir = results_dir / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)

    master_csv = results_dir / "master_results.csv"
    if not master_csv.exists():
        print(f"Error: {master_csv} does not exist. Run experiment matrix first.")
        sys.exit(1)

    df_master = pd.read_csv(master_csv)
    setup_matplotlib_style()

    print("Generating publication figures...")
    plot_sla_violation_rates(df_master, plots_dir / "sla_violation_rates_bar.png")
    plot_latency_cdf(results_dir, plots_dir / "latency_cdf_comparison.png")
    plot_timeseries_dynamics(results_dir, plots_dir / "time_series_dynamics_compound.png")
    plot_fairness_and_utilization(df_master, plots_dir / "fairness_and_utilization_box.png")
    plot_fidelity_vs_reliability_tradeoff(df_master, plots_dir / "fidelity_vs_reliability_tradeoff.png")

    sens_csv = results_dir / "sensitivity" / "balb_weights_sweep.csv"
    plot_sensitivity_heatmap(sens_csv, plots_dir / "sensitivity_heatmap.png")
    print(f"All figures generated successfully in {plots_dir.resolve()}.")


if __name__ == "__main__":
    main()

# CloudRescue — Phase 4 Experimental Evaluation (360 Simulation Runs)

**Status:** Completed  
**Date:** 2026-10-31  
**Project:** CloudRescue — Autonomic Brownout Self-Adaptive Graceful Degradation  
**Environment:** Python 3.14.7, SimPy 4.1.1, NumPy 2.4.6, SciPy 1.18.1, Pandas 3.0.0, Matplotlib 3.10.8  

---

## 1. Experimental Protocol & Reproducibility Matrix

The full pre-registered evaluation matrix comprises **360 simulation executions** without parameter alterations or selective reporting:

$$\text{Total Runs} = 3 \text{ Configurations} \times 4 \text{ Scenarios} \times 30 \text{ Matched Seeds} = \mathbf{360\text{ Runs}}$$

### 1.1 Configurations
1. **`CFG-A` (Baseline):** Static execution ($\theta = 1.0$, all optional tasks attempted), standardized Join-Shortest-Queue (JSQ) routing.
2. **`CFG-B` (Brownout Only):** Per-worker velocity-form discrete PI controller ($\theta_i(t) \in [0.0, 1.0]$), standardized Join-Shortest-Queue (JSQ) routing.
3. **`CFG-C` (Full CloudRescue):** Per-worker velocity-form discrete PI controller combined with Brownout-Aware Load Balancing (BALB).

### 1.2 Stress Scenarios
1. **Nominal (`WKL-1` + `FAIL-0`):** Stationary arrival rate $\lambda_{\text{nom}} = 80\text{ req/s}$ ($0.08\text{ req/ms}$), no injected failures.
2. **Flash Crowd Surge (`WKL-2` + `FAIL-0`):** Baseline rate $\lambda_{\text{nom}} = 80\text{ req/s}$ with a $3\times$ surge $\lambda_{\text{burst}} = 240\text{ req/s}$ active from $t = 300\text{ s}$ to $t = 450\text{ s}$ ($\Delta t = 150\text{ s}$).
3. **Server Crash Failure (`WKL-1` + `FAIL-1`):** Baseline rate $\lambda_{\text{nom}} = 80\text{ req/s}$; 2 of 4 worker instances (Workers 1 & 2) experience a simultaneous crash-stop failure from $t = 300\text{ s}$ to $t = 450\text{ s}$ (50% cluster capacity loss).
4. **Compound Stress (`WKL-2` + `FAIL-1`):** Simultaneous flash crowd surge ($240\text{ req/s}$) and server crash failure (50% cluster capacity loss) from $t = 300\text{ s}$ to $t = 450\text{ s}$.

### 1.3 Master Seed Registry
The 30 pre-registered master seeds are:
`[1001, 1002, 1003, ..., 1030]`

All runs employ the **5-stream PRNG architecture** derived via `np.random.SeedSequence(seed).spawn(5)`:
- Stream 1: Request inter-arrival process
- Stream 2: Mandatory service time distribution ($S_{\text{mand}} \sim \text{Exp}(\mu_{\text{mand}})$)
- Stream 3: Optional service time distribution ($S_{\text{opt}} \sim \text{Exp}(\mu_{\text{opt}})$)
- Stream 4: Optional execution threshold draw ($U_{\text{opt}} \sim \text{Uniform}(0.0, 1.0)$)
- Stream 5: Failure injection and repair events

Pre-sampling immutable request attributes upfront ensures that skipping optional tasks in degraded configurations consumes zero PRNG draws, guaranteeing **100% paired workload equivalence** across all three configurations for each seed.

---

## 2. Directory Layout & Artifacts

```
results/experiment_360/
├── master_results.csv              # All 360 simulation runs with 28 columns of metrics
├── aggregated_metrics.csv          # Grouped statistics (mean, std, median, IQR, min, max)
├── statistical_comparisons.csv     # Paired tests (p-values, test stats, effect sizes, 95% CIs)
├── execution.log                   # Complete execution timestamped log
├── README.md                       # This reproducibility guide
├── EXPERIMENT_REPORT.md            # Comprehensive research analysis report
├── plots/                          # Publication-quality figures (300 DPI)
│   ├── sla_violation_rates_bar.png
│   ├── latency_cdf_comparison.png
│   ├── time_series_dynamics_compound.png
│   ├── fairness_and_utilization_box.png
│   ├── fidelity_vs_reliability_tradeoff.png
│   └── sensitivity_heatmap.png
├── sensitivity/                    # BALB weight grid sweeps (alpha, beta, gamma)
│   ├── balb_weights_sweep.csv
│   └── balb_weights_aggregated.csv
└── runs/                           # Individual run artifacts (summary.json, config.json, etc.)
    ├── nominal/
    ├── flash_crowd/
    ├── server_failure/
    └── compound_stress/
```

---

## 3. Reproduction Commands

To reproduce the full 360-run evaluation from scratch:

```bash
# 1. Activate project environment
source .venv/bin/activate

# 2. Execute master experiment matrix (360 runs in parallel across 7 processes)
python scripts/run_experiment_matrix.py --processes 7 --output-dir results/experiment_360

# 3. Execute paired statistical hypothesis tests
python scripts/analyze_results.py --master-csv results/experiment_360/master_results.csv --output-dir results/experiment_360

# 4. Run BALB sensitivity parameter grid sweep
python scripts/run_sensitivity.py --processes 7 --output-dir results/experiment_360/sensitivity

# 5. Generate publication plots
python scripts/generate_plots.py --results-dir results/experiment_360
```

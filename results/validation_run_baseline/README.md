# CloudRescue — Phase 1 Baseline Validation Run

> **IMPORTANT NOTICE:** This directory contains preliminary validation run artifacts generated during Phase 1 engine verification. These are **NOT** final experimental research findings.

- **Configuration:** CFG-A (Baseline, $\theta=1.0$, Join-Shortest-Queue)
- **Simulation Time:** 20.0 s (20000 ms)
- **Warm-Up Time:** 2.0 s (2000 ms)
- **Master Seed:** 42
- **Total Generated Requests:** 1598
- **Submitted (Post Warm-Up):** 1434
- **Completed (Post Warm-Up):** 1363
- **Request Success Rate ($S_r$):** 95.05%
- **Latency SLA Violations ($V_{\text{lat}}$):** 30.96%
- **Overall SLA Failures ($V_{\text{overall}}$):** 30.68%
- **Mean Latency ($\bar{L}$):** 80.15 ms
- **Median Latency ($L_{50}$):** 72.81 ms
- **95th Percentile Latency ($L_{95}$):** 172.98 ms
- **99th Percentile Latency ($L_{99}$):** 196.83 ms
- **Fidelity ($F$):** 100.0%
- **Mean Worker Utilization ($\bar{U}$):** 80.11%
- **Jain's Fairness Index ($J$):** 0.9636

## Artifact Files
- `config.json`: Configuration snapshot.
- `events.csv.gz`: Compressed timestamped simulation event log.
- `summary.json`: Computed summary metrics.

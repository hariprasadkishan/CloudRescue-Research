# CloudRescue — Phase 2 Brownout Validation Run (CFG-B)

> **IMPORTANT NOTICE:** This directory contains preliminary validation run artifacts generated during Phase 2 engine verification. These are **NOT** final experimental research findings.

- **Configuration:** CFG-B (Brownout Only, Adaptive PI Dimmer $\theta_i(t)$, Join-Shortest-Queue)
- **Simulation Time:** 20.0 s (20000 ms)
- **Warm-Up Time:** 2.0 s (2000 ms)
- **Master Seed:** 42
- **Total Generated Requests:** 1598
- **Submitted (Post Warm-Up):** 1434
- **Completed (Post Warm-Up):** 1380
- **Request Success Rate ($S_r$):** 96.23%
- **Latency SLA Violations ($V_{\text{lat}}$):** 23.62%
- **Overall SLA Failures ($V_{\text{overall}}$):** 23.36%
- **Mean Latency ($\bar{L}$):** 69.93 ms
- **Median Latency ($L_{50}$):** 60.88 ms
- **95th Percentile Latency ($L_{95}$):** 159.22 ms
- **99th Percentile Latency ($L_{99}$):** 187.16 ms
- **Service Fidelity ($F$):** 90.0%
- **Mean Operational Dimmer ($\bar{\theta}$):** 0.8971
- **Per-Worker Dimmer:** {0: 0.8828, 1: 0.9103, 2: 0.8911, 3: 0.9041}
- **Mean Worker Utilization ($\bar{U}$):** 75.5%
- **Jain's Fairness Index ($J$):** 0.9508

## Artifact Files
- `config.json`: Configuration snapshot.
- `events.csv.gz`: Compressed timestamped simulation event log.
- `controller_timeseries.csv`: Discrete controller time-series records (p95, error, theta).
- `summary.json`: Computed summary metrics.

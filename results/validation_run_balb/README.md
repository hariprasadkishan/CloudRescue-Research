# CloudRescue — Phase 3 BALB Validation Run (CFG-C)

> **IMPORTANT NOTICE:** This directory contains preliminary validation run artifacts generated during Phase 3 engine verification. These are **NOT** final experimental research findings.

- **Configuration:** CFG-C (Brownout + BALB: Adaptive PI Dimmer $\theta_i(t)$, Score-Based BALB Routing)
- **Simulation Time:** 20.0 s (20000 ms)
- **Warm-Up Time:** 2.0 s (2000 ms)
- **Master Seed:** 42
- **Total Generated Requests:** 1598
- **Submitted (Post Warm-Up):** 1434
- **Completed (Post Warm-Up):** 1347
- **Request Success Rate ($S_r$):** 93.93%
- **Latency SLA Violations ($V_{\text{lat}}$):** 30.44%
- **Overall SLA Failures ($V_{\text{overall}}$):** 30.4%
- **Median Latency ($L_{50}$):** 70.35 ms
- **95th Percentile Latency ($L_{95}$):** 168.28 ms
- **99th Percentile Latency ($L_{99}$):** 191.01 ms
- **Mean Latency ($\bar{L}$):** 78.33 ms
- **Service Fidelity ($F$):** 90.13%
- **Mean Operational Dimmer ($\bar{\theta}$):** 0.8922
- **Per-Worker Dimmer:** {0: 0.898, 1: 0.881, 2: 0.8993, 3: 0.8905}
- **Mean Worker Utilization ($\bar{U}$):** 74.62%
- **Jain's Fairness Index ($J$):** 0.9921
- **BALB Fallback Decisions:** 0 / 1598 (0.00%)

## Artifact Files
- `config.json`: Configuration snapshot.
- `events.csv.gz`: Compressed timestamped simulation event log.
- `controller_timeseries.csv`: Discrete controller time-series records (p95, error, theta).
- `balb_routing_diagnostics.csv`: Per-request BALB candidate score breakdowns and selected worker.
- `summary.json`: Computed summary metrics and BALB diagnostic totals.

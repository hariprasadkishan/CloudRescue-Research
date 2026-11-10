"""Unit tests for recovery_analyzer module verifying T_adapt and T_restore calculations."""

import numpy as np
import pandas as pd
import pytest
from simulator.cloudrescue.monitoring.recovery_analyzer import compute_recovery_metrics


def test_nominal_scenario_returns_none():
    """Verify that nominal scenario with no shock returns None for T_adapt and T_restore."""
    res = compute_recovery_metrics(
        completed_requests=[(100.0, 50.0), (200.0, 60.0)],
        controller_timeseries=pd.DataFrame(),
        t_shock_start_ms=None,
        t_shock_end_ms=None,
    )
    assert res.t_adapt_s is None
    assert res.t_restore_s is None
    assert res.t_adapt_recovered is True


def test_adaptation_recovery_detection():
    """Verify detection of T_adapt when rolling p95 falls below r_SLA for 3s."""
    # Generate requests: high latency during shock (300s-350s), then low latency (<100ms) from 350s to 450s
    reqs = []
    # From 300s to 350s: 20 reqs/sec with latency 150ms
    for t in np.arange(290_000.0, 350_000.0, 50.0):
        reqs.append((float(t), 150.0))
    # From 350s onward: 20 reqs/sec with latency 70ms
    for t in np.arange(350_000.0, 460_000.0, 50.0):
        reqs.append((float(t), 70.0))

    ctrl_df = pd.DataFrame([
        {"timestamp": 300_000.0, "worker_id": 0, "new_theta": 0.5},
        {"timestamp": 450_000.0, "worker_id": 0, "new_theta": 1.0},
    ])

    res = compute_recovery_metrics(
        completed_requests=reqs,
        controller_timeseries=ctrl_df,
        t_shock_start_ms=300_000.0,
        t_shock_end_ms=450_000.0,
        t_sim_end_ms=1_000_000.0,
        r_sla_ms=100.0,
        r_target_ms=80.0,
    )

    assert res.t_adapt_recovered is True
    # Shock started at 300s. Stable adaptation after 350s should be detected ~360s (window 10s + 3s stable)
    assert 50.0 <= res.t_adapt_s <= 75.0


def test_unrecovered_adaptation_is_right_censored():
    """Verify that failure to adapt during the shock is right-censored at total shock duration."""
    # High latency constantly through the entire shock
    reqs = [(float(t), 180.0) for t in np.arange(290_000.0, 460_000.0, 50.0)]

    res = compute_recovery_metrics(
        completed_requests=reqs,
        controller_timeseries=pd.DataFrame(),
        t_shock_start_ms=300_000.0,
        t_shock_end_ms=450_000.0,
        t_sim_end_ms=1_000_000.0,
        r_sla_ms=100.0,
    )

    assert res.t_adapt_recovered is False
    assert res.t_adapt_s == 150.0  # (450s - 300s)


def test_post_restoration_nominal_referenced_recovery_detected():
    """Verify that restoration is detected when restored workers reach >=95% of nominal ref and p95 <= 80ms."""
    # Completed requests from 440s to 550s: latency 60ms (< 80ms target)
    reqs = [(float(t), 60.0) for t in np.arange(440_000.0, 550_000.0, 50.0)]

    # Restored workers (1 and 2) recover their dimmer to >= 0.95 * ref (ref=0.20, threshold=0.19) at t=480s
    rows = []
    for t in np.arange(450_000.0, 550_000.0, 1000.0):
        theta_val = 0.10 if t < 480_000.0 else 0.22  # 0.22 >= 0.19
        for wid in [0, 1, 2, 3]:
            rows.append({"timestamp": float(t), "worker_id": wid, "new_theta": theta_val})
    ctrl_df = pd.DataFrame(rows)

    nom_refs = {0: 0.20, 1: 0.20, 2: 0.20, 3: 0.20}

    res = compute_recovery_metrics(
        completed_requests=reqs,
        controller_timeseries=ctrl_df,
        t_shock_start_ms=300_000.0,
        t_shock_end_ms=450_000.0,
        t_sim_end_ms=1_000_000.0,
        r_sla_ms=100.0,
        r_target_ms=80.0,
        nominal_dimmer_refs=nom_refs,
        restored_worker_ids=[1, 2],
    )

    assert res.t_restore_recovered is True
    # At 480s dimmer reaches 0.22; with 3s stability requirement, detection at ~33s post shock end (450s + 33s = 483s)
    assert 30.0 <= res.t_restore_s <= 40.0


def test_post_restoration_dimmer_below_nominal_is_right_censored():
    """Verify right-censoring when restored workers never reach 95% of nominal reference."""
    reqs = [(float(t), 60.0) for t in np.arange(440_000.0, 550_000.0, 50.0)]

    # Restored workers only reach 0.15 (< 0.19)
    rows = []
    for t in np.arange(450_000.0, 550_000.0, 1000.0):
        for wid in [0, 1, 2, 3]:
            rows.append({"timestamp": float(t), "worker_id": wid, "new_theta": 0.15})
    ctrl_df = pd.DataFrame(rows)

    nom_refs = {0: 0.20, 1: 0.20, 2: 0.20, 3: 0.20}

    res = compute_recovery_metrics(
        completed_requests=reqs,
        controller_timeseries=ctrl_df,
        t_shock_start_ms=300_000.0,
        t_shock_end_ms=450_000.0,
        t_sim_end_ms=1_000_000.0,
        r_sla_ms=100.0,
        r_target_ms=80.0,
        nominal_dimmer_refs=nom_refs,
        restored_worker_ids=[1, 2],
    )

    assert res.t_restore_recovered is False
    assert res.t_restore_s == 550.0  # (1000s - 450s)


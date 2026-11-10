"""Recovery time analyzer evaluating T_adapt and T_restore per EXPERIMENT_PLAN.md."""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np
import pandas as pd


@dataclass
class RecoveryMetrics:
    """Holds adaptation and post-restoration recovery time measurements."""
    t_adapt_s: Optional[float]
    t_adapt_recovered: bool
    t_restore_s: Optional[float]
    t_restore_recovered: bool
    notes: str = ""


def compute_recovery_metrics(
    completed_requests: List[Tuple[float, float]],  # (t_completed_ms, latency_ms)
    controller_timeseries: pd.DataFrame,             # columns: timestamp, worker_id, new_theta
    t_shock_start_ms: Optional[float] = 300_000.0,
    t_shock_end_ms: Optional[float] = 450_000.0,
    t_sim_end_ms: float = 1_000_000.0,
    r_sla_ms: float = 100.0,
    r_target_ms: float = 80.0,
    w_rec_ms: float = 10_000.0,                     # 10s evaluation window
    n_rec_min: int = 20,                            # 20 samples minimum
    t_stable_ms: float = 3_000.0,                   # 3s stability threshold
    dt_eval_ms: float = 1_000.0,                    # evaluate every 1s
    theta_restore_threshold: float = 0.95,
    nominal_dimmer_refs: Optional[dict[int, float]] = None,
    restored_worker_ids: Optional[List[int]] = None,
    relative_restore_ratio: float = 0.95,
) -> RecoveryMetrics:
    """Evaluates T_adapt and T_restore per EXPERIMENT_PLAN.md Section 5, Metric 8 and DEC-010.
    
    If nominal_dimmer_refs is provided:
        Post-restoration requires that each restored worker's dimmer achieves at least
        relative_restore_ratio (default 95%) of its own steady-state nominal reference,
        combined with rolling p95 latency <= r_target_ms (80 ms) for t_stable_ms (3s).
    Otherwise:
        Falls back to legacy absolute cluster mean dimmer >= theta_restore_threshold.
    
    If no stress is configured (Nominal scenario, t_shock_start_ms is None), returns None.
    """
    if t_shock_start_ms is None or t_shock_end_ms is None:
        return RecoveryMetrics(
            t_adapt_s=None,
            t_adapt_recovered=True,
            t_restore_s=None,
            t_restore_recovered=True,
            notes="Nominal scenario (no stress injected)",
        )

    # Sort completions by completion time
    if not completed_requests:
        return RecoveryMetrics(
            t_adapt_s=float((t_shock_end_ms - t_shock_start_ms) / 1000.0),
            t_adapt_recovered=False,
            t_restore_s=float((t_sim_end_ms - t_shock_end_ms) / 1000.0),
            t_restore_recovered=False,
            notes="No completed requests",
        )

    comp_arr = np.array(sorted(completed_requests, key=lambda x: x[0]))
    c_times = comp_arr[:, 0]
    c_lats = comp_arr[:, 1]

    # Pre-process controller timeseries into a lookup of mean dimmer at timestamp t
    # If controller timeseries is empty (e.g. CFG-A baseline where theta=1.0 constantly)
    has_ctrl = not controller_timeseries.empty and "new_theta" in controller_timeseries.columns

    def get_cluster_mean_theta(t_query: float) -> float:
        if not has_ctrl:
            return 1.0  # CFG-A baseline operates at static theta = 1.0
        # Filter events up to t_query
        past_events = controller_timeseries[controller_timeseries["timestamp"] <= t_query]
        if past_events.empty:
            return 1.0
        # Get the latest reported theta per worker
        latest = past_events.sort_values("timestamp").groupby("worker_id").last()
        return float(latest["new_theta"].mean())

    def get_worker_thetas(t_query: float) -> dict[int, float]:
        if not has_ctrl:
            return {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0}
        past_events = controller_timeseries[controller_timeseries["timestamp"] <= t_query]
        if past_events.empty:
            return {0: 1.0, 1: 1.0, 2: 1.0, 3: 1.0}
        latest = past_events.sort_values("timestamp").groupby("worker_id").last()
        return latest["new_theta"].to_dict()

    def get_rolling_p95(t_eval: float) -> Optional[float]:
        t_low = t_eval - w_rec_ms
        i_low = np.searchsorted(c_times, t_low, side="left")
        i_high = np.searchsorted(c_times, t_eval, side="right")
        count = i_high - i_low
        if count < n_rec_min:
            return None
        return float(np.percentile(c_lats[i_low:i_high], 95))

    # --- 1. Adaptation Recovery Time (T_adapt) ---
    # Evaluated during active shock: [t_shock_start_ms, t_shock_end_ms]
    adapted_timestamp: Optional[float] = None
    consecutive_stable_ms = 0.0

    eval_times_adapt = np.arange(t_shock_start_ms, t_shock_end_ms + 1.0, dt_eval_ms)
    for t in eval_times_adapt:
        p95 = get_rolling_p95(t)
        if p95 is not None and p95 <= r_sla_ms:
            consecutive_stable_ms += dt_eval_ms
            if consecutive_stable_ms >= t_stable_ms:
                # Earliest timestamp where continuous stability was satisfied
                adapted_timestamp = t
                break
        else:
            consecutive_stable_ms = 0.0

    if adapted_timestamp is not None:
        t_adapt_s = round(float((adapted_timestamp - t_shock_start_ms) / 1000.0), 2)
        t_adapt_recovered = True
    else:
        # Right-censored at total duration of shock
        t_adapt_s = round(float((t_shock_end_ms - t_shock_start_ms) / 1000.0), 2)
        t_adapt_recovered = False

    # --- 2. Post-Restoration Recovery Time (T_restore) ---
    # Evaluated after failure repair: [t_shock_end_ms, t_sim_end_ms]
    restored_timestamp: Optional[float] = None
    consecutive_restore_ms = 0.0

    eval_times_restore = np.arange(t_shock_end_ms, t_sim_end_ms + 1.0, dt_eval_ms)
    for t in eval_times_restore:
        p95 = get_rolling_p95(t)

        if nominal_dimmer_refs is not None:
            worker_thetas = get_worker_thetas(t)
            check_wids = restored_worker_ids if restored_worker_ids is not None else list(nominal_dimmer_refs.keys())
            dimmer_ok = True
            for wid in check_wids:
                ref = nominal_dimmer_refs.get(wid, 1.0)
                curr = worker_thetas.get(wid, 1.0)
                if curr < relative_restore_ratio * ref:
                    dimmer_ok = False
                    break
        else:
            theta_bar = get_cluster_mean_theta(t)
            dimmer_ok = bool(theta_bar >= theta_restore_threshold)

        if p95 is not None and p95 <= r_target_ms and dimmer_ok:
            consecutive_restore_ms += dt_eval_ms
            if consecutive_restore_ms >= t_stable_ms:
                restored_timestamp = t
                break
        else:
            consecutive_restore_ms = 0.0

    if restored_timestamp is not None:
        t_restore_s = round(float((restored_timestamp - t_shock_end_ms) / 1000.0), 2)
        t_restore_recovered = True
    else:
        # Right-censored at remaining simulation duration post-repair
        t_restore_s = round(float((t_sim_end_ms - t_shock_end_ms) / 1000.0), 2)
        t_restore_recovered = False

    return RecoveryMetrics(
        t_adapt_s=t_adapt_s,
        t_adapt_recovered=t_adapt_recovered,
        t_restore_s=t_restore_s,
        t_restore_recovered=t_restore_recovered,
    )

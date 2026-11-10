"""Adaptive Brownout PI Controller implementing velocity-form discrete control with anti-windup.

Mathematical formulation adheres strictly to ARCHITECTURE.md, EXPERIMENT_PLAN.md,
and DECISIONS.md (DEC-009):
- Error calculation: e_i(t) = r_target - r_hat_95,i(t)
- Velocity form update: delta_theta_i(t) = Kp * (e_i(t) - e_prev) + Ki * e_i(t) * delta_t
- Intrinsic anti-windup: theta_i(t) = clamp(theta_i(t - delta_t) + delta_theta_i(t), theta_min, theta_max)
- Missing data hold: if samples < N_min_ctrl, PI update is skipped and theta is held constant.
- Derivative kick prevention: on resumption, e_prev is re-initialized to e_current.
- Stalled queue safety decrement: if samples < N_min_ctrl but queue > 0 and wait > r_target,
  theta is decremented by delta_stall.
- Crash/recovery state management: on worker recovery, the controller resets to nominal
  (theta = 1.0, e_prev = None) because the instance re-enters service with an empty queue
  and zero backlog, ensuring newly dispatched requests receive full fidelity without
  artificial derivative impulses.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, TYPE_CHECKING
import numpy as np

from ..config import SimulationConfig

if TYPE_CHECKING:
    import simpy
    from ..models.worker import WorkerInstance
    from ..monitoring.event_logger import EventLogger


@dataclass
class ControllerStepResult:
    """Snapshot of a single controller evaluation tick."""
    timestamp: float
    worker_id: int
    measured_p95_ms: Optional[float]
    error_s: Optional[float]
    old_theta: float
    new_theta: float
    n_samples: int
    status: str  # "updated", "held_insufficient_samples", "stalled_queue_decrement", "offline"


class BrownoutController:
    """Per-worker adaptive Brownout PI feedback controller."""

    def __init__(
        self,
        worker: WorkerInstance,
        config: SimulationConfig,
        logger: Optional[EventLogger] = None,
    ) -> None:
        self.worker = worker
        self.config = config
        self.logger = logger

        # Control parameters from SimulationConfig (not hardcoded)
        self.worker_id = worker.worker_id
        self.target_latency_ms = config.target_latency_ms
        self.target_latency_s = config.target_latency_ms / 1000.0
        self.ctrl_interval_ms = config.ctrl_interval_ms
        self.ctrl_interval_s = config.ctrl_interval_ms / 1000.0
        self.kp = config.kp
        self.ki = config.ki  # Ki in s^-1
        self.n_min_ctrl = config.n_min_ctrl
        self.delta_stall = config.delta_stall
        self.theta_min = config.theta_min
        self.theta_max = config.theta_max

        # Dynamic controller state
        self.current_theta: float = self.theta_max
        self.prev_error_s: Optional[float] = None
        self.step_history: List[ControllerStepResult] = []

        # Synchronize worker dimmer
        self.worker.current_theta = self.current_theta

    def reset(self) -> None:
        """Reset controller state upon worker recovery.
        
        Design Choice:
        When a worker recovers from a crash-stop failure, its internal queues and buffers
        have been purged. Resetting theta to theta_max (1.0) and prev_error to None ensures
        that the restored instance immediately contributes full service capacity without
        carrying forward obsolete overload state or introducing artificial derivative kicks.
        """
        self.current_theta = self.theta_max
        self.prev_error_s = None
        self.worker.current_theta = self.current_theta

    def step(self, current_time: float) -> ControllerStepResult:
        """Executes a single periodic control update at timestamp current_time."""
        if not self.worker.is_healthy:
            result = ControllerStepResult(
                timestamp=current_time,
                worker_id=self.worker_id,
                measured_p95_ms=None,
                error_s=None,
                old_theta=self.current_theta,
                new_theta=self.current_theta,
                n_samples=0,
                status="offline",
            )
            self.step_history.append(result)
            return result

        # 1. Gather requests completed within the sliding control interval [t - delta_t, t]
        window_start = current_time - self.ctrl_interval_ms
        completed_in_window = self.worker.get_completed_in_window(window_start, current_time)
        n_samples = len(completed_in_window)

        # 2. Insufficient data verification (DEC-009)
        if n_samples < self.n_min_ctrl:
            hol_wait_ms = self.worker.get_head_of_line_wait_time(current_time)
            queue_len = self.worker.queue_length

            # Stalled queue condition: queue non-empty and head-of-line wait exceeds target setpoint
            if queue_len > 0 and hol_wait_ms > self.target_latency_ms:
                old_theta = self.current_theta
                cand_theta = self.current_theta - self.delta_stall
                self.current_theta = max(self.theta_min, min(self.theta_max, cand_theta))
                self.worker.current_theta = self.current_theta
                self.prev_error_s = None  # Reset error to avoid derivative kick on resumption
                status = "stalled_queue_decrement"

                result = ControllerStepResult(
                    timestamp=current_time,
                    worker_id=self.worker_id,
                    measured_p95_ms=None,
                    error_s=None,
                    old_theta=old_theta,
                    new_theta=self.current_theta,
                    n_samples=n_samples,
                    status=status,
                )
            else:
                # Hold theta constant
                old_theta = self.current_theta
                self.prev_error_s = None  # Invalidate previous error state
                status = "held_insufficient_samples"

                result = ControllerStepResult(
                    timestamp=current_time,
                    worker_id=self.worker_id,
                    measured_p95_ms=None,
                    error_s=None,
                    old_theta=old_theta,
                    new_theta=self.current_theta,
                    n_samples=n_samples,
                    status=status,
                )

        else:
            # 3. Valid sample count: compute 95th-percentile response latency
            latencies = [
                r.total_latency for r in completed_in_window if r.total_latency is not None
            ]
            measured_p95_ms = float(np.percentile(latencies, 95))
            measured_p95_s = measured_p95_ms / 1000.0

            # Error calculation: e_i(t) = r_target - r_measured(t)
            # Latency > target => error < 0 (overloaded, reduces theta)
            # Latency <= target => error >= 0 (headroom, restores theta)
            error_s = self.target_latency_s - measured_p95_s

            # State Resumption: if resuming after hold or reset, initialize prev_error = error
            # so the derivative term Kp * (e - e_prev) evaluates to zero
            if self.prev_error_s is None:
                self.prev_error_s = error_s

            # Discrete PI Velocity Form:
            # delta_theta = Kp * (e - e_prev) + Ki * e * delta_t
            delta_p = self.kp * (error_s - self.prev_error_s)
            delta_i = self.ki * error_s * self.ctrl_interval_s
            delta_theta = delta_p + delta_i

            old_theta = self.current_theta
            cand_theta = self.current_theta + delta_theta

            # Intrinsic Anti-Windup Clamping to [theta_min, theta_max]
            self.current_theta = max(self.theta_min, min(self.theta_max, cand_theta))
            self.worker.current_theta = self.current_theta
            self.prev_error_s = error_s
            status = "updated"

            result = ControllerStepResult(
                timestamp=current_time,
                worker_id=self.worker_id,
                measured_p95_ms=measured_p95_ms,
                error_s=error_s,
                old_theta=old_theta,
                new_theta=self.current_theta,
                n_samples=n_samples,
                status=status,
            )

        self.step_history.append(result)

        if self.logger:
            self.logger.log_event(
                "CONTROLLER_UPDATED",
                current_time,
                worker_id=self.worker_id,
                measured_p95_ms=result.measured_p95_ms,
                error=result.error_s,
                old_theta=result.old_theta,
                new_theta=result.new_theta,
                n_samples=result.n_samples,
                status=result.status,
            )

        return result

    def get_timeseries_df(self) -> pd.DataFrame:
        """Returns step history as a pandas DataFrame."""
        import pandas as pd
        if not self.step_history:
            return pd.DataFrame(columns=["timestamp", "worker_id", "measured_p95_ms", "error_s", "old_theta", "new_theta", "n_samples", "status"])
        records = [
            {
                "timestamp": s.timestamp,
                "worker_id": s.worker_id,
                "measured_p95_ms": s.measured_p95_ms,
                "error_s": s.error_s,
                "old_theta": s.old_theta,
                "new_theta": s.new_theta,
                "n_samples": s.n_samples,
                "status": s.status,
            }
            for s in self.step_history
        ]
        return pd.DataFrame(records)

    def run_control_loop(self, env: simpy.Environment) -> simpy.Process:
        """SimPy periodic process running the feedback controller every ctrl_interval_ms."""
        while True:
            yield env.timeout(self.ctrl_interval_ms)
            self.step(env.now)

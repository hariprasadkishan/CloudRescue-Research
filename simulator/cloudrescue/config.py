"""Configuration parameters for CloudRescue simulation.

All parameters adhere to specifications in PRD.md and EXPERIMENT_PLAN.md.
Time units in this simulator are normalized to milliseconds (ms) unless explicitly noted.
Rate units are expressed in events per millisecond (e.g., 80 req/s = 0.08 req/ms).
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


@dataclass(frozen=True)
class FailureSchedule:
    """Defines a worker crash and recovery interval."""
    worker_ids: List[int]
    t_fail: float  # In milliseconds
    t_repair: float  # In milliseconds

    def __post_init__(self) -> None:
        if self.t_fail < 0:
            raise ValueError(f"t_fail must be non-negative, got {self.t_fail}")
        if self.t_repair <= self.t_fail:
            raise ValueError(f"t_repair ({self.t_repair}) must be greater than t_fail ({self.t_fail})")
        if not self.worker_ids:
            raise ValueError("worker_ids cannot be empty")


@dataclass
class SimulationConfig:
    """Master configuration for CloudRescue discrete-event simulation."""

    # Cluster configuration
    num_workers: int = 4
    queue_capacity: int = 50
    mu_mand: float = 0.1  # Mean mandatory service time = 10 ms (rate = 0.1 req/ms)
    mu_opt: float = 1.0 / 30.0  # Mean optional service time = 30 ms (rate ≈ 0.0333 req/ms)
    timeout_ms: float = 200.0  # Request timeout deadline T_timeout (ms)
    sla_threshold_ms: float = 100.0  # SLA latency limit r_SLA (ms)
    target_latency_ms: float = 80.0  # Controller target setpoint r_target (ms)

    # Workload configuration
    lambda_nom: float = 0.08  # Nominal arrival rate = 80 req/s = 0.08 req/ms
    lambda_burst: float = 0.24  # Burst arrival rate = 240 req/s = 0.24 req/ms
    burst_start_ms: float = 300_000.0  # 300 seconds = 300,000 ms
    burst_duration_ms: float = 150_000.0  # 150 seconds = 150,000 ms

    # Execution configuration
    sim_time_ms: float = 1_000_000.0  # 1,000 seconds = 1,000,000 ms
    warmup_ms: float = 100_000.0  # 100 seconds = 100,000 ms
    seed: int = 42

    # Failure schedules
    fail_schedules: List[FailureSchedule] = field(default_factory=list)

    # Resilience Configuration Mode
    mode: str = "CFG-A"  # "CFG-A" (Baseline), "CFG-B" (Brownout Only), "CFG-C" (Full CloudRescue)
    enable_brownout: bool = False  # Set to True for CFG-B and CFG-C

    # Controller parameters
    ctrl_interval_ms: float = 1_000.0  # delta_t_ctrl = 1.0 s = 1,000 ms
    n_min_ctrl: int = 5
    delta_stall: float = 0.05
    kp: float = 0.5
    ki: float = 0.1  # Ki = 0.1 s^-1 (per PRD and EXPERIMENT_PLAN table row 71)
    theta_min: float = 0.0
    theta_max: float = 1.0

    # Load balancer parameters (CFG-A and CFG-B use pure JSQ)
    routing_policy: str = "JSQ"  # "JSQ" for CFG-A/B, "BALB" for CFG-C
    balb_alpha: float = 1.0
    balb_beta: float = 1.0
    balb_gamma: float = 0.5
    q_soft_ratio: float = 0.8  # Q_soft = 0.8 * Q_max

    def validate(self) -> None:
        """Validate configuration parameters. Raises ValueError on invalid inputs."""
        if self.num_workers <= 0:
            raise ValueError(f"num_workers must be positive, got {self.num_workers}")
        if self.queue_capacity <= 0:
            raise ValueError(f"queue_capacity must be positive, got {self.queue_capacity}")
        if self.mu_mand <= 0:
            raise ValueError(f"mu_mand must be positive, got {self.mu_mand}")
        if self.mu_opt <= 0:
            raise ValueError(f"mu_opt must be positive, got {self.mu_opt}")
        if self.timeout_ms <= 0:
            raise ValueError(f"timeout_ms must be positive, got {self.timeout_ms}")
        if self.sla_threshold_ms <= 0:
            raise ValueError(f"sla_threshold_ms must be positive, got {self.sla_threshold_ms}")
        if self.target_latency_ms <= 0:
            raise ValueError(f"target_latency_ms must be positive, got {self.target_latency_ms}")
        if self.lambda_nom <= 0:
            raise ValueError(f"lambda_nom must be positive, got {self.lambda_nom}")
        if self.lambda_burst < 0:
            raise ValueError(f"lambda_burst cannot be negative, got {self.lambda_burst}")
        if self.burst_start_ms < 0:
            raise ValueError(f"burst_start_ms cannot be negative, got {self.burst_start_ms}")
        if self.burst_duration_ms < 0:
            raise ValueError(f"burst_duration_ms cannot be negative, got {self.burst_duration_ms}")
        if self.sim_time_ms <= 0:
            raise ValueError(f"sim_time_ms must be positive, got {self.sim_time_ms}")
        if self.warmup_ms < 0 or self.warmup_ms >= self.sim_time_ms:
            raise ValueError(f"warmup_ms ({self.warmup_ms}) must be non-negative and < sim_time_ms ({self.sim_time_ms})")
        if self.theta_min < 0.0 or self.theta_max > 1.0 or self.theta_min > self.theta_max:
            raise ValueError(f"Invalid dimmer bounds: [{self.theta_min}, {self.theta_max}]")
        if self.mode not in ("CFG-A", "CFG-B", "CFG-C"):
            raise ValueError(f"Invalid mode '{self.mode}'; must be one of 'CFG-A', 'CFG-B', 'CFG-C'")
        if self.routing_policy not in ("JSQ", "BALB"):
            raise ValueError(f"Invalid routing_policy '{self.routing_policy}'; must be 'JSQ' or 'BALB'")
        if self.balb_alpha < 0.0 or self.balb_beta < 0.0 or self.balb_gamma < 0.0:
            raise ValueError(f"BALB weights must be non-negative, got alpha={self.balb_alpha}, beta={self.balb_beta}, gamma={self.balb_gamma}")
        if self.q_soft_ratio <= 0.0 or self.q_soft_ratio > 1.0:
            raise ValueError(f"q_soft_ratio must be in (0.0, 1.0], got {self.q_soft_ratio}")

        if self.mode == "CFG-C":
            self.enable_brownout = True
            self.routing_policy = "BALB"
        elif self.mode == "CFG-B":
            self.enable_brownout = True
            self.routing_policy = "JSQ"
        elif self.routing_policy == "BALB":
            self.mode = "CFG-C"
            self.enable_brownout = True
        elif self.enable_brownout and self.mode == "CFG-A":
            self.mode = "CFG-B"
            self.routing_policy = "JSQ"
        for sched in self.fail_schedules:
            sched.__post_init__()
            for wid in sched.worker_ids:
                if wid < 0 or wid >= self.num_workers:
                    raise ValueError(f"Invalid worker_id {wid} in fail_schedule; must be in [0, {self.num_workers - 1}]")

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        d = asdict(self)
        d["fail_schedules"] = [asdict(s) for s in self.fail_schedules]
        return d

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SimulationConfig:
        """Create SimulationConfig from dictionary."""
        data_copy = dict(data)
        if "fail_schedules" in data_copy:
            data_copy["fail_schedules"] = [
                FailureSchedule(**s) if isinstance(s, dict) else s
                for s in data_copy["fail_schedules"]
            ]
        config = cls(**data_copy)
        config.validate()
        return config

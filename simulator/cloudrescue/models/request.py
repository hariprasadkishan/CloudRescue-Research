"""Request model with pre-generated attributes for deterministic reproducibility."""

from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class RequestStatus(str, Enum):
    """Lifecycle states of a request in the simulator."""
    SUBMITTED = "SUBMITTED"
    QUEUED = "QUEUED"
    DROPPED_QUEUE = "DROPPED_QUEUE"
    DROPPED_TIMEOUT = "DROPPED_TIMEOUT"
    FAILED_CRASH = "FAILED_CRASH"
    COMPLETED = "COMPLETED"


@dataclass
class Request:
    """Represents a client request in CloudRescue.
    
    Attributes k, t_arrive, s_mand, s_opt, u_opt, timeout are pre-sampled
    before simulation dispatch to guarantee 100% matched random inputs across
    ablation configurations.
    """
    request_id: int
    t_arrive: float          # Arrival timestamp (ms)
    s_mand: float            # Mandatory execution duration (ms)
    s_opt: float             # Optional execution duration (ms)
    u_opt: float             # Optional execution threshold draw in [0, 1)
    timeout: float           # Timeout deadline T_timeout (ms)

    # Dynamic lifecycle tracking
    status: RequestStatus = RequestStatus.SUBMITTED
    worker_id: Optional[int] = None
    t_queued: Optional[float] = None
    t_mand_start: Optional[float] = None
    t_mand_end: Optional[float] = None
    t_opt_start: Optional[float] = None
    t_opt_end: Optional[float] = None
    t_completed: Optional[float] = None
    opt_executed: bool = False
    theta_at_decision: Optional[float] = None

    @property
    def total_latency(self) -> Optional[float]:
        """Total response time from arrival to completion (ms)."""
        if self.t_completed is not None:
            return self.t_completed - self.t_arrive
        return None

    @property
    def queue_wait_time(self) -> Optional[float]:
        """Duration spent waiting in queue before mandatory computation begins (ms)."""
        if self.t_mand_start is not None:
            return self.t_mand_start - self.t_arrive
        return None

    def is_successful(self) -> bool:
        """A request is successful iff it completed execution and latency <= timeout."""
        if self.status != RequestStatus.COMPLETED:
            return False
        lat = self.total_latency
        return lat is not None and lat <= self.timeout

    def is_sla_violated(self, sla_threshold: float) -> bool:
        """Evaluates whether a successful request violated the SLA latency limit."""
        if not self.is_successful():
            return False
        lat = self.total_latency
        return lat is not None and lat > sla_threshold

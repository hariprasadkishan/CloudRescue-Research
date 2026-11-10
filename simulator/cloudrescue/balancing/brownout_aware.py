"""Brownout-Aware Load Balancer (BALB) for CFG-C.

Implements the composite multi-attribute utility score defined in ARCHITECTURE.md,
PRD.md, and EXPERIMENT_PLAN.md:
    Score_i(t) = alpha * theta_i(t) - beta * (q_i(t) / Q_max) - gamma * U_i(t)

Design & Provenance:
- Synthesizes principles of Klein et al. [61] (IEEE SRDS 2014) as a CloudRescue composite design.
- Direction: Higher score is superior (maximizes fidelity, penalizes queue backlog and processor load).
- Anti-overloading: Queue penalty prevents routing exclusively to high-theta workers.
- Soft Overload Fallback: When all operational workers exceed Q_soft (0.8 * Q_max),
  alpha is set to 0.0 to eliminate fidelity bias and prioritize buffer survival.
- Failure Masking: Offline/crashed instances and full-queue instances (q_i >= Q_max) are excluded.
- Deterministic Tie-Breaking: In case of equal scores, breaks ties by smaller queue length,
  then lower worker_id.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, TYPE_CHECKING
import pandas as pd

from ..models.worker import WorkerInstance
from ..models.request import Request
from ..config import SimulationConfig

if TYPE_CHECKING:
    from ..monitoring.event_logger import EventLogger


@dataclass
class BalbRoutingRecord:
    """Diagnostic record of a single BALB routing decision."""
    timestamp: float
    request_id: int
    selected_worker_id: Optional[int]
    fallback_active: bool
    scores: Dict[int, float] = field(default_factory=dict)
    thetas: Dict[int, float] = field(default_factory=dict)
    queues: Dict[int, int] = field(default_factory=dict)
    utilizations: Dict[int, float] = field(default_factory=dict)


class BrownoutAwareLoadBalancer:
    """Brownout-Aware Load Balancing policy evaluating fidelity, backlog, and CPU capacity."""

    def __init__(
        self,
        workers: List[WorkerInstance],
        config: SimulationConfig,
        logger: Optional[EventLogger] = None,
    ) -> None:
        self.workers = workers
        self.config = config
        self.logger = logger

        # Weights from configuration
        self.alpha = config.balb_alpha
        self.beta = config.balb_beta
        self.gamma = config.balb_gamma
        self.q_max = float(config.queue_capacity)
        self.q_soft = float(config.queue_capacity) * config.q_soft_ratio

        self.routing_history: List[BalbRoutingRecord] = []

    def calculate_score(
        self,
        worker: WorkerInstance,
        current_time: Optional[float] = None,
        force_zero_alpha: bool = False,
    ) -> float:
        """Calculates composite BALB score for an individual worker.
        
        Score_i = alpha * theta_i - beta * (q_i / Q_max) - gamma * U_i
        All three terms are dimensionless ratios in [0.0, 1.0].
        """
        effective_alpha = 0.0 if force_zero_alpha else self.alpha
        theta = worker.current_theta
        q_ratio = worker.queue_length / self.q_max
        u_ratio = worker.get_utilization_ratio(current_time)

        score = (effective_alpha * theta) - (self.beta * q_ratio) - (self.gamma * u_ratio)
        return score

    def select_worker(
        self,
        request: Request,
        current_time: Optional[float] = None,
    ) -> Optional[WorkerInstance]:
        """Selects the operational worker with the highest BALB composite score.
        
        Excludes offline/crashed instances and full-queue instances.
        Returns None if no worker is eligible to accept the request.
        """
        # 1. Filter eligible candidates: operational and queue not full
        operational = [w for w in self.workers if w.is_healthy]
        eligible = [w for w in operational if w.queue_length < self.config.queue_capacity]

        if not eligible:
            # Record failed routing decision (all workers crashed or saturated)
            rec = BalbRoutingRecord(
                timestamp=request.t_arrive if current_time is None else current_time,
                request_id=request.request_id,
                selected_worker_id=None,
                fallback_active=False,
            )
            self.routing_history.append(rec)
            return None

        # 2. Check soft overload fallback: all eligible workers have q_i >= Q_soft
        all_soft_overloaded = all(w.queue_length >= self.q_soft for w in eligible)
        fallback_active = all_soft_overloaded

        # 3. Score all eligible candidates
        candidate_scores: Dict[WorkerInstance, float] = {}
        thetas_diag: Dict[int, float] = {}
        queues_diag: Dict[int, int] = {}
        utils_diag: Dict[int, float] = {}
        scores_diag: Dict[int, float] = {}

        now = request.t_arrive if current_time is None else current_time

        for w in eligible:
            score = self.calculate_score(w, current_time=now, force_zero_alpha=fallback_active)
            candidate_scores[w] = score

            thetas_diag[w.worker_id] = round(w.current_theta, 4)
            queues_diag[w.worker_id] = w.queue_length
            utils_diag[w.worker_id] = round(w.get_utilization_ratio(now), 4)
            scores_diag[w.worker_id] = round(score, 4)

        # 4. Select candidate with maximum score, with deterministic tie-breaking:
        # Highest score, then lowest queue length, then lowest worker_id
        best_worker = max(
            eligible,
            key=lambda w: (
                round(candidate_scores[w], 8),
                -w.queue_length,
                -w.worker_id,
            ),
        )

        rec = BalbRoutingRecord(
            timestamp=now,
            request_id=request.request_id,
            selected_worker_id=best_worker.worker_id,
            fallback_active=fallback_active,
            scores=scores_diag,
            thetas=thetas_diag,
            queues=queues_diag,
            utilizations=utils_diag,
        )
        self.routing_history.append(rec)

        if self.logger:
            self.logger.log_event(
                "BALB_ROUTING_DECISION",
                now,
                request_id=request.request_id,
                selected_worker_id=best_worker.worker_id,
                fallback_active=fallback_active,
                scores=scores_diag,
                best_score=scores_diag.get(best_worker.worker_id),
            )

        return best_worker

    def get_diagnostics(self) -> pd.DataFrame:
        """Returns routing decisions and score diagnostics as a pandas DataFrame."""
        if not self.routing_history:
            return pd.DataFrame()
        records = []
        for r in self.routing_history:
            records.append({
                "timestamp": r.timestamp,
                "request_id": r.request_id,
                "selected_worker_id": r.selected_worker_id,
                "fallback_active": r.fallback_active,
                "scores": r.scores,
                "thetas": r.thetas,
                "queues": r.queues,
                "utilizations": r.utilizations,
            })
        return pd.DataFrame(records)

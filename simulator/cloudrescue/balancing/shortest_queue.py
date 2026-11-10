"""Join-Shortest-Queue (JSQ) load balancer for CFG-A (Baseline)."""

from __future__ import annotations
from typing import List, Optional
from ..models.worker import WorkerInstance
from ..models.request import Request


class JoinShortestQueueBalancer:
    """Standardized Join-Shortest-Queue (JSQ) load balancing policy.
    
    Routes incoming requests to the operational worker with the minimum
    current queue length. Excludes offline/crashed workers. Uses deterministic
    lowest worker_id tie-breaking to maintain perfect reproducibility.
    """

    def __init__(self, workers: List[WorkerInstance]) -> None:
        self.workers = workers

    def select_worker(
        self,
        request: Request,
        current_time: Optional[float] = None,
    ) -> Optional[WorkerInstance]:
        """Selects the operational worker with the shortest queue.
        
        Returns None if no worker is operational.
        """
        operational = [w for w in self.workers if w.is_healthy]
        if not operational:
            return None

        # Min by (queue_length, worker_id) for deterministic tie-breaking
        return min(operational, key=lambda w: (w.queue_length, w.worker_id))

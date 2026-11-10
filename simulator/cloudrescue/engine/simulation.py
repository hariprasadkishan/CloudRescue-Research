"""Discrete-event simulation engine coordinating SimPy environment, workers, and workload."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import simpy
import numpy as np

import pandas as pd

from ..config import SimulationConfig, FailureSchedule
from ..models.request import Request, RequestStatus
from ..models.worker import WorkerInstance
from ..workload.generator import WorkloadGenerator
from ..balancing.shortest_queue import JoinShortestQueueBalancer
from ..balancing.brownout_aware import BrownoutAwareLoadBalancer
from ..monitoring.event_logger import EventLogger
from ..control.brownout_controller import BrownoutController


@dataclass
class SimulationResult:
    """Holds artifacts and computed metrics of a simulation run."""
    config: SimulationConfig
    logger: EventLogger
    metrics: Dict[str, Any]
    worker_utilizations: Dict[int, float]
    mean_utilization: float
    jains_index: Optional[float]
    total_generated_requests: int
    controllers: List[BrownoutController] = field(default_factory=list)
    balb_diagnostics: Optional[pd.DataFrame] = None
    jains_index_all_workers: Optional[float] = 1.0
    active_workers_fairness: List[int] = field(default_factory=list)
    fairness_population_type: str = "strict_zero_downtime"
    fairness_status: str = "evaluable"


class SimulationEngine:
    """SimPy-based discrete-event simulation engine for CloudRescue (CFG-A, CFG-B, and CFG-C)."""

    def __init__(
        self,
        config: SimulationConfig,
        logger: Optional[EventLogger] = None,
    ) -> None:
        self.config = config
        self.config.validate()
        self.logger = logger or EventLogger()

        self.env = simpy.Environment()
        self.workers: List[WorkerInstance] = [
            WorkerInstance(
                worker_id=i,
                env=self.env,
                queue_capacity=self.config.queue_capacity,
                logger=self.logger,
                default_theta=1.0,
            )
            for i in range(self.config.num_workers)
        ]

        # Initialize per-worker Brownout PI controllers for CFG-B
        self.controllers: List[BrownoutController] = []
        if self.config.enable_brownout:
            for w in self.workers:
                ctrl = BrownoutController(worker=w, config=self.config, logger=self.logger)
                w.attach_controller(ctrl)
                self.controllers.append(ctrl)

        # Initialize load balancer: BALB for CFG-C, JSQ for CFG-A and CFG-B
        if self.config.routing_policy == "BALB" or self.config.mode == "CFG-C":
            self.balancer = BrownoutAwareLoadBalancer(
                self.workers, config=self.config, logger=self.logger
            )
        else:
            self.balancer = JoinShortestQueueBalancer(self.workers)

        self.workload_gen = WorkloadGenerator(self.config)
        self.requests: List[Request] = []

    def _schedule_failures(self) -> None:
        """Spawns SimPy processes for all configured worker failure and repair intervals."""
        for sched in self.config.fail_schedules:
            self.env.process(self._failure_lifecycle(sched))

    def _failure_lifecycle(self, sched: FailureSchedule) -> simpy.Process:
        """Manages the timeline of a single crash and repair event."""
        # Wait until crash timestamp
        delay_to_crash = sched.t_fail - self.env.now
        if delay_to_crash > 0:
            yield self.env.timeout(delay_to_crash)

        for wid in sched.worker_ids:
            if 0 <= wid < len(self.workers):
                self.workers[wid].crash()

        # Wait until repair timestamp
        delay_to_repair = sched.t_repair - self.env.now
        if delay_to_repair > 0:
            yield self.env.timeout(delay_to_repair)

        for wid in sched.worker_ids:
            if 0 <= wid < len(self.workers):
                self.workers[wid].recover()

    def _dispatch_requests(self) -> simpy.Process:
        """Dispatches pre-generated requests according to their arrival timestamps."""
        for req in self.requests:
            delay = req.t_arrive - self.env.now
            if delay > 0:
                yield self.env.timeout(delay)

            self.logger.log_event(
                "REQUEST_SUBMITTED",
                self.env.now,
                request_id=req.request_id,
            )

            target_worker = self.balancer.select_worker(req, current_time=self.env.now)
            if target_worker is None:
                # All workers are offline or saturated
                req.status = RequestStatus.DROPPED_QUEUE
                reason = "all_queues_full" if any(w.is_healthy for w in self.workers) else "all_workers_offline"
                self.logger.log_event(
                    "REQUEST_DROPPED_QUEUE",
                    self.env.now,
                    request_id=req.request_id,
                    reason=reason,
                )
            else:
                target_worker.enqueue(req)

    def run(self) -> SimulationResult:
        """Executes the discrete-event simulation to completion."""
        # Pre-generate immutable requests from multi-stream PRNG
        self.requests = self.workload_gen.generate_requests()

        # Register SimPy dispatcher and failure processes
        self.env.process(self._dispatch_requests())
        self._schedule_failures()

        # Register controller feedback processes if brownout is active
        for ctrl in self.controllers:
            self.env.process(ctrl.run_control_loop(self.env))

        # Run SimPy clock up to configured duration
        self.env.run(until=self.config.sim_time_ms)

        # Finalize metrics
        for w in self.workers:
            w.finalize_operational_time(self.config.sim_time_ms)

        worker_utils = {w.worker_id: round(w.get_utilization(), 2) for w in self.workers}
        mean_u = round(float(np.mean(list(worker_utils.values()))), 2) if worker_utils else 0.0

        warmup_ms = self.config.warmup_ms
        sim_time_ms = self.config.sim_time_ms

        # Post-warmup completed request counts per worker (successful requests N_success)
        post_warmup_counts = {
            w.worker_id: len(
                w.get_completed_in_window(
                    warmup_ms,
                    sim_time_ms,
                    successful_only=True,
                    timeout_ms=self.config.timeout_ms,
                )
            )
            for w in self.workers
        }

        # Identify active operational worker population M_active during evaluation window
        # Per EXPERIMENT_PLAN.md: "Evaluated over the set of workers M_active that were operational
        # during the evaluation window, preventing hardware outages from artificially degrading the load balancer's fairness score."
        fully_operational_workers = [
            w for w in self.workers
            if w.is_fully_operational_in_window(warmup_ms, sim_time_ms)
        ]

        if len(fully_operational_workers) >= 2:
            active_workers = fully_operational_workers
            fairness_population_type = "strict_zero_downtime"
        else:
            # Fallback if fewer than 2 workers were continuously operational:
            # Include all workers that had non-zero uptime during the evaluation window
            uptime_workers = [
                w for w in self.workers
                if ((sim_time_ms - warmup_ms) - w.get_downtime_in_window(warmup_ms, sim_time_ms)) > 0
            ]
            if uptime_workers:
                active_workers = uptime_workers
                fairness_population_type = "partial_uptime_fallback"
            else:
                active_workers = []
                fairness_population_type = "empty"

        active_wids = [w.worker_id for w in active_workers]
        active_counts = [post_warmup_counts[wid] for wid in active_wids]
        sum_active = sum(active_counts)
        sum_active_sq = sum(c * c for c in active_counts)
        m_size = len(active_counts)

        if m_size == 0:
            jains = None
            fairness_status = "undefined_no_active_workers"
        elif sum_active_sq == 0:
            jains = None
            fairness_status = "undefined_zero_completions"
        else:
            jains = round(float((sum_active ** 2) / (m_size * sum_active_sq)), 4)
            fairness_status = "evaluable"

        # Legacy / Cluster-wide comparison metric (all workers, full run including warmup)
        legacy_counts = [len(w.completed_requests) for w in self.workers]
        sum_legacy = sum(legacy_counts)
        sum_legacy_sq = sum(c * c for c in legacy_counts)
        if len(legacy_counts) == 0:
            jains_all = None
            legacy_fairness_status = "undefined_no_workers"
        elif sum_legacy_sq == 0:
            jains_all = None
            legacy_fairness_status = "undefined_zero_completions"
        else:
            jains_all = round(float((sum_legacy ** 2) / (len(legacy_counts) * sum_legacy_sq)), 4)
            legacy_fairness_status = "evaluable"

        summary = self.logger.compute_summary_metrics(
            warmup_ms=self.config.warmup_ms,
            sla_threshold_ms=self.config.sla_threshold_ms,
            timeout_ms=self.config.timeout_ms,
        )
        summary["jains_fairness_index"] = jains
        summary["jains_fairness_index_all_workers"] = jains_all
        summary["active_workers_fairness"] = active_wids
        summary["fairness_population_type"] = fairness_population_type
        summary["fairness_status"] = fairness_status
        summary["legacy_fairness_status"] = legacy_fairness_status
        summary["post_warmup_worker_counts"] = post_warmup_counts

        balb_diag = (
            self.balancer.get_diagnostics()
            if hasattr(self.balancer, "get_diagnostics")
            else None
        )

        return SimulationResult(
            config=self.config,
            logger=self.logger,
            metrics=summary,
            worker_utilizations=worker_utils,
            mean_utilization=mean_u,
            jains_index=jains,
            total_generated_requests=len(self.requests),
            controllers=self.controllers,
            balb_diagnostics=balb_diag,
            jains_index_all_workers=jains_all,
            active_workers_fairness=active_wids,
            fairness_population_type=fairness_population_type,
            fairness_status=fairness_status,
        )

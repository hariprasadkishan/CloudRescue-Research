"""Worker instance model for discrete-event cloud execution."""

from __future__ import annotations
import collections
from typing import Optional, List, Any, TYPE_CHECKING
import simpy

from .request import Request, RequestStatus

if TYPE_CHECKING:
    from ..monitoring.event_logger import EventLogger


class WorkerInstance:
    """Models a single cloud worker instance with an independent FIFO queue,
    dual-stage processing (mandatory + optional), and crash/recovery capabilities.
    """

    def __init__(
        self,
        worker_id: int,
        env: simpy.Environment,
        queue_capacity: int = 50,
        logger: Optional[EventLogger] = None,
        default_theta: float = 1.0,
    ) -> None:
        self.worker_id = worker_id
        self.env = env
        self.queue_capacity = queue_capacity
        self.logger = logger
        self.current_theta = default_theta

        self.queue: collections.deque[Request] = collections.deque()
        self.is_healthy: bool = True
        self.in_flight_request: Optional[Request] = None
        self._current_req_start: Optional[float] = None
        self.controller: Optional[Any] = None

        # Utilization and operational tracking
        self.total_busy_time: float = 0.0
        self.total_operational_time: float = 0.0
        self.last_status_change_time: float = 0.0
        self.downtime_intervals: List[tuple[float, float]] = []
        self._current_crash_start: Optional[float] = None
        self.completed_requests: List[Request] = []

        # SimPy synchronization
        self._wake_event: simpy.Event = self.env.event()
        self._service_process: simpy.Process = self.env.process(self._service_loop())

    @property
    def queue_length(self) -> int:
        """Current number of requests waiting in the queue."""
        return len(self.queue)

    def enqueue(self, request: Request) -> bool:
        """Attempts to enqueue an admitted request. Returns True if accepted, False if dropped."""
        if not self.is_healthy:
            request.status = RequestStatus.DROPPED_QUEUE
            if self.logger:
                self.logger.log_event(
                    "REQUEST_DROPPED_QUEUE",
                    self.env.now,
                    request_id=request.request_id,
                    worker_id=self.worker_id,
                    reason="worker_offline",
                )
            return False

        if len(self.queue) >= self.queue_capacity:
            request.status = RequestStatus.DROPPED_QUEUE
            if self.logger:
                self.logger.log_event(
                    "REQUEST_DROPPED_QUEUE",
                    self.env.now,
                    request_id=request.request_id,
                    worker_id=self.worker_id,
                    reason="queue_full",
                )
            return False

        request.status = RequestStatus.QUEUED
        request.worker_id = self.worker_id
        request.t_queued = self.env.now
        self.queue.append(request)

        if self.logger:
            self.logger.log_event(
                "REQUEST_QUEUED",
                self.env.now,
                request_id=request.request_id,
                worker_id=self.worker_id,
                queue_depth=len(self.queue),
            )

        # Wake up service loop if waiting
        if not self._wake_event.triggered:
            self._wake_event.succeed()

        return True

    def _service_loop(self) -> simpy.Process:
        """Sequential FIFO service loop executing mandatory and optional stages."""
        while True:
            try:
                if not self.is_healthy:
                    # Idle while offline; wait for recovery
                    self._wake_event = self.env.event()
                    yield self._wake_event
                    continue

                if not self.queue:
                    # Queue empty; wait for incoming requests
                    self._wake_event = self.env.event()
                    yield self._wake_event
                    continue

                req = self.queue.popleft()

                # Head-of-line timeout check
                wait_time = self.env.now - req.t_arrive
                if wait_time > req.timeout:
                    req.status = RequestStatus.DROPPED_TIMEOUT
                    if self.logger:
                        self.logger.log_event(
                            "REQUEST_DROPPED_TIMEOUT",
                            self.env.now,
                            request_id=req.request_id,
                            worker_id=self.worker_id,
                            wait_time=wait_time,
                        )
                    continue

                self.in_flight_request = req
                req_start_time = self.env.now
                self._current_req_start = req_start_time

                # Stage 1: Mandatory execution
                req.t_mand_start = self.env.now
                if self.logger:
                    self.logger.log_event(
                        "MANDATORY_START",
                        self.env.now,
                        request_id=req.request_id,
                        worker_id=self.worker_id,
                    )

                yield self.env.timeout(req.s_mand)

                req.t_mand_end = self.env.now
                if self.logger:
                    self.logger.log_event(
                        "MANDATORY_END",
                        self.env.now,
                        request_id=req.request_id,
                        worker_id=self.worker_id,
                        duration=req.s_mand,
                    )

                # Stage 2: Instantaneous optional execution decision
                req.theta_at_decision = self.current_theta
                if req.u_opt <= self.current_theta:
                    req.opt_executed = True
                    req.t_opt_start = self.env.now
                    if self.logger:
                        self.logger.log_event(
                            "OPTIONAL_EXECUTED",
                            self.env.now,
                            request_id=req.request_id,
                            worker_id=self.worker_id,
                            theta=self.current_theta,
                            duration=req.s_opt,
                        )

                    yield self.env.timeout(req.s_opt)
                    req.t_opt_end = self.env.now
                else:
                    req.opt_executed = False
                    if self.logger:
                        self.logger.log_event(
                            "OPTIONAL_BYPASSED",
                            self.env.now,
                            request_id=req.request_id,
                            worker_id=self.worker_id,
                            theta=self.current_theta,
                        )

                # Completion
                req.t_completed = self.env.now
                req.status = RequestStatus.COMPLETED
                self.completed_requests.append(req)

                active_duration = self.env.now - req_start_time
                self.total_busy_time += active_duration

                if self.logger:
                    self.logger.log_event(
                        "REQUEST_COMPLETED",
                        self.env.now,
                        request_id=req.request_id,
                        worker_id=self.worker_id,
                        total_latency=req.total_latency,
                        full_fidelity=req.opt_executed,
                    )

            except simpy.Interrupt:
                # Worker crashed while processing request or waiting
                if self.in_flight_request is not None:
                    self.in_flight_request.status = RequestStatus.FAILED_CRASH
                break
            finally:
                self.in_flight_request = None
                self._current_req_start = None

    def crash(self) -> None:
        """Trigger crash-stop failure: halt service, abort in-flight task, drop queued tasks."""
        if not self.is_healthy:
            return

        # Accrue operational time up to crash timestamp
        self.total_operational_time += self.env.now - self.last_status_change_time
        self.last_status_change_time = self.env.now
        self.is_healthy = False
        self._current_crash_start = self.env.now

        if self.logger:
            self.logger.log_event("SERVER_CRASHED", self.env.now, worker_id=self.worker_id)

        # Interrupt current service if busy
        if self._service_process.is_alive:
            self._service_process.interrupt()

        # Abort all requests queued on this instance
        while self.queue:
            req = self.queue.popleft()
            req.status = RequestStatus.FAILED_CRASH
            if self.logger:
                self.logger.log_event(
                    "REQUEST_FAILED_CRASH",
                    self.env.now,
                    request_id=req.request_id,
                    worker_id=self.worker_id,
                )

    def attach_controller(self, controller: Any) -> None:
        """Attaches a brownout controller to this worker instance."""
        self.controller = controller
        self.current_theta = controller.current_theta

    def recover(self) -> None:
        """Trigger recovery: restore health, restart service process, and reset controller."""
        if self.is_healthy:
            return

        if self._current_crash_start is not None:
            self.downtime_intervals.append((self._current_crash_start, self.env.now))
            self._current_crash_start = None

        self.last_status_change_time = self.env.now
        self.is_healthy = True

        if self.logger:
            self.logger.log_event("SERVER_RECOVERED", self.env.now, worker_id=self.worker_id)

        # Reset attached controller state upon recovery (DEC-009)
        if self.controller is not None:
            self.controller.reset()

        # Restart service loop
        self._wake_event = self.env.event()
        self._service_process = self.env.process(self._service_loop())

    def get_completed_in_window(
        self,
        window_start: float,
        window_end: float,
        successful_only: bool = False,
        timeout_ms: Optional[float] = None,
    ) -> List[Request]:
        """Returns requests completed on this worker in the time range [window_start, window_end]."""
        # Iterate in reverse because requests are appended chronologically
        res: List[Request] = []
        for req in reversed(self.completed_requests):
            if req.t_completed is None:
                continue
            if req.t_completed < window_start:
                break
            if req.t_completed <= window_end:
                if successful_only and timeout_ms is not None:
                    if req.total_latency is not None and req.total_latency > timeout_ms:
                        continue
                res.append(req)
        return res

    def get_head_of_line_wait_time(self, current_time: float) -> float:
        """Returns queue wait time of the head-of-line request, or 0.0 if queue is empty."""
        if self.queue:
            return current_time - self.queue[0].t_arrive
        return 0.0

    def finalize_operational_time(self, sim_end_time: float) -> None:
        """Finalize total operational time and downtime tracking at the end of simulation."""
        if self.is_healthy:
            self.total_operational_time += sim_end_time - self.last_status_change_time
            self.last_status_change_time = sim_end_time
        elif self._current_crash_start is not None:
            self.downtime_intervals.append((self._current_crash_start, sim_end_time))
            self._current_crash_start = None

    def get_downtime_in_window(self, window_start: float, window_end: float) -> float:
        """Returns total downtime duration (ms) of this worker within [window_start, window_end]."""
        total_dt = 0.0
        for c_start, c_end in self.downtime_intervals:
            overlap_start = max(window_start, c_start)
            overlap_end = min(window_end, c_end)
            if overlap_end > overlap_start:
                total_dt += (overlap_end - overlap_start)
        if not self.is_healthy and self._current_crash_start is not None:
            overlap_start = max(window_start, self._current_crash_start)
            overlap_end = window_end
            if overlap_end > overlap_start:
                total_dt += (overlap_end - overlap_start)
        return total_dt

    def is_fully_operational_in_window(self, window_start: float, window_end: float) -> bool:
        """Returns True if the worker experienced zero downtime within [window_start, window_end]."""
        return self.get_downtime_in_window(window_start, window_end) == 0.0

    def get_utilization_ratio(self, current_time: Optional[float] = None) -> float:
        """Returns worker CPU utilization as a ratio in [0.0, 1.0].
        
        Accurately accounts for cumulative busy time over operational time up to current_time,
        including in-flight active service duration if currently processing a request.
        """
        busy = self.total_busy_time
        op = self.total_operational_time

        if current_time is not None and self.is_healthy:
            op += (current_time - self.last_status_change_time)
            if self.in_flight_request is not None and self._current_req_start is not None:
                busy += (current_time - self._current_req_start)

        if op <= 0.0:
            return 0.0
        return min(1.0, max(0.0, busy / op))

    def get_utilization(self, current_time: Optional[float] = None) -> float:
        """Returns worker CPU utilization percentage Ui = (T_busy / T_operational) * 100."""
        return self.get_utilization_ratio(current_time) * 100.0

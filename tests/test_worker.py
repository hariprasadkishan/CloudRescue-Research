"""Unit tests for WorkerInstance model."""

import simpy
import pytest
from simulator.cloudrescue.models.worker import WorkerInstance
from simulator.cloudrescue.models.request import Request, RequestStatus
from simulator.cloudrescue.monitoring.event_logger import EventLogger


def test_worker_queue_capacity():
    """Verify worker drops requests when queue reaches queue_capacity, and accepts new after service starts."""
    env = simpy.Environment()
    logger = EventLogger()
    worker = WorkerInstance(worker_id=0, env=env, queue_capacity=2, logger=logger)

    req1 = Request(1, 0.0, 50.0, 50.0, 0.1, 200.0)
    req2 = Request(2, 0.0, 50.0, 50.0, 0.1, 200.0)
    req3 = Request(3, 0.0, 50.0, 50.0, 0.1, 200.0)

    # Initially queue has capacity 2
    assert worker.enqueue(req1) is True
    assert worker.enqueue(req2) is True
    # At this point, len(queue) == 2 == queue_capacity, so 3rd is dropped
    assert worker.enqueue(req3) is False
    assert req3.status == RequestStatus.DROPPED_QUEUE

    # Step simulation: worker pops req1 into execution, so queue length becomes 1
    env.step()
    assert worker.queue_length == 1
    # Now a new request can be enqueued
    req4 = Request(4, 0.0, 50.0, 50.0, 0.1, 200.0)
    assert worker.enqueue(req4) is True
    assert worker.queue_length == 2


def test_worker_capacity_rejection_isolated():
    """Verify strict queue capacity rejection."""
    env = simpy.Environment()
    logger = EventLogger()
    worker = WorkerInstance(worker_id=0, env=env, queue_capacity=2, logger=logger)

    req1 = Request(1, 0.0, 10.0, 20.0, 0.5, 200.0)
    req2 = Request(2, 0.0, 10.0, 20.0, 0.5, 200.0)
    req3 = Request(3, 0.0, 10.0, 20.0, 0.5, 200.0)

    assert worker.enqueue(req1) is True
    assert worker.enqueue(req2) is True
    assert worker.enqueue(req3) is False
    assert req3.status == RequestStatus.DROPPED_QUEUE


def test_worker_execution_lifecycle():
    """Verify mandatory and optional stage execution with theta=1.0."""
    env = simpy.Environment()
    logger = EventLogger()
    worker = WorkerInstance(worker_id=0, env=env, queue_capacity=5, logger=logger)

    # Mandatory = 10 ms, Optional = 20 ms, Total = 30 ms
    req = Request(1, 0.0, 10.0, 20.0, 0.2, 200.0)
    worker.enqueue(req)

    env.run(until=50.0)

    assert req.status == RequestStatus.COMPLETED
    assert req.t_mand_start == 0.0
    assert req.t_mand_end == 10.0
    assert req.t_opt_start == 10.0
    assert req.t_opt_end == 30.0
    assert req.t_completed == 30.0
    assert req.opt_executed is True
    assert req.total_latency == 30.0
    assert worker.total_busy_time == 30.0


def test_worker_head_of_line_timeout_drop():
    """Verify request dropped at head of line if queue wait time > timeout."""
    env = simpy.Environment()
    logger = EventLogger()
    worker = WorkerInstance(worker_id=0, env=env, queue_capacity=5, logger=logger)

    # First request takes 150 ms
    req1 = Request(1, 0.0, 100.0, 50.0, 0.5, 300.0)
    # Second request arrives at t=0 with timeout=100 ms
    req2 = Request(2, 0.0, 10.0, 10.0, 0.5, 100.0)

    worker.enqueue(req1)
    worker.enqueue(req2)

    # Run until after req1 finishes (t=150.0)
    env.run(until=200.0)

    assert req1.status == RequestStatus.COMPLETED
    # When req2 is popped at t=150.0, wait_time = 150.0 - 0.0 = 150.0 > 100.0 timeout
    assert req2.status == RequestStatus.DROPPED_TIMEOUT
    assert req2.t_mand_start is None


def test_worker_crash_and_recovery():
    """Verify worker crash stops execution, drops queued requests, and recovers cleanly."""
    env = simpy.Environment()
    logger = EventLogger()
    worker = WorkerInstance(worker_id=0, env=env, queue_capacity=5, logger=logger)

    req1 = Request(1, 0.0, 50.0, 50.0, 0.5, 200.0)
    req2 = Request(2, 0.0, 20.0, 20.0, 0.5, 200.0)

    worker.enqueue(req1)
    worker.enqueue(req2)

    # Crash at t=25 ms while req1 is in mandatory processing
    def crash_trigger():
        yield env.timeout(25.0)
        worker.crash()

    env.process(crash_trigger())
    env.run(until=60.0)

    assert worker.is_healthy is False
    assert req1.status == RequestStatus.FAILED_CRASH
    assert req2.status == RequestStatus.FAILED_CRASH
    assert len(worker.queue) == 0

    # New request enqueued while down should be rejected
    req3 = Request(3, 60.0, 10.0, 10.0, 0.5, 200.0)
    assert worker.enqueue(req3) is False
    assert req3.status == RequestStatus.DROPPED_QUEUE

    # Recover worker at t=70 ms
    worker.recover()
    assert worker.is_healthy is True

    req4 = Request(4, 70.0, 10.0, 10.0, 0.5, 200.0)
    assert worker.enqueue(req4) is True

    env.run(until=100.0)
    assert req4.status == RequestStatus.COMPLETED

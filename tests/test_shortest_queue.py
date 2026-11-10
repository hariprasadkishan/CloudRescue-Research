"""Unit tests for JoinShortestQueueBalancer."""

import simpy
import pytest
from simulator.cloudrescue.models.worker import WorkerInstance
from simulator.cloudrescue.models.request import Request
from simulator.cloudrescue.balancing.shortest_queue import JoinShortestQueueBalancer


def test_jsq_routing_to_shortest():
    """Verify JSQ selects the worker with the fewest queued items."""
    env = simpy.Environment()
    w0 = WorkerInstance(0, env, queue_capacity=10)
    w1 = WorkerInstance(1, env, queue_capacity=10)
    w2 = WorkerInstance(2, env, queue_capacity=10)

    balancer = JoinShortestQueueBalancer([w0, w1, w2])

    req = Request(1, 0.0, 10.0, 10.0, 0.5, 200.0)

    # All queues empty -> ties broken by lowest worker_id (w0)
    chosen = balancer.select_worker(req)
    assert chosen == w0
    w0.enqueue(req)

    # Now w0 has length 1, w1 and w2 have length 0 -> lowest tie is w1
    req2 = Request(2, 0.0, 10.0, 10.0, 0.5, 200.0)
    chosen = balancer.select_worker(req2)
    assert chosen == w1
    w1.enqueue(req2)

    # Now w0 and w1 have length 1, w2 has length 0 -> w2
    req3 = Request(3, 0.0, 10.0, 10.0, 0.5, 200.0)
    chosen = balancer.select_worker(req3)
    assert chosen == w2


def test_jsq_excludes_crashed_workers():
    """Verify JSQ ignores crashed workers even if their queue length is 0."""
    env = simpy.Environment()
    w0 = WorkerInstance(0, env, queue_capacity=10)
    w1 = WorkerInstance(1, env, queue_capacity=10)

    balancer = JoinShortestQueueBalancer([w0, w1])

    w0.crash()
    assert not w0.is_healthy

    req = Request(1, 0.0, 10.0, 10.0, 0.5, 200.0)
    chosen = balancer.select_worker(req)

    assert chosen == w1


def test_jsq_all_workers_offline():
    """Verify JSQ returns None when all workers are offline."""
    env = simpy.Environment()
    w0 = WorkerInstance(0, env, queue_capacity=10)
    w1 = WorkerInstance(1, env, queue_capacity=10)

    balancer = JoinShortestQueueBalancer([w0, w1])

    w0.crash()
    w1.crash()

    req = Request(1, 0.0, 10.0, 10.0, 0.5, 200.0)
    chosen = balancer.select_worker(req)

    assert chosen is None

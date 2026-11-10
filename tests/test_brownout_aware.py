"""Unit and integration tests for Brownout-Aware Load Balancing (BALB) and CFG-C."""

import simpy
import pytest
import numpy as np

from simulator.cloudrescue.config import SimulationConfig
from simulator.cloudrescue.models.worker import WorkerInstance
from simulator.cloudrescue.models.request import Request
from simulator.cloudrescue.balancing.brownout_aware import BrownoutAwareLoadBalancer
from simulator.cloudrescue.balancing.shortest_queue import JoinShortestQueueBalancer
from simulator.cloudrescue.engine.simulation import SimulationEngine
from simulator.cloudrescue.monitoring.event_logger import EventLogger


def _create_mock_worker(
    worker_id: int,
    env: simpy.Environment,
    queue_capacity: int = 50,
    theta: float = 1.0,
    queue_len: int = 0,
    busy_ratio: float = 0.0,
    is_healthy: bool = True,
) -> WorkerInstance:
    """Helper to instantiate and configure a worker with specified mock attributes."""
    w = WorkerInstance(worker_id=worker_id, env=env, queue_capacity=queue_capacity)
    w.current_theta = theta
    w.is_healthy = is_healthy

    # Populate queue
    for i in range(queue_len):
        w.queue.append(Request(1000 + i, 0.0, 10.0, 10.0, 0.5, 200.0))

    # Set mock operational and busy times to yield desired busy_ratio
    w.total_operational_time = 1000.0
    w.total_busy_time = 1000.0 * busy_ratio
    w.last_status_change_time = env.now
    return w


def test_balb_score_calculation_direct():
    """Verify that BALB score matches the exact research formula:
    Score_i = alpha * theta_i - beta * (q_i / Q_max) - gamma * U_i
    """
    env = simpy.Environment()
    config = SimulationConfig(
        balb_alpha=1.0,
        balb_beta=1.0,
        balb_gamma=0.5,
        queue_capacity=50,
    )
    # theta = 0.8, q = 10 (q/Q_max = 0.20), U = 0.40
    # Expected: 1.0 * 0.8 - 1.0 * 0.20 - 0.5 * 0.40 = 0.80 - 0.20 - 0.20 = 0.40
    w = _create_mock_worker(0, env, queue_capacity=50, theta=0.8, queue_len=10, busy_ratio=0.40)
    balancer = BrownoutAwareLoadBalancer([w], config)

    score = balancer.calculate_score(w)
    assert score == pytest.approx(0.40, rel=1e-5)


def test_balb_selects_highest_score_worker():
    """Verify BALB routes to the worker with the highest composite utility score."""
    env = simpy.Environment()
    config = SimulationConfig(balb_alpha=1.0, balb_beta=1.0, balb_gamma=0.5, queue_capacity=50)

    # Worker 0: theta=0.6, q=10, U=0.4 -> Score = 0.6 - 0.20 - 0.20 = 0.20
    # Worker 1: theta=1.0, q=5,  U=0.3 -> Score = 1.0 - 0.10 - 0.15 = 0.75
    # Worker 2: theta=0.9, q=15, U=0.2 -> Score = 0.9 - 0.30 - 0.10 = 0.50
    w0 = _create_mock_worker(0, env, theta=0.6, queue_len=10, busy_ratio=0.4)
    w1 = _create_mock_worker(1, env, theta=1.0, queue_len=5,  busy_ratio=0.3)
    w2 = _create_mock_worker(2, env, theta=0.9, queue_len=15, busy_ratio=0.2)

    balancer = BrownoutAwareLoadBalancer([w0, w1, w2], config)
    req = Request(1, 0.0, 10.0, 10.0, 0.5, 200.0)

    chosen = balancer.select_worker(req)
    assert chosen == w1
    assert chosen.worker_id == 1


def test_balb_theta_affects_selection():
    """Verify that worker with higher dimmer is selected when queue and utilization are identical."""
    env = simpy.Environment()
    config = SimulationConfig(balb_alpha=1.0, balb_beta=1.0, balb_gamma=0.5, queue_capacity=50)

    # Identical queue (q=0) and utilization (U=0.10)
    # w0 has theta=0.4 -> Score = 0.40 - 0 - 0.05 = 0.35
    # w1 has theta=0.9 -> Score = 0.90 - 0 - 0.05 = 0.85
    w0 = _create_mock_worker(0, env, theta=0.4, queue_len=0, busy_ratio=0.10)
    w1 = _create_mock_worker(1, env, theta=0.9, queue_len=0, busy_ratio=0.10)

    balancer = BrownoutAwareLoadBalancer([w0, w1], config)
    req = Request(1, 0.0, 10.0, 10.0, 0.5, 200.0)

    chosen = balancer.select_worker(req)
    assert chosen == w1


def test_balb_queue_depth_affects_selection():
    """Verify that worker with smaller queue backlog is selected when theta and utilization are identical."""
    env = simpy.Environment()
    config = SimulationConfig(balb_alpha=1.0, balb_beta=1.0, balb_gamma=0.5, queue_capacity=50)

    # Identical theta=1.0 and utilization U=0.20
    # w0 has q=25 -> Score = 1.0 - 0.50 - 0.10 = 0.40
    # w1 has q=5  -> Score = 1.0 - 0.10 - 0.10 = 0.80
    w0 = _create_mock_worker(0, env, theta=1.0, queue_len=25, busy_ratio=0.20)
    w1 = _create_mock_worker(1, env, theta=1.0, queue_len=5,  busy_ratio=0.20)

    balancer = BrownoutAwareLoadBalancer([w0, w1], config)
    req = Request(1, 0.0, 10.0, 10.0, 0.5, 200.0)

    chosen = balancer.select_worker(req)
    assert chosen == w1


def test_balb_utilization_affects_selection_independently():
    """Verify that CPU utilization independently influences routing decisions when queue and theta are equal.
    
    Confirms queue depth is NOT a substitute for CPU capacity.
    """
    env = simpy.Environment()
    config = SimulationConfig(balb_alpha=1.0, balb_beta=1.0, balb_gamma=0.5, queue_capacity=50)

    # Identical theta=1.0 and identical queue backlog q=10
    # w0: U=0.90 (heavily loaded processor) -> Score = 1.0 - 0.20 - 0.5*0.90 = 0.35
    # w1: U=0.10 (idle processor)            -> Score = 1.0 - 0.20 - 0.5*0.10 = 0.75
    w0 = _create_mock_worker(0, env, theta=1.0, queue_len=10, busy_ratio=0.90)
    w1 = _create_mock_worker(1, env, theta=1.0, queue_len=10, busy_ratio=0.10)

    balancer = BrownoutAwareLoadBalancer([w0, w1], config)
    req = Request(1, 0.0, 10.0, 10.0, 0.5, 200.0)

    chosen = balancer.select_worker(req)
    assert chosen == w1


def test_balb_crashed_worker_exclusion():
    """Verify crashed/offline workers are immediately excluded from selection even if their score would be highest."""
    env = simpy.Environment()
    config = SimulationConfig(balb_alpha=1.0, balb_beta=1.0, balb_gamma=0.5, queue_capacity=50)

    # w0 has perfect score but is crashed
    w0 = _create_mock_worker(0, env, theta=1.0, queue_len=0, busy_ratio=0.0, is_healthy=False)
    # w1 is degraded but healthy
    w1 = _create_mock_worker(1, env, theta=0.3, queue_len=10, busy_ratio=0.5, is_healthy=True)

    balancer = BrownoutAwareLoadBalancer([w0, w1], config)
    req = Request(1, 0.0, 10.0, 10.0, 0.5, 200.0)

    chosen = balancer.select_worker(req)
    assert chosen == w1


def test_balb_full_queue_worker_exclusion():
    """Verify saturated workers (q_i >= Q_max) are excluded from selection."""
    env = simpy.Environment()
    config = SimulationConfig(balb_alpha=1.0, balb_beta=1.0, balb_gamma=0.5, queue_capacity=50)

    # w0 has full queue (50/50)
    w0 = _create_mock_worker(0, env, queue_capacity=50, theta=1.0, queue_len=50, busy_ratio=0.1)
    # w1 has room (45/50)
    w1 = _create_mock_worker(1, env, queue_capacity=50, theta=0.5, queue_len=45, busy_ratio=0.1)

    balancer = BrownoutAwareLoadBalancer([w0, w1], config)
    req = Request(1, 0.0, 10.0, 10.0, 0.5, 200.0)

    chosen = balancer.select_worker(req)
    assert chosen == w1

    # When all workers reach Q_max, balancer returns None
    w1.queue.append(Request(2, 0.0, 10.0, 10.0, 0.5, 200.0))
    w1.queue.append(Request(3, 0.0, 10.0, 10.0, 0.5, 200.0))
    w1.queue.append(Request(4, 0.0, 10.0, 10.0, 0.5, 200.0))
    w1.queue.append(Request(5, 0.0, 10.0, 10.0, 0.5, 200.0))
    w1.queue.append(Request(6, 0.0, 10.0, 10.0, 0.5, 200.0))
    assert w1.queue_length == 50

    assert balancer.select_worker(req) is None


def test_balb_soft_overload_fallback():
    """Verify soft overload fallback: when all operational workers have q_i >= Q_soft (40/50),
    alpha is set to 0 to prevent queue drops, routing strictly by shortest queue and utilization.
    """
    env = simpy.Environment()
    config = SimulationConfig(
        balb_alpha=1.0,
        balb_beta=1.0,
        balb_gamma=0.5,
        queue_capacity=50,
        q_soft_ratio=0.8,  # Q_soft = 40
    )

    # Both workers exceed Q_soft (40)
    # Without fallback (alpha=1.0):
    # w0: q=44, theta=1.0, U=0.2 -> Score = 1.0 - (44/50) - 0.10 = +0.02
    # w1: q=41, theta=0.2, U=0.2 -> Score = 0.2 - (41/50) - 0.10 = -0.72  (w0 would be chosen despite being near drop!)
    #
    # With fallback (alpha=0.0):
    # w0: Score = 0 - 0.88 - 0.10 = -0.98
    # w1: Score = 0 - 0.82 - 0.10 = -0.92  (w1 is chosen, shedding load away from saturated w0!)
    w0 = _create_mock_worker(0, env, queue_capacity=50, theta=1.0, queue_len=44, busy_ratio=0.2)
    w1 = _create_mock_worker(1, env, queue_capacity=50, theta=0.2, queue_len=41, busy_ratio=0.2)

    balancer = BrownoutAwareLoadBalancer([w0, w1], config)
    req = Request(1, 0.0, 10.0, 10.0, 0.5, 200.0)

    chosen = balancer.select_worker(req)
    assert chosen == w1
    assert balancer.routing_history[-1].fallback_active is True


def test_balb_deterministic_tie_breaking():
    """Verify deterministic tie-breaking: identical score -> lowest queue length -> lowest worker_id."""
    env = simpy.Environment()
    config = SimulationConfig(balb_alpha=1.0, balb_beta=1.0, balb_gamma=0.5, queue_capacity=50)

    # w0 and w1 have identical scores
    w0 = _create_mock_worker(0, env, theta=0.8, queue_len=10, busy_ratio=0.2)
    w1 = _create_mock_worker(1, env, theta=0.8, queue_len=10, busy_ratio=0.2)

    balancer = BrownoutAwareLoadBalancer([w0, w1], config)
    req = Request(1, 0.0, 10.0, 10.0, 0.5, 200.0)

    chosen = balancer.select_worker(req)
    # Lowest worker_id wins tie
    assert chosen == w0


def test_balb_invalid_configuration_rejection():
    """Verify that negative weights or invalid q_soft_ratio raise ValueError."""
    with pytest.raises(ValueError):
        SimulationConfig(balb_alpha=-0.5).validate()

    with pytest.raises(ValueError):
        SimulationConfig(balb_beta=-1.0).validate()

    with pytest.raises(ValueError):
        SimulationConfig(balb_gamma=-0.1).validate()

    with pytest.raises(ValueError):
        SimulationConfig(q_soft_ratio=0.0).validate()

    with pytest.raises(ValueError):
        SimulationConfig(q_soft_ratio=1.5).validate()

    with pytest.raises(ValueError):
        SimulationConfig(routing_policy="INVALID_POLICY").validate()


def test_cfg_a_and_cfg_b_regression_behavior():
    """Verify CFG-A and CFG-B behavior remains strictly unchanged and uses JSQ."""
    # CFG-A: brownout disabled, JSQ balancer
    cfg_a = SimulationConfig(mode="CFG-A", sim_time_ms=2000.0, warmup_ms=200.0, lambda_nom=0.05, seed=42)
    eng_a = SimulationEngine(cfg_a)
    assert isinstance(eng_a.balancer, JoinShortestQueueBalancer)
    assert len(eng_a.controllers) == 0

    # CFG-B: brownout enabled, JSQ balancer
    cfg_b = SimulationConfig(mode="CFG-B", sim_time_ms=2000.0, warmup_ms=200.0, lambda_nom=0.05, seed=42)
    eng_b = SimulationEngine(cfg_b)
    assert isinstance(eng_b.balancer, JoinShortestQueueBalancer)
    assert len(eng_b.controllers) == 4

    # CFG-C: brownout enabled, BALB balancer
    cfg_c = SimulationConfig(mode="CFG-C", sim_time_ms=2000.0, warmup_ms=200.0, lambda_nom=0.05, seed=42)
    eng_c = SimulationEngine(cfg_c)
    assert isinstance(eng_c.balancer, BrownoutAwareLoadBalancer)
    assert len(eng_c.controllers) == 4


def test_cfg_c_reproducibility():
    """Verify CFG-C reproducibility: identical seed produces identical metrics, events, and BALB decisions."""
    cfg1 = SimulationConfig(
        mode="CFG-C",
        num_workers=4,
        sim_time_ms=4000.0,
        warmup_ms=500.0,
        lambda_nom=0.08,
        seed=888,
    )
    cfg2 = SimulationConfig(
        mode="CFG-C",
        num_workers=4,
        sim_time_ms=4000.0,
        warmup_ms=500.0,
        lambda_nom=0.08,
        seed=888,
    )

    res1 = SimulationEngine(cfg1).run()
    res2 = SimulationEngine(cfg2).run()

    assert res1.metrics == res2.metrics
    assert res1.worker_utilizations == res2.worker_utilizations
    assert res1.jains_index == res2.jains_index

    # Compare BALB routing decision history
    diag1 = res1.balb_diagnostics
    diag2 = res2.balb_diagnostics
    assert diag1 is not None and diag2 is not None
    assert len(diag1) == len(diag2)
    assert (diag1["selected_worker_id"].values == diag2["selected_worker_id"].values).all()

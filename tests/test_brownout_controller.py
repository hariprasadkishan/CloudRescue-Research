"""Unit and integration tests for BrownoutController and CFG-B execution."""

import simpy
import pytest
import numpy as np

from simulator.cloudrescue.config import SimulationConfig
from simulator.cloudrescue.models.worker import WorkerInstance
from simulator.cloudrescue.models.request import Request, RequestStatus
from simulator.cloudrescue.control.brownout_controller import BrownoutController
from simulator.cloudrescue.monitoring.event_logger import EventLogger
from simulator.cloudrescue.engine.simulation import SimulationEngine


def _helper_add_completed_requests(worker: WorkerInstance, count: int, latency_ms: float, t_completed: float = 1000.0):
    """Helper to populate worker with simulated completed requests."""
    for i in range(count):
        req = Request(
            request_id=100 + i,
            t_arrive=t_completed - latency_ms,
            s_mand=latency_ms / 2.0,
            s_opt=latency_ms / 2.0,
            u_opt=0.5,
            timeout=500.0,
        )
        req.t_completed = t_completed
        req.status = RequestStatus.COMPLETED
        worker.completed_requests.append(req)


def test_controller_high_latency_decreases_theta():
    """Verify that when p95 latency exceeds target latency (80 ms), theta decreases."""
    env = simpy.Environment()
    logger = EventLogger()
    config = SimulationConfig(
        target_latency_ms=80.0,
        ctrl_interval_ms=1000.0,
        kp=0.5,
        ki=0.1,
        n_min_ctrl=5,
    )
    worker = WorkerInstance(0, env, queue_capacity=10, logger=logger)
    ctrl = BrownoutController(worker, config, logger)
    worker.attach_controller(ctrl)

    # Populate 10 requests completing in [0, 1000] ms with latency = 160 ms (> 80 ms target)
    _helper_add_completed_requests(worker, count=10, latency_ms=160.0, t_completed=1000.0)

    res = ctrl.step(1000.0)

    assert res.status == "updated"
    assert res.measured_p95_ms == 160.0
    assert res.error_s == pytest.approx((80.0 - 160.0) / 1000.0, rel=1e-4)  # -0.08 s
    assert res.new_theta < res.old_theta
    assert ctrl.current_theta < 1.0


def test_controller_low_latency_restores_theta():
    """Verify that when p95 latency is below target latency (80 ms), theta gradually increases."""
    env = simpy.Environment()
    logger = EventLogger()
    config = SimulationConfig(
        target_latency_ms=80.0,
        ctrl_interval_ms=1000.0,
        kp=0.5,
        ki=0.1,
        n_min_ctrl=5,
    )
    worker = WorkerInstance(0, env, queue_capacity=10, logger=logger)
    ctrl = BrownoutController(worker, config, logger)
    worker.attach_controller(ctrl)

    # Start controller from degraded state theta = 0.5
    ctrl.current_theta = 0.5
    worker.current_theta = 0.5

    # Populate 10 requests completing in [0, 1000] ms with low latency = 40 ms (< 80 ms target)
    _helper_add_completed_requests(worker, count=10, latency_ms=40.0, t_completed=1000.0)

    res = ctrl.step(1000.0)

    assert res.status == "updated"
    assert res.measured_p95_ms == 40.0
    assert res.error_s == pytest.approx((80.0 - 40.0) / 1000.0, rel=1e-4)  # +0.04 s
    assert res.new_theta > res.old_theta
    assert ctrl.current_theta > 0.5


def test_controller_clamping_bounds():
    """Verify that theta is strictly clamped within [0.0, 1.0] under extreme stress and headroom."""
    env = simpy.Environment()
    config = SimulationConfig(
        target_latency_ms=80.0,
        ctrl_interval_ms=1000.0,
        kp=0.5,
        ki=0.1,
        n_min_ctrl=5,
    )
    worker = WorkerInstance(0, env, queue_capacity=10)
    ctrl = BrownoutController(worker, config)
    worker.attach_controller(ctrl)

    # 1. Catastrophic overload: latency = 5000 ms over multiple steps
    for step_num in range(1, 30):
        t = step_num * 1000.0
        _helper_add_completed_requests(worker, count=10, latency_ms=5000.0, t_completed=t)
        ctrl.step(t)
        assert ctrl.current_theta >= 0.0

    assert ctrl.current_theta == 0.0

    # 2. Perfect headroom: latency = 1 ms over multiple steps
    for step_num in range(31, 100):
        t = step_num * 1000.0
        _helper_add_completed_requests(worker, count=10, latency_ms=1.0, t_completed=t)
        ctrl.step(t)
        assert ctrl.current_theta <= 1.0

    assert ctrl.current_theta == 1.0


def test_controller_insufficient_samples_hold():
    """Verify that when samples < N_min_ctrl, PI update is skipped and theta held constant."""
    env = simpy.Environment()
    config = SimulationConfig(n_min_ctrl=5)
    worker = WorkerInstance(0, env, queue_capacity=10)
    ctrl = BrownoutController(worker, config)
    worker.attach_controller(ctrl)
    ctrl.current_theta = 0.75

    # Only 2 requests completed in interval
    _helper_add_completed_requests(worker, count=2, latency_ms=150.0, t_completed=1000.0)

    res = ctrl.step(1000.0)

    assert res.status == "held_insufficient_samples"
    assert res.new_theta == 0.75
    assert ctrl.prev_error_s is None


def test_controller_derivative_kick_prevention():
    """Verify that the first valid update after missing data sets prev_error = error,
    so derivative kick Kp * (e - prev_error) evaluates to zero.
    """
    env = simpy.Environment()
    config = SimulationConfig(
        target_latency_ms=80.0,
        ctrl_interval_ms=1000.0,
        kp=0.5,
        ki=0.1,
        n_min_ctrl=5,
    )
    worker = WorkerInstance(0, env, queue_capacity=10)
    ctrl = BrownoutController(worker, config)
    worker.attach_controller(ctrl)
    ctrl.current_theta = 1.0
    ctrl.prev_error_s = None  # Resumption state

    # 10 requests with latency 120 ms => error = (80 - 120)/1000 = -0.04 s
    _helper_add_completed_requests(worker, count=10, latency_ms=120.0, t_completed=1000.0)

    res = ctrl.step(1000.0)

    assert res.status == "updated"
    # Expected change: delta_p = 0.5 * (-0.04 - (-0.04)) = 0.0
    # delta_i = 0.1 * (-0.04) * 1.0 = -0.004
    # Total change should be exactly delta_i
    expected_delta = 0.1 * (-0.04) * 1.0
    expected_theta = 1.0 + expected_delta
    assert res.new_theta == pytest.approx(expected_theta, rel=1e-4)


def test_controller_stalled_queue_safety_decrement():
    """Verify that when samples < 5 but queue > 0 with wait > r_target,
    the controller detects stall and decrements theta by delta_stall (0.05).
    """
    env = simpy.Environment()
    config = SimulationConfig(
        target_latency_ms=80.0,
        ctrl_interval_ms=1000.0,
        delta_stall=0.05,
        n_min_ctrl=5,
    )
    worker = WorkerInstance(0, env, queue_capacity=10)
    ctrl = BrownoutController(worker, config)
    worker.attach_controller(ctrl)
    ctrl.current_theta = 0.90

    # Zero completed requests in window
    # But queue contains request that arrived at t = 500 ms with current time = 1000 ms
    # Waiting time = 1000 - 500 = 500 ms > 80 ms target
    stalled_req = Request(1, 500.0, 50.0, 50.0, 0.5, 1000.0)
    worker.queue.append(stalled_req)

    res = ctrl.step(1000.0)

    assert res.status == "stalled_queue_decrement"
    assert res.new_theta == pytest.approx(0.85, rel=1e-4)
    assert ctrl.current_theta == pytest.approx(0.85, rel=1e-4)
    assert ctrl.prev_error_s is None


def test_worker_optional_execution_with_theta():
    """Verify that optional computation executes iff U_opt <= current_theta."""
    env = simpy.Environment()
    logger = EventLogger()
    worker = WorkerInstance(0, env, queue_capacity=5, logger=logger)
    # Set dimmer to 0.60
    worker.current_theta = 0.60

    # Req 1: U_opt = 0.40 <= 0.60 -> executes optional
    req1 = Request(1, 0.0, 10.0, 20.0, 0.40, 200.0)
    # Req 2: U_opt = 0.75 > 0.60 -> bypasses optional
    req2 = Request(2, 0.0, 10.0, 20.0, 0.75, 200.0)

    worker.enqueue(req1)
    worker.enqueue(req2)

    env.run(until=100.0)

    assert req1.status == RequestStatus.COMPLETED
    assert req1.opt_executed is True
    assert req1.total_latency == 30.0  # 10 mand + 20 opt

    assert req2.status == RequestStatus.COMPLETED
    assert req2.opt_executed is False
    assert req2.total_latency == 40.0  # 30 ms queue wait + 10 ms mand only

    # Check event logging
    df = logger.to_dataframe()
    opt_exec = df[df["event_type"] == "OPTIONAL_EXECUTED"]
    opt_byp = df[df["event_type"] == "OPTIONAL_BYPASSED"]

    assert len(opt_exec) == 1
    assert opt_exec.iloc[0]["request_id"] == 1
    assert opt_exec.iloc[0]["theta"] == 0.60

    assert len(opt_byp) == 1
    assert opt_byp.iloc[0]["request_id"] == 2
    assert opt_byp.iloc[0]["theta"] == 0.60


def test_mandatory_computation_always_executes():
    """Verify that mandatory computation is never bypassed, even when theta = 0.0."""
    env = simpy.Environment()
    logger = EventLogger()
    worker = WorkerInstance(0, env, queue_capacity=5, logger=logger)
    worker.current_theta = 0.0  # Full feature degradation

    req = Request(1, 0.0, 15.0, 30.0, 0.1, 200.0)
    worker.enqueue(req)

    env.run(until=50.0)

    assert req.status == RequestStatus.COMPLETED
    assert req.t_mand_start == 0.0
    assert req.t_mand_end == 15.0
    assert req.opt_executed is False
    assert req.total_latency == 15.0


def test_worker_crash_and_recovery_controller_reset():
    """Verify that worker crash suspends updates, and recovery resets controller to nominal (theta=1.0)."""
    env = simpy.Environment()
    config = SimulationConfig()
    worker = WorkerInstance(0, env, queue_capacity=5)
    ctrl = BrownoutController(worker, config)
    worker.attach_controller(ctrl)

    # Degrade theta
    ctrl.current_theta = 0.40
    worker.current_theta = 0.40

    # Worker crashes
    worker.crash()
    res = ctrl.step(1000.0)
    assert res.status == "offline"

    # Worker recovers -> controller should reset to theta=1.0 and prev_error=None
    worker.recover()
    assert worker.is_healthy is True
    assert ctrl.current_theta == 1.0
    assert worker.current_theta == 1.0
    assert ctrl.prev_error_s is None


def test_cfg_b_end_to_end_simulation():
    """Verify CFG-B simulation runs with active brownout adaptation."""
    config = SimulationConfig(
        mode="CFG-B",
        enable_brownout=True,
        num_workers=4,
        sim_time_ms=5000.0,
        warmup_ms=500.0,
        lambda_nom=0.08,  # 80 req/s
        seed=42,
    )
    engine = SimulationEngine(config)
    res = engine.run()

    assert res.config.enable_brownout is True
    assert len(res.controllers) == 4
    assert res.metrics["n_submitted"] > 0
    assert res.metrics["n_success"] > 0

    # Verify controller update events were logged
    df = res.logger.to_dataframe()
    ctrl_updates = df[df["event_type"] == "CONTROLLER_UPDATED"]
    assert len(ctrl_updates) > 0

    # Controller timeseries should be non-empty
    ts_df = res.logger.get_controller_timeseries()
    assert len(ts_df) == len(ctrl_updates)
    assert "new_theta" in ts_df.columns


def test_cfg_a_unchanged_behavior():
    """Verify CFG-A (Baseline) remains unchanged: zero controller updates, theta=1.0, fidelity=100%."""
    config = SimulationConfig(
        mode="CFG-A",
        enable_brownout=False,
        num_workers=4,
        sim_time_ms=4000.0,
        warmup_ms=500.0,
        lambda_nom=0.05,
        seed=123,
    )
    engine = SimulationEngine(config)
    res = engine.run()

    assert res.config.enable_brownout is False
    assert len(res.controllers) == 0
    assert res.metrics["fidelity_percent"] == 100.0
    assert res.metrics["mean_dimmer"] == 1.0

    df = res.logger.to_dataframe()
    assert len(df[df["event_type"] == "CONTROLLER_UPDATED"]) == 0
    assert len(df[df["event_type"] == "OPTIONAL_BYPASSED"]) == 0


def test_cfg_b_reproducibility():
    """Verify CFG-B reproducibility: identical seeds produce identical controller trajectories and metrics."""
    config1 = SimulationConfig(
        mode="CFG-B",
        enable_brownout=True,
        num_workers=4,
        sim_time_ms=4000.0,
        warmup_ms=500.0,
        lambda_nom=0.08,
        seed=777,
    )
    config2 = SimulationConfig(
        mode="CFG-B",
        enable_brownout=True,
        num_workers=4,
        sim_time_ms=4000.0,
        warmup_ms=500.0,
        lambda_nom=0.08,
        seed=777,
    )

    res1 = SimulationEngine(config1).run()
    res2 = SimulationEngine(config2).run()

    assert res1.metrics == res2.metrics
    df1 = res1.logger.get_controller_timeseries()
    df2 = res2.logger.get_controller_timeseries()
    assert len(df1) == len(df2)
    assert (df1["new_theta"].values == df2["new_theta"].values).all()

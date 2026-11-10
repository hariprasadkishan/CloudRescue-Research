"""Unit tests for WorkloadGenerator and multi-stream PRNG reproducibility."""

import pytest
from simulator.cloudrescue.config import SimulationConfig
from simulator.cloudrescue.workload.generator import WorkloadGenerator


def test_workload_seed_determinism():
    """Verify that identical seed produces identical sequence of requests."""
    config1 = SimulationConfig(seed=12345, sim_time_ms=5000.0, lambda_nom=0.05)
    config2 = SimulationConfig(seed=12345, sim_time_ms=5000.0, lambda_nom=0.05)

    gen1 = WorkloadGenerator(config1)
    gen2 = WorkloadGenerator(config2)

    reqs1 = gen1.generate_requests()
    reqs2 = gen2.generate_requests()

    assert len(reqs1) == len(reqs2)
    for r1, r2 in zip(reqs1, reqs2):
        assert r1.request_id == r2.request_id
        assert r1.t_arrive == r2.t_arrive
        assert r1.s_mand == r2.s_mand
        assert r1.s_opt == r2.s_opt
        assert r1.u_opt == r2.u_opt


def test_workload_stream_isolation():
    """Verify that changing service parameters does not alter arrival timestamps.
    
    This guarantees that Stream 1 (Arrivals) is isolated from Stream 2 (Service times).
    """
    config1 = SimulationConfig(seed=42, sim_time_ms=5000.0, mu_mand=0.1, mu_opt=0.033)
    config2 = SimulationConfig(seed=42, sim_time_ms=5000.0, mu_mand=0.5, mu_opt=0.200)

    gen1 = WorkloadGenerator(config1)
    gen2 = WorkloadGenerator(config2)

    reqs1 = gen1.generate_requests()
    reqs2 = gen2.generate_requests()

    assert len(reqs1) == len(reqs2)
    for r1, r2 in zip(reqs1, reqs2):
        # Arrival timestamps must be 100% identical
        assert r1.t_arrive == r2.t_arrive
        # But service times should differ due to different rates
        assert r1.s_mand != r2.s_mand
        assert r1.s_opt != r2.s_opt
        # While u_opt remains identical (same draws from Stream 4)
        assert r1.u_opt == r2.u_opt


def test_workload_burst_rate():
    """Verify that arrival rate surges during the burst window."""
    config = SimulationConfig(
        seed=100,
        sim_time_ms=10000.0,
        lambda_nom=0.02,       # 20 req/s = 0.02 req/ms
        lambda_burst=0.10,     # 100 req/s = 0.10 req/ms (5x surge)
        burst_start_ms=3000.0,
        burst_duration_ms=2000.0,  # 3000 - 5000 ms
    )
    gen = WorkloadGenerator(config)
    reqs = gen.generate_requests()

    pre_burst = [r for r in reqs if r.t_arrive < 3000.0]
    during_burst = [r for r in reqs if 3000.0 <= r.t_arrive < 5000.0]

    # Pre-burst rate (duration 3000 ms)
    rate_pre = len(pre_burst) / 3000.0
    # Burst rate (duration 2000 ms)
    rate_burst = len(during_burst) / 2000.0

    # Burst rate should be significantly higher than pre-burst rate
    assert rate_burst > rate_pre * 2.5

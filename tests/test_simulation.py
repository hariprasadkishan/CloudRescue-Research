"""Unit and integration tests for SimulationEngine and CFG-A execution."""

import pytest
from simulator.cloudrescue.config import SimulationConfig, FailureSchedule
from simulator.cloudrescue.engine.simulation import SimulationEngine


def test_simulation_cfg_a_execution():
    """Verify an end-to-end CFG-A baseline simulation run."""
    config = SimulationConfig(
        num_workers=4,
        queue_capacity=50,
        mu_mand=0.1,             # 10 ms
        mu_opt=1.0 / 30.0,       # 30 ms
        timeout_ms=200.0,
        sla_threshold_ms=100.0,
        lambda_nom=0.04,         # 40 req/s = 0.04 req/ms
        sim_time_ms=5000.0,      # 5 seconds
        warmup_ms=500.0,         # 0.5 seconds
        seed=42,
    )

    engine = SimulationEngine(config)
    result = engine.run()

    assert result.total_generated_requests > 0
    assert result.metrics["n_submitted"] > 0
    assert result.metrics["n_success"] > 0
    assert result.metrics["sr_percent"] > 0.0
    assert result.metrics["mean_latency_ms"] > 0.0
    # In CFG-A (Baseline), theta=1.0, so fidelity should be 100%
    assert result.metrics["fidelity_percent"] == 100.0
    assert 0.0 <= result.jains_index <= 1.0


def test_simulation_failure_schedule():
    """Verify that worker crash and recovery events are executed as scheduled."""
    config = SimulationConfig(
        num_workers=4,
        queue_capacity=50,
        lambda_nom=0.04,
        sim_time_ms=6000.0,
        warmup_ms=500.0,
        seed=123,
        fail_schedules=[
            FailureSchedule(worker_ids=[1, 2], t_fail=2000.0, t_repair=4000.0)
        ],
    )

    engine = SimulationEngine(config)
    result = engine.run()

    df = result.logger.to_dataframe()
    crashed_events = df[df["event_type"] == "SERVER_CRASHED"]
    recovered_events = df[df["event_type"] == "SERVER_RECOVERED"]

    # Workers 1 and 2 should both have crashed and recovered
    assert len(crashed_events) == 2
    assert set(crashed_events["worker_id"]) == {1, 2}
    assert len(recovered_events) == 2
    assert set(recovered_events["worker_id"]) == {1, 2}


def test_simulation_reproducibility():
    """Verify that identical configurations and seeds produce identical outputs."""
    config1 = SimulationConfig(
        num_workers=4,
        sim_time_ms=4000.0,
        warmup_ms=500.0,
        seed=999,
        lambda_nom=0.05,
    )
    config2 = SimulationConfig(
        num_workers=4,
        sim_time_ms=4000.0,
        warmup_ms=500.0,
        seed=999,
        lambda_nom=0.05,
    )

    res1 = SimulationEngine(config1).run()
    res2 = SimulationEngine(config2).run()

    assert res1.total_generated_requests == res2.total_generated_requests
    assert res1.metrics == res2.metrics
    assert res1.worker_utilizations == res2.worker_utilizations
    assert res1.jains_index == res2.jains_index

    # Check event-level equality
    df1 = res1.logger.to_dataframe()
    df2 = res2.logger.to_dataframe()
    assert len(df1) == len(df2)
    assert (df1["timestamp"].values == df2["timestamp"].values).all()
    assert (df1["event_type"].values == df2["event_type"].values).all()


def test_simulation_invalid_config():
    """Verify invalid configurations are rejected before startup."""
    with pytest.raises(ValueError):
        SimulationConfig(num_workers=0).validate()

    with pytest.raises(ValueError):
        SimulationConfig(queue_capacity=-5).validate()

    with pytest.raises(ValueError):
        SimulationConfig(timeout_ms=-10.0).validate()

    with pytest.raises(ValueError):
        SimulationConfig(warmup_ms=2000.0, sim_time_ms=1000.0).validate()

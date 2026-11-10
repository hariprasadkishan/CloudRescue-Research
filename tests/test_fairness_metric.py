"""Focused unit tests for Jain's Fairness Index post-warmup and active-worker calculation."""

import pytest
from simulator.cloudrescue.config import SimulationConfig, FailureSchedule
from simulator.cloudrescue.engine.simulation import SimulationEngine


def test_fairness_excludes_warmup_completions():
    """Verify that requests completed during warm-up are strictly excluded from post-warmup fairness."""
    config = SimulationConfig(
        num_workers=4,
        queue_capacity=50,
        lambda_nom=0.08,
        sim_time_ms=4000.0,
        warmup_ms=1000.0,
        seed=42,
    )

    engine = SimulationEngine(config)
    result = engine.run()

    post_warmup_counts = result.metrics["post_warmup_worker_counts"]
    total_post_warmup = sum(post_warmup_counts.values())

    # Total post-warmup count must match n_success exactly
    assert total_post_warmup == result.metrics["n_success"]

    # Total completed requests across all time must be greater than post-warmup completions
    total_all_time = sum(len(w.completed_requests) for w in engine.workers)
    assert total_all_time > total_post_warmup

    # Active workers should be all 4 instances in nominal run
    assert result.active_workers_fairness == [0, 1, 2, 3]
    assert result.fairness_population_type == "strict_zero_downtime"
    assert result.fairness_status == "evaluable"
    assert result.jains_index is not None
    assert 0.0 <= result.jains_index <= 1.0


def test_fairness_active_worker_selection_on_failure():
    """Verify that crashed workers are excluded from M_active to avoid penalizing hardware outages."""
    config = SimulationConfig(
        num_workers=4,
        queue_capacity=50,
        lambda_nom=0.08,
        sim_time_ms=5000.0,
        warmup_ms=500.0,
        seed=42,
        fail_schedules=[
            FailureSchedule(worker_ids=[1, 2], t_fail=1000.0, t_repair=3500.0)
        ],
    )

    engine = SimulationEngine(config)
    result = engine.run()

    # Workers 1 and 2 experienced downtime in the [500, 5000] window
    # Therefore, M_active must be [0, 3] with strict zero-downtime classification
    assert result.active_workers_fairness == [0, 3]
    assert result.fairness_population_type == "strict_zero_downtime"
    assert result.fairness_status == "evaluable"

    # Jain's index must be computed over workers 0 and 3
    counts_0_3 = [result.metrics["post_warmup_worker_counts"][0], result.metrics["post_warmup_worker_counts"][3]]
    sum_c = sum(counts_0_3)
    expected_j = round(float((sum_c ** 2) / (2 * sum(c * c for c in counts_0_3))), 4)
    assert result.jains_index == expected_j

    # Cluster-wide metric includes crashed workers 1 and 2
    assert "jains_fairness_index_all_workers" in result.metrics
    assert result.jains_index_all_workers is not None
    assert 0.0 <= result.jains_index_all_workers <= 1.0


def test_fairness_zero_completions_safe_handling():
    """Verify that zero completions post-warmup is flagged as undefined rather than falsely claiming 1.0."""
    # Use extremely low arrival rate and tiny window so 0 requests complete
    config = SimulationConfig(
        num_workers=4,
        queue_capacity=50,
        lambda_nom=0.00001,
        sim_time_ms=200.0,
        warmup_ms=100.0,
        seed=999,
    )

    engine = SimulationEngine(config)
    result = engine.run()

    # Zero completions: jains_index must be None and flagged as undefined_zero_completions
    assert result.jains_index is None
    assert result.fairness_status == "undefined_zero_completions"
    assert result.metrics["fairness_status"] == "undefined_zero_completions"


def test_fairness_all_workers_crash_fallback():
    """Verify fallback handling when all workers experience downtime during the evaluation window."""
    config = SimulationConfig(
        num_workers=4,
        queue_capacity=50,
        lambda_nom=0.05,
        sim_time_ms=4000.0,
        warmup_ms=500.0,
        seed=42,
        fail_schedules=[
            # Staggered crashes: all 4 workers have some downtime
            FailureSchedule(worker_ids=[0, 1], t_fail=1000.0, t_repair=2000.0),
            FailureSchedule(worker_ids=[2, 3], t_fail=2000.0, t_repair=3000.0),
        ],
    )

    engine = SimulationEngine(config)
    result = engine.run()

    # None were continuously operational, so fallback population type is partial_uptime_fallback
    assert len(result.active_workers_fairness) == 4
    assert result.fairness_population_type == "partial_uptime_fallback"
    assert result.fairness_status == "evaluable"
    assert result.jains_index is not None
    assert 0.0 <= result.jains_index <= 1.0


def test_fairness_empty_active_workers_handling():
    """Verify that if all workers are down for the entire evaluation window, metric is flagged undefined."""
    config = SimulationConfig(
        num_workers=4,
        queue_capacity=50,
        lambda_nom=0.05,
        sim_time_ms=3000.0,
        warmup_ms=500.0,
        seed=42,
        fail_schedules=[
            # All workers crash before evaluation window and never recover
            FailureSchedule(worker_ids=[0, 1, 2, 3], t_fail=100.0, t_repair=10000.0),
        ],
    )

    engine = SimulationEngine(config)
    result = engine.run()

    assert result.active_workers_fairness == []
    assert result.fairness_population_type == "empty"
    assert result.jains_index is None
    assert result.fairness_status == "undefined_no_active_workers"

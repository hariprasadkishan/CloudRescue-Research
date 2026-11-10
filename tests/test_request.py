"""Unit tests for Request model."""

import pytest
from simulator.cloudrescue.models.request import Request, RequestStatus


def test_request_initialization():
    """Verify pre-generated request attributes are assigned properly."""
    req = Request(
        request_id=1,
        t_arrive=10.5,
        s_mand=12.0,
        s_opt=28.0,
        u_opt=0.45,
        timeout=200.0,
    )
    assert req.request_id == 1
    assert req.t_arrive == 10.5
    assert req.s_mand == 12.0
    assert req.s_opt == 28.0
    assert req.u_opt == 0.45
    assert req.timeout == 200.0
    assert req.status == RequestStatus.SUBMITTED
    assert req.total_latency is None
    assert req.queue_wait_time is None
    assert not req.is_successful()


def test_request_completion_and_latency():
    """Verify latency calculation and success classification."""
    req = Request(
        request_id=2,
        t_arrive=100.0,
        s_mand=10.0,
        s_opt=30.0,
        u_opt=0.2,
        timeout=200.0,
    )
    req.t_queued = 100.0
    req.t_mand_start = 120.0  # Waited 20 ms in queue
    req.t_mand_end = 130.0
    req.t_opt_start = 130.0
    req.t_opt_end = 160.0
    req.t_completed = 160.0  # Total latency = 60 ms
    req.status = RequestStatus.COMPLETED

    assert req.queue_wait_time == 20.0
    assert req.total_latency == 60.0
    assert req.is_successful()
    assert not req.is_sla_violated(sla_threshold=100.0)
    assert req.is_sla_violated(sla_threshold=50.0)


def test_request_timeout_failure():
    """Verify request exceeding timeout is not considered successful."""
    req = Request(
        request_id=3,
        t_arrive=100.0,
        s_mand=50.0,
        s_opt=160.0,
        u_opt=0.1,
        timeout=200.0,
    )
    req.t_mand_start = 100.0
    req.t_completed = 310.0  # Total latency = 210 ms > 200 ms timeout
    req.status = RequestStatus.COMPLETED

    assert req.total_latency == 210.0
    assert not req.is_successful()
    # Dropped or unsuccessful requests cannot violate SLA latency (they are SLA failures in V_overall)
    assert not req.is_sla_violated(sla_threshold=100.0)


def test_request_drop_status():
    """Verify non-completed states are recognized as unsuccessful."""
    req = Request(
        request_id=4,
        t_arrive=50.0,
        s_mand=10.0,
        s_opt=30.0,
        u_opt=0.5,
        timeout=200.0,
    )
    req.status = RequestStatus.DROPPED_QUEUE
    assert not req.is_successful()

    req.status = RequestStatus.DROPPED_TIMEOUT
    assert not req.is_successful()

    req.status = RequestStatus.FAILED_CRASH
    assert not req.is_successful()

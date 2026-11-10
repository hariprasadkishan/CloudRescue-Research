"""Structured event logging and preliminary metrics calculation for CloudRescue."""

from __future__ import annotations
import gzip
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd


@dataclass
class SimulationEvent:
    """Represents a single timestamped simulation event."""
    event_type: str
    timestamp: float
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        res = {"timestamp": self.timestamp, "event_type": self.event_type}
        res.update(self.data)
        return res


class EventLogger:
    """In-memory event recorder with export and metric analysis methods."""

    def __init__(self) -> None:
        self.events: List[SimulationEvent] = []

    def log_event(self, event_type: str, timestamp: float, **data: Any) -> None:
        """Appends a new structured event."""
        self.events.append(SimulationEvent(event_type=event_type, timestamp=timestamp, data=data))

    def to_dataframe(self) -> pd.DataFrame:
        """Converts recorded events into a pandas DataFrame."""
        if not self.events:
            return pd.DataFrame(columns=["timestamp", "event_type"])
        records = [e.to_dict() for e in self.events]
        return pd.DataFrame(records)

    def save_csv(self, filepath: str, compress: bool = False) -> None:
        """Saves events to CSV or gzip-compressed CSV."""
        df = self.to_dataframe()
        if compress or filepath.endswith(".gz"):
            with gzip.open(filepath, "wt", encoding="utf-8") as f:
                df.to_csv(f, index=False)
        else:
            df.to_csv(filepath, index=False)

    def compute_summary_metrics(
        self,
        warmup_ms: float = 0.0,
        sla_threshold_ms: float = 100.0,
        timeout_ms: float = 200.0,
    ) -> Dict[str, Any]:
        """Calculates standardized metrics strictly according to PRD.md and EXPERIMENT_PLAN.md.
        
        Evaluated outside the warm-up window [warmup_ms, inf).
        """
        # Filter events outside warm-up
        events = [e for e in self.events if e.timestamp >= warmup_ms]

        submitted_ids = set()
        completed_latencies: List[float] = []
        completed_opt: int = 0
        drop_queue_count = 0
        drop_timeout_count = 0
        crash_failed_count = 0

        for e in events:
            etype = e.event_type
            data = e.data

            if etype == "REQUEST_SUBMITTED":
                submitted_ids.add(data.get("request_id"))
            elif etype == "REQUEST_DROPPED_QUEUE":
                drop_queue_count += 1
            elif etype == "REQUEST_DROPPED_TIMEOUT":
                drop_timeout_count += 1
            elif etype == "REQUEST_FAILED_CRASH":
                crash_failed_count += 1
            elif etype == "REQUEST_COMPLETED":
                lat = data.get("total_latency")
                if lat is not None and lat <= timeout_ms:
                    completed_latencies.append(lat)
                    if data.get("full_fidelity", False):
                        completed_opt += 1

        n_submitted = len(submitted_ids)
        n_success = len(completed_latencies)

        # 1. Success Rate Sr (%)
        sr = (n_success / n_submitted * 100.0) if n_submitted > 0 else 0.0

        # 2. Latency SLA Violations V_lat (%) among successful requests
        lat_violations = sum(1 for l in completed_latencies if l > sla_threshold_ms)
        v_lat = (lat_violations / n_success * 100.0) if n_success > 0 else 0.0

        # 3. Overall SLA Failure Rate V_overall (%) among all submitted requests
        # SLA failures = drop_queue + drop_timeout + crash + latency_violations
        n_sla_failure = drop_queue_count + drop_timeout_count + crash_failed_count + lat_violations
        v_overall = (n_sla_failure / n_submitted * 100.0) if n_submitted > 0 else 0.0

        # 4. Mean, Median (p50), 95th-Percentile (p95), and 99th-Percentile (p99) Latency (ms)
        mean_lat = float(np.mean(completed_latencies)) if n_success > 0 else 0.0
        p50_lat = float(np.percentile(completed_latencies, 50)) if n_success > 0 else 0.0
        p95_lat = float(np.percentile(completed_latencies, 95)) if n_success > 0 else 0.0
        p99_lat = float(np.percentile(completed_latencies, 99)) if n_success > 0 else 0.0

        # 5. Service Fidelity F (%)
        fidelity = (completed_opt / n_success * 100.0) if n_success > 0 else 0.0

        # 6. Mean Dimmer Value θ_mean and per-worker dimmer across operational worker updates
        ctrl_events = [e for e in events if e.event_type == "CONTROLLER_UPDATED"]
        per_worker_theta: Dict[int, float] = {}
        if ctrl_events:
            thetas = [e.data.get("new_theta") for e in ctrl_events if e.data.get("new_theta") is not None]
            mean_dimmer = float(np.mean(thetas)) if thetas else 1.0

            # Calculate per-worker dimmer means
            worker_thetas: Dict[int, List[float]] = {}
            for e in ctrl_events:
                wid = e.data.get("worker_id")
                th = e.data.get("new_theta")
                if wid is not None and th is not None:
                    worker_thetas.setdefault(wid, []).append(th)
            for wid, th_list in worker_thetas.items():
                per_worker_theta[wid] = round(float(np.mean(th_list)), 4)
        else:
            mean_dimmer = 1.0  # CFG-A baseline operates at fixed theta = 1.0

        return {
            "n_submitted": n_submitted,
            "n_success": n_success,
            "drop_queue_count": drop_queue_count,
            "drop_timeout_count": drop_timeout_count,
            "crash_failed_count": crash_failed_count,
            "lat_violations_count": lat_violations,
            "sr_percent": round(sr, 2),
            "v_lat_percent": round(v_lat, 2),
            "v_overall_percent": round(v_overall, 2),
            "mean_latency_ms": round(mean_lat, 2),
            "p50_latency_ms": round(p50_lat, 2),
            "p95_latency_ms": round(p95_lat, 2),
            "p99_latency_ms": round(p99_lat, 2),
            "fidelity_percent": round(fidelity, 2),
            "mean_dimmer": round(mean_dimmer, 4),
            "per_worker_theta": per_worker_theta,
        }

    def get_balb_routing_diagnostics(self) -> pd.DataFrame:
        """Extracts BALB routing decision records for diagnostic analysis."""
        balb_events = [e for e in self.events if e.event_type == "BALB_ROUTING_DECISION"]
        if not balb_events:
            return pd.DataFrame(
                columns=[
                    "timestamp",
                    "request_id",
                    "selected_worker_id",
                    "fallback_active",
                    "scores",
                    "best_score",
                ]
            )
        records = []
        for e in balb_events:
            d = {"timestamp": e.timestamp}
            d.update(e.data)
            records.append(d)
        return pd.DataFrame(records)

    def save_balb_routing_diagnostics(self, filepath: str) -> None:
        """Saves BALB routing decision records to CSV."""
        df = self.get_balb_routing_diagnostics()
        df.to_csv(filepath, index=False)

    def get_controller_timeseries(self) -> pd.DataFrame:
        """Extracts controller update time-series data for analysis and visualization."""
        ctrl_events = [e for e in self.events if e.event_type == "CONTROLLER_UPDATED"]
        if not ctrl_events:
            return pd.DataFrame(
                columns=[
                    "timestamp",
                    "worker_id",
                    "measured_p95_ms",
                    "error",
                    "old_theta",
                    "new_theta",
                    "n_samples",
                    "status",
                ]
            )
        records = []
        for e in ctrl_events:
            d = {"timestamp": e.timestamp}
            d.update(e.data)
            records.append(d)
        return pd.DataFrame(records)

    def save_controller_timeseries(self, filepath: str) -> None:
        """Saves controller time-series records to CSV."""
        df = self.get_controller_timeseries()
        df.to_csv(filepath, index=False)

"""Workload generator implementing the 5-stream PRNG reproducibility architecture."""

from __future__ import annotations
from typing import List, Tuple
import numpy as np

from ..config import SimulationConfig
from ..models.request import Request


class WorkloadGenerator:
    """Generates immutable request tuples using isolated pseudorandom number streams.
    
    Adheres strictly to the multi-stream PRNG architecture defined in ARCHITECTURE.md:
    - Stream 1: Arrival process (inter-arrival intervals)
    - Stream 2: Mandatory processing durations Exp(mu_mand)
    - Stream 3: Optional processing durations Exp(mu_opt)
    - Stream 4: Optional execution threshold draws Uniform(0.0, 1.0)
    - Stream 5: Failure injection / repair schedule
    """

    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        
        # Derive 5 isolated PRNG streams from the master seed via SeedSequence
        ss = np.random.SeedSequence(self.config.seed)
        child_seeds = ss.spawn(5)
        
        self.rng_arrivals = np.random.default_rng(child_seeds[0])
        self.rng_mand = np.random.default_rng(child_seeds[1])
        self.rng_opt = np.random.default_rng(child_seeds[2])
        self.rng_uopt = np.random.default_rng(child_seeds[3])
        self.rng_failures = np.random.default_rng(child_seeds[4])

    def _get_rate_at(self, t: float) -> float:
        """Returns the instantaneous arrival rate lambda(t) in req/ms."""
        burst_end = self.config.burst_start_ms + self.config.burst_duration_ms
        if self.config.burst_start_ms <= t < burst_end and self.config.lambda_burst > 0:
            return self.config.lambda_burst
        return self.config.lambda_nom

    def generate_requests(self) -> List[Request]:
        """Pre-generates all Request tuples up to sim_time_ms.
        
        Pre-sampling all attributes upfront ensures that skipped optional stages
        in degraded configurations consume zero PRNG draws, preventing stochastic drift.
        """
        requests: List[Request] = []
        t_current = 0.0
        req_id = 1

        while True:
            current_rate = self._get_rate_at(t_current)
            # Inter-arrival time ~ Exp(current_rate)
            inter_arrival = self.rng_arrivals.exponential(1.0 / current_rate)
            t_current += inter_arrival

            if t_current > self.config.sim_time_ms:
                break

            s_mand = float(self.rng_mand.exponential(1.0 / self.config.mu_mand))
            s_opt = float(self.rng_opt.exponential(1.0 / self.config.mu_opt))
            u_opt = float(self.rng_uopt.uniform(0.0, 1.0))

            req = Request(
                request_id=req_id,
                t_arrive=t_current,
                s_mand=s_mand,
                s_opt=s_opt,
                u_opt=u_opt,
                timeout=self.config.timeout_ms,
            )
            requests.append(req)
            req_id += 1

        return requests

"""Tests verifying Phase 4 experiment matrix runner and statistical analysis functions."""

import numpy as np
import pandas as pd
import pytest
from scripts.analyze_results import compute_paired_analysis


def test_paired_analysis_identical_inputs():
    """When two series are identical, mean diff is 0 and p-value is 1.0."""
    s1 = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0])
    s2 = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0])
    res = compute_paired_analysis(s1, s2, "metric")
    assert res["mean_diff"] == 0.0
    assert res["std_diff"] == 0.0
    assert not res["is_significant"]


def test_paired_analysis_normal_significant_difference():
    """Tests paired analysis with a known normal shift."""
    np.random.seed(42)
    s_old = pd.Series(np.random.normal(50, 5, 30))
    s_new = s_old - 10.0  # Significant reduction
    res = compute_paired_analysis(s_new, s_old, "metric")
    assert res["mean_diff"] == pytest.approx(-10.0, abs=1e-3)
    assert res["is_significant"]
    assert res["p_value"] < 0.001
    assert res["effect_size_name"] == "Cohen's d_z"


def test_paired_analysis_non_normal_difference():
    """Tests paired analysis when differences are strongly non-normal."""
    diffs = [0.1] * 25 + [100.0, 200.0, 300.0, 400.0, 500.0]  # extreme skew
    s_old = pd.Series([10.0] * 30)
    s_new = s_old + pd.Series(diffs)
    res = compute_paired_analysis(s_new, s_old, "metric")
    assert not res["is_normal"]
    assert res["test_type"] == "Wilcoxon signed-rank"
    assert res["is_significant"]

"""
QoE Simulator - Level 6: Benford's Law Digital Distribution Scanner.

Implements spec Section 6.1 (Nigrini 2012): first-digit and second-digit Benford
distributions, a Kolmogorov-Smirnov statistic, and an artificiality test that flags
tidy rounded transactional populations (LINTER_BENFORD_ANOMALY).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import Decimal
from typing import List, Sequence


def _digits(value):
    number = Decimal(str(value)).copy_abs()
    if not number.is_finite():
        raise ValueError("Benford values must be finite")
    return number.as_tuple().digits if number else ()


def _first_digit(value):
    digits = _digits(value)
    return digits[0] if digits else 0


def _second_digit(value):
    digits = _digits(value)
    return digits[1] if len(digits) > 1 else 0


BENFORD_EXPECTED = {d: math.log10(1.0 + 1.0 / d) for d in range(1, 10)}


@dataclass
class BenfordDigitAnomaly:
    digit: int
    observed_frequency: float
    expected_frequency: float
    z_score: float
    is_statistically_anomalous: bool

    def to_dict(self) -> dict:
        return {
            "digit": self.digit,
            "observed_frequency": self.observed_frequency,
            "expected_frequency": self.expected_frequency,
            "z_score": self.z_score,
            "is_statistically_anomalous": self.is_statistically_anomalous,
        }


class BenfordScanner:
    """Scans a transactional population for Benford digital distribution."""

    def scan(self, values: Sequence) -> dict:
        values = [Decimal(str(v)) for v in values]
        if any(not v.is_finite() for v in values):
            raise ValueError("Benford values must be finite")
        values = [v for v in values if v]
        n = len(values)
        first_counts = {d: 0 for d in range(1, 10)}
        second_counts = {d: 0 for d in range(0, 10)}

        for v in values:
            fd = _first_digit(v)
            sd = _second_digit(v)
            if fd:
                first_counts[fd] += 1
            second_counts[sd] += 1

        first_obs = {d: (first_counts[d] / n if n else 0.0) for d in range(1, 10)}
        second_expected = {d: sum(math.log10(1 + 1 / (10 * k + d)) for k in range(1, 10)) for d in range(10)}
        second_obs = {d: (second_counts[d] / n if n else 0.0) for d in range(0, 10)}

        first_dist = []
        for d in range(1, 10):
            expected = BENFORD_EXPECTED[d]
            observed = first_obs[d]
            # z-score for a single digit proportion under normal approximation
            se = math.sqrt(expected * (1 - expected) / n) if n else 0.0
            z = (observed - expected) / se if se else 0.0
            first_dist.append(BenfordDigitAnomaly(
                digit=d, observed_frequency=observed, expected_frequency=expected,
                z_score=z, is_statistically_anomalous=abs(z) > 2.576))

        second_dist = []
        for d in range(0, 10):
            observed = second_obs[d]
            expected = second_expected[d]
            se = math.sqrt(expected * (1 - expected) / n) if n else 0.0
            z = (observed - expected) / se if se else 0.0
            second_dist.append(BenfordDigitAnomaly(
                digit=d, observed_frequency=observed, expected_frequency=expected,
                z_score=z, is_statistically_anomalous=abs(z) > 2.576))

        # Kolmogorov-Smirnov statistic over first-digit cumulative distributions
        cum_obs = 0.0
        cum_exp = 0.0
        ks = 0.0
        for d in range(1, 10):
            cum_obs += first_obs[d]
            cum_exp += BENFORD_EXPECTED[d]
            ks = max(ks, abs(cum_obs - cum_exp))

        # Artificiality test: a KS statistic above 0.10 flags non-Benford data.
        passes = n >= 100 and ks < 0.10

        return {
            "engagement_id": "",
            "total_transactions_scanned": n,
            "kolmogorov_smirnov_statistic": ks,
            "passes_benford_uniformity": passes,
            "first_digit_distribution": [a.to_dict() for a in first_dist],
            "second_digit_distribution": [a.to_dict() for a in second_dist],
        }

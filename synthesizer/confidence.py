"""Shared deterministic confidence calibration for evidence-backed Synapse views."""
from __future__ import annotations

import math


def calibrate_confidence(
    *,
    direct_chain: bool,
    corroborating_sources: int = 0,
    sample_size: int = 1,
    authoritative_source: bool = False,
    correlation_coefficient: float | None = None,
    data_completeness_pct: float | None = None,
    correlation_counts: dict | None = None,
) -> dict:
    """Calculate confidence in an observed correlation, never model opinion.

    For correlation-backed RCA scores, the weighted score is 60% positive Phi
    correlation, 25% sample reliability, and 15% data completeness. Legacy
    callers without a coefficient retain the evidence-band response shape.
    """
    corroborating_sources = max(0, int(corroborating_sources or 0))
    sample_size = max(0, int(sample_size or 0))
    if correlation_coefficient is not None:
        phi = max(-1.0, min(1.0, float(correlation_coefficient)))
        correlation_points = round(max(0.0, phi) * 60, 1)
        sample_points = round(min(sample_size / 30, 1.0) * 25, 1)
        completeness = max(0.0, min(100.0, float(data_completeness_pct or 0)))
        completeness_points = round(completeness * 0.15, 1)
        score = round(correlation_points + sample_points + completeness_points)
        level = "high" if score >= 70 else "medium" if score >= 40 else "low"
        counts = correlation_counts or {}
        return {
            "level": level,
            "score": score,
            "reason": f"{score}/100: Phi correlation {phi:.2f}, {sample_size} records, {completeness:.0f}% complete correlation data",
            "correlational": True,
            "correlation_coefficient": round(phi, 3),
            "correlation_counts": counts,
            "corroborating_sources": corroborating_sources,
            "sample_size": sample_size,
            "data_completeness_pct": round(completeness, 1),
            "factors": [
                {"name": "Correlation strength (Phi)", "points": correlation_points, "max_points": 60},
                {"name": "Sample reliability", "points": sample_points, "max_points": 25},
                {"name": "Data completeness", "points": completeness_points, "max_points": 15},
            ],
        }

    if authoritative_source:
        level = "high"
        reason = "authoritative source directly supports the claim"
    elif direct_chain and corroborating_sources >= 2:
        level = "high"
        reason = f"direct evidence chain corroborated by {corroborating_sources} linked source types"
    elif direct_chain or corroborating_sources >= 1 or sample_size >= 3:
        level = "medium"
        reason = "direct evidence exists but corroboration or sample size is limited"
    else:
        level = "low"
        reason = "evidence is incomplete or indirect"
    return {
        "level": level,
        "reason": reason,
        "corroborating_sources": corroborating_sources,
        "sample_size": sample_size,
    }

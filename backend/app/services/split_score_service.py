from __future__ import annotations

import logging
from uuid import UUID

import pandas as pd

from app.core.exceptions import UnsupportedEventError
from app.repositories.split_score_repository import SplitScoreRepository
from app.schemas.split_score_schemas import RunMetric, SegmentScore, SplitScoreResponse
from app.utils.hurdle_metrics import transform_stride_cycles_to_hurdle_metrics
from app.utils.split_score import compute_diffs, generate_coaching_notes
from app.utils.split_score_constants import (
    POPULATION_STATS,
    SEGMENT_LABELS,
    SUPPORTED_EVENTS,
)

logger = logging.getLogger(__name__)


class SplitScoreService:
    def __init__(self, repository: SplitScoreRepository) -> None:
        self.repository = repository

    async def get_split_score(self, run_id: UUID) -> SplitScoreResponse:
        logger.info(f"Service: Computing split score for run {run_id}")

        run_meta = await self.repository.get_run_meta(run_id)
        event_type = run_meta.event_type
        elapsed_ms: float = float(run_meta.elapsed_ms)

        if event_type not in SUPPORTED_EVENTS:
            raise UnsupportedEventError(event_type)

        gender = await self.repository.get_athlete_gender(run_id)
        gender_key = gender if gender in ("male", "female") else "male"
        stats = POPULATION_STATS[gender_key][event_type]

        raw_metrics = await self.repository.get_run_metrics(run_id)
        segments_ms = self._compute_segments(raw_metrics, elapsed_ms, event_type)
        diffs = compute_diffs(segments_ms, elapsed_ms, event_type, gender_key)
        notes = generate_coaching_notes(diffs, event_type)

        segment_scores = [
            SegmentScore(
                label=label,
                raw_ms=round(raw_ms, 1),
                pct_of_total=round((raw_ms / elapsed_ms) * 100, 2),
                diff_s=d["diff_s"],
                diff_pct=d["diff_pct"],
            )
            for label, raw_ms, d in zip(
                SEGMENT_LABELS[event_type], segments_ms, diffs, strict=True
            )
        ]

        logger.info(f"Service: Computed split score for run {run_id}")
        return SplitScoreResponse(
            run_id=str(run_id),
            event_type=event_type,
            total_ms=elapsed_ms,
            segments=segment_scores,
            coaching_notes=notes,
            population_mean_pcts=stats["mean"],
            population_std_pcts=stats["std"],
            population_percentiles=stats["percentiles"],
        )

    def _compute_segments(
        self,
        raw_metrics: list[RunMetric],
        elapsed_ms: float,
        event_type: str,
    ) -> list[float]:
        from app.schemas.event_type import EventType

        if event_type == EventType.hurdles_400m:
            return self._compute_hurdle_segments(raw_metrics, elapsed_ms, n_hurdles=10)
        if event_type == EventType.hurdles_110m:
            return self._compute_hurdle_segments(raw_metrics, elapsed_ms, n_hurdles=10)
        if event_type == EventType.hurdles_100m:
            return self._compute_hurdle_segments(raw_metrics, elapsed_ms, n_hurdles=10)
        if event_type == EventType.sprint_400m:
            return self._compute_sprint_segments(raw_metrics, elapsed_ms, n_splits=4)
        if event_type == EventType.sprint_100m:
            return self._compute_sprint_segments(raw_metrics, elapsed_ms, n_splits=3)
        if event_type == EventType.sprint_200m:
            return self._compute_sprint_segments(raw_metrics, elapsed_ms, n_splits=2)
        raise UnsupportedEventError(event_type)

    def _compute_hurdle_segments(
        self, raw_metrics: list[RunMetric], elapsed_ms: float, n_hurdles: int
    ) -> list[float]:
        df = pd.DataFrame([m.model_dump() for m in raw_metrics])
        hurdle_df = transform_stride_cycles_to_hurdle_metrics(df)
        if len(hurdle_df) < n_hurdles:
            raise ValueError(
                f"Expected {n_hurdles} hurdles, detected {len(hurdle_df)}. "
                "Check that the run contains a full race."
            )
        start_to_h1 = float(hurdle_df.iloc[0]["clearance_start_ms"])
        middle_splits: list[float] = (
            hurdle_df["hurdle_split_ms"].dropna().astype(float).tolist()
        )
        h_last_to_fin = elapsed_ms - float(hurdle_df.iloc[-1]["clearance_start_ms"])
        return [start_to_h1, *middle_splits, h_last_to_fin]

    def _compute_sprint_segments(
        self, raw_metrics: list[RunMetric], elapsed_ms: float, n_splits: int
    ) -> list[float]:
        df = (
            pd.DataFrame([m.model_dump() for m in raw_metrics])
            .sort_values("ic_time")
            .reset_index(drop=True)
        )
        n = len(df)
        q = n // n_splits
        splits: list[float] = []
        for i in range(n_splits):
            start_idx = i * q
            end_idx = (i + 1) * q if i < n_splits - 1 else n - 1
            seg_ms = float(df.iloc[end_idx]["ic_time"] - df.iloc[start_idx]["ic_time"])
            splits.append(seg_ms)
        return splits

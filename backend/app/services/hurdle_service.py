import logging
from uuid import UUID

import numpy as np
import pandas as pd

from app.repositories.hurdle_repository import HurdleRepository
from app.schemas.hurdle_schemas import (
    GctIncreaseData,
    HurdleMarker,
    HurdleMetricRow,
    HurdleSplitBarData,
    HurdleTimelinePoint,
    HurdleTimelineResponse,
    LandingGctBarData,
    StepsBetweenHurdlesData,
    TakeoffFtBarData,
    TakeoffGctBarData,
)
from app.utils.hurdle_chart_transformations import (
    transform_gct_increase,
    transform_hurdle_splits,
    transform_landing_gct,
    transform_steps_between_hurdles,
    transform_takeoff_ft,
    transform_takeoff_gct,
)
from app.utils.hurdle_metrics import transform_stride_cycles_to_hurdle_metrics

logger = logging.getLogger(__name__)


class HurdleService:
    """Service for hurdle-metric related business logic."""

    def __init__(self, repository: HurdleRepository) -> None:
        self.repository = repository

    async def _get_hurdle_metric_rows(self, run_id: UUID) -> list[HurdleMetricRow]:
        """Fetch raw steps, run the hurdle transform, and return validated HurdleMetricRow objects."""
        steps = await self.repository.get_hurdle_metrics(run_id)

        df = pd.DataFrame(steps)
        hurdle_df = transform_stride_cycles_to_hurdle_metrics(df)
        rows = hurdle_df.to_dict(orient="records")

        # Sanitize at the dict level so Pydantic sees Python None, not nan.
        sanitized = [
            {
                k: (None if isinstance(v, float) and np.isnan(v) else v)
                for k, v in row.items()
            }
            for row in rows
        ]

        return [HurdleMetricRow(**row) for row in sanitized]

    async def get_hurdle_metrics_by_run_id(self, run_id: UUID) -> list[HurdleMetricRow]:
        """Get all per-hurdle metrics for a run."""
        logger.info(f"Service: Getting hurdle metrics for run {run_id}")
        result = await self._get_hurdle_metric_rows(run_id)
        logger.info(f"Service: Returning {len(result)} hurdle rows for run {run_id}")
        return result

    async def get_hurdle_splits(self, run_id: UUID) -> list[HurdleSplitBarData]:
        """Transform hurdle data for split bar chart."""
        logger.info(f"Service: Getting hurdle splits for run {run_id}")
        data = await self._get_hurdle_metric_rows(run_id)
        return transform_hurdle_splits(data)

    async def get_steps_between_hurdles(
        self, run_id: UUID
    ) -> list[StepsBetweenHurdlesData]:
        """Transform hurdle data for steps-between display."""
        logger.info(f"Service: Getting steps between hurdles for run {run_id}")
        data = await self._get_hurdle_metric_rows(run_id)
        return transform_steps_between_hurdles(data)

    async def get_takeoff_gct(self, run_id: UUID) -> list[TakeoffGctBarData]:
        """Transform hurdle data for takeoff GCT bar chart."""
        logger.info(f"Service: Getting takeoff GCT for run {run_id}")
        data = await self._get_hurdle_metric_rows(run_id)
        return transform_takeoff_gct(data)

    async def get_landing_gct(self, run_id: UUID) -> list[LandingGctBarData]:
        """Transform hurdle data for landing GCT bar chart."""
        logger.info(f"Service: Getting landing GCT for run {run_id}")
        data = await self._get_hurdle_metric_rows(run_id)
        return transform_landing_gct(data)

    async def get_takeoff_ft(self, run_id: UUID) -> list[TakeoffFtBarData]:
        """Transform hurdle data for takeoff FT bar chart."""
        logger.info(f"Service: Getting takeoff FT for run {run_id}")
        data = await self._get_hurdle_metric_rows(run_id)
        return transform_takeoff_ft(data)

    async def get_gct_increase(self, run_id: UUID) -> list[GctIncreaseData]:
        """Transform hurdle data for GCT increase KPI."""
        logger.info(f"Service: Getting GCT increase for run {run_id}")
        data = await self._get_hurdle_metric_rows(run_id)
        return transform_gct_increase(data)

    async def get_hurdle_timeline(self, run_id: UUID) -> HurdleTimelineResponse:
        """Build time-series points for the hurdle timeline chart."""
        logger.info(f"Service: Getting hurdle timeline for run {run_id}")
        steps = await self.repository.get_hurdle_metrics(run_id)
        points: list[HurdleTimelinePoint] = []

        for step in steps:
            foot = step["foot"]
            ic_ms = step["ic_time"]
            to_ms = step["to_time"]
            gct_ms = step["gct_ms"]
            ft_ms = step["flight_ms"]

            if ic_ms is None or to_ms is None:
                continue

            ic_s = ic_ms / 1000
            to_s = to_ms / 1000

            # Ground phase — two points to make flat bottom
            gt_mid_s = (ic_ms + (to_ms - ic_ms) / 2) / 1000
            for t in [ic_s, gt_mid_s, to_s - 0.001]:
                points.append(
                    HurdleTimelinePoint(
                        time_s=round(t, 4),
                        left=0.0 if foot == "left" else None,
                        right=0.0 if foot == "right" else None,
                        foot=foot,
                        phase="ground",
                        gct_ms=gct_ms,
                        ft_ms=None,
                    )
                )

            # Air phase
            if ft_ms:
                ft_mid_s = (to_ms + ft_ms / 2) / 1000  # midpoint of flight
                ft_end_s = (to_ms + ft_ms) / 1000
                for t in [to_s, ft_mid_s, ft_end_s - 0.001]:
                    points.append(
                        HurdleTimelinePoint(
                            time_s=round(t, 4),
                            left=float(ft_ms) if foot == "left" else None,
                            right=float(ft_ms) if foot == "right" else None,
                            foot=foot,
                            phase="air",
                            gct_ms=None,
                            ft_ms=ft_ms,
                        )
                    )

        # Sort per foot separately to preserve ground→air→ground sequence
        left_points = sorted(
            [p for p in points if p.foot == "left"], key=lambda p: p.time_s
        )
        right_points = sorted(
            [p for p in points if p.foot == "right"], key=lambda p: p.time_s
        )
        points = left_points + right_points

        hurdle_rows = await self._get_hurdle_metric_rows(run_id)
        markers = [
            HurdleMarker(
                time_s=round(row.clearance_start_ms / 1000, 4),
                hurdle_num=row.hurdle_num,
            )
            for row in hurdle_rows
        ]

        logger.info(
            f"Service: Returning {len(points)} timeline points for run {run_id}"
        )
        return HurdleTimelineResponse(
            points=points,
            left_points=left_points,
            right_points=right_points,
            hurdle_markers=markers,
        )

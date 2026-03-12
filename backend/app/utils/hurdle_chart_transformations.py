from app.schemas.hurdle_schemas import (
    GctIncreaseData,
    HurdleMetricRow,
    HurdleSplitBarData,
    LandingGctBarData,
    StepsBetweenHurdlesData,
    TakeoffFtBarData,
    TakeoffGctBarData,
)


def transform_hurdle_splits(
    data: list[HurdleMetricRow],
) -> list[HurdleSplitBarData]:
    """Extract hurdle split bar chart data from full hurdle metrics."""
    return [
        HurdleSplitBarData(
            hurdle_num=row.hurdle_num,
            hurdle_split_ms=row.hurdle_split_ms,
        )
        for row in data
    ]


def transform_steps_between_hurdles(
    data: list[HurdleMetricRow],
) -> list[StepsBetweenHurdlesData]:
    """Extract steps-between-hurdles display data from full hurdle metrics."""
    return [
        StepsBetweenHurdlesData(
            hurdle_num=row.hurdle_num,
            steps_between_hurdles=row.steps_between_hurdles,
        )
        for row in data
    ]


def transform_takeoff_gct(
    data: list[HurdleMetricRow],
) -> list[TakeoffGctBarData]:
    """Extract takeoff GCT bar chart data from full hurdle metrics."""
    return [
        TakeoffGctBarData(
            hurdle_num=row.hurdle_num,
            takeoff_foot=row.takeoff_foot,
            takeoff_gct_ms=row.takeoff_gct_ms,
        )
        for row in data
    ]


def transform_landing_gct(
    data: list[HurdleMetricRow],
) -> list[LandingGctBarData]:
    """Extract landing GCT bar chart data from full hurdle metrics."""
    return [
        LandingGctBarData(
            hurdle_num=row.hurdle_num,
            landing_foot=row.landing_foot,
            landing_gct_ms=row.landing_gct_ms,
        )
        for row in data
    ]


def transform_takeoff_ft(
    data: list[HurdleMetricRow],
) -> list[TakeoffFtBarData]:
    """Extract takeoff flight time bar chart data from full hurdle metrics."""
    return [
        TakeoffFtBarData(
            hurdle_num=row.hurdle_num,
            takeoff_ft_ms=row.takeoff_ft_ms,
        )
        for row in data
    ]


def transform_gct_increase(
    data: list[HurdleMetricRow],
) -> list[GctIncreaseData]:
    """Extract GCT increase hurdle-to-hurdle data from full hurdle metrics."""
    return [
        GctIncreaseData(
            hurdle_num=row.hurdle_num,
            takeoff_gct_ms=row.takeoff_gct_ms,
            gct_increase_hurdle_to_hurdle_pct=row.gct_increase_hurdle_to_hurdle_pct,
        )
        for row in data
    ]

from typing import Literal

from app.schemas.run_schemas import (
    LROverlayData,
    RunResponse,
    StackedBarData,
    StepFrequencyData,
)


def transform_data_for_lr_overlay(
    data: list[RunResponse], metric: Literal["gct_ms", "flight_ms"]
) -> list[LROverlayData]:
    """Transform each data point in run for FT and GCT visualizations"""

    stride_map: dict[int, dict] = {}
    for row in data:
        stride_num = row.stride_num
        if stride_num not in stride_map:
            stride_map[stride_num] = {"stride_num": stride_num}
        stride_map[stride_num][row.foot] = getattr(row, metric)

    return sorted(
        [LROverlayData(**entry) for entry in stride_map.values()],
        key=lambda x: x.stride_num,
    )


def transform_data_for_stacked_bar(data: list[RunResponse]) -> list[StackedBarData]:
    """Transform each data point in run for stacked bar chart (step time)"""

    return sorted(
        [
            StackedBarData(
                stride_num=row.stride_num,
                foot=row.foot,
                label=f"{row.stride_num}{'L' if row.foot == 'left' else 'R'}",
                gct_ms=row.gct_ms,
                flight_ms=row.flight_ms,
            )
            for row in data
        ],
        key=lambda x: x.stride_num,
    )


def transform_data_for_step_frequency(
    data: list[RunResponse],
) -> list[StepFrequencyData]:
    """Transform each data point in run for Step Frequency line chart.

    Formula: step_frequency_hz = 1000 / step_time_ms
    """
    return sorted(
        [
            StepFrequencyData(
                stride_num=row.stride_num,
                foot=row.foot,
                label=f"{row.stride_num}{'L' if row.foot == 'left' else 'R'}",
                step_frequency_hz=round(1000 / row.step_time_ms, 3),
            )
            for row in data
        ],
        key=lambda x: (x.stride_num, x.foot),
    )

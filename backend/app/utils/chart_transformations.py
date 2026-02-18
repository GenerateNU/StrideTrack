from typing import Literal

from app.schemas.run_schemas import LROverlayData, RunResponse, StackedBarData


def transform_data_for_lr_overlay(
    data: list[RunResponse], metric: Literal["gct_ms", "flight_ms"]
) -> list[LROverlayData]:
    """Transform each data point in run for FT and GCT visualizations"""

    stride_map: dict[int, dict] = {}
    for row in RunResponse:
        stride_num = row["stride_num"]
        if stride_num not in stride_map:
            stride_map[stride_num] = {"stride_num": stride_num}
        stride_map[stride_num][row["foot"]] = row[metric]

    return sorted(stride_map.values(), key=lambda x: x["stride_num"])


def transform_data_for_stacked_bar(data: list[RunResponse]) -> list[StackedBarData]:
    """Transform each data point in run for stacked bar chart (step time)"""

    return sorted(
        [
            {
                "stride_num": row["stride_num"],
                "foot": row["foot"],
                "label": f"{row['stride_num']}{'L' if row['foot'] == 'left' else 'R'}",
                "gct_ms": row["gct_ms"],
                "flight_ms": row["flight_ms"],
            }
            for row in data
        ],
        key=lambda x: x["stride_num"],
    )

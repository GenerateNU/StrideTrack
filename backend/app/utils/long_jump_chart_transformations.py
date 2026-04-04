from app.schemas.long_jump_schemas import (
    ApproachProfileData,
    LjTakeoffData,
    LongJumpMetricRow,
)


def transform_lj_approach_profile(
    raw_steps: list[dict],
    clearance_start_ms: int,
) -> list[ApproachProfileData]:
    approach = sorted(
        [s for s in raw_steps if s["to_time"] <= clearance_start_ms],
        key=lambda s: s["ic_time"],
    )
    n = len(approach)
    result: list[ApproachProfileData] = []

    for i, step in enumerate(approach):
        if i == n - 1:
            phase = "takeoff"
        elif i == n - 2:
            phase = "penultimate"
        elif i == n - 3:
            phase = "antepenultimate"
        else:
            phase = "approach"

        result.append(
            ApproachProfileData(
                stride_num=int(step["stride_num"]),
                foot=step["foot"],
                ic_time=int(step["ic_time"]),
                gct_ms=int(step["gct_ms"]),
                phase=phase,
            )
        )

    return result


def transform_lj_takeoff(row: LongJumpMetricRow) -> LjTakeoffData:
    return LjTakeoffData(
        takeoff_foot=row.takeoff_foot,
        takeoff_gct_ms=row.takeoff_gct_ms,
        penultimate_foot=row.penultimate_foot,
        penultimate_gct_ms=row.penultimate_gct_ms,
        jump_ft_ms=row.jump_ft_ms,
    )

from app.schemas.triple_jump_schemas import (
    PhaseRatioData,
    TjContactEfficiencyData,
    TripleJumpMetricRow,
)


def transform_tj_phase_ratio(row: TripleJumpMetricRow) -> list[PhaseRatioData]:
    return [
        PhaseRatioData(
            phase="hop",
            ft_ms=row.hop_ft_ms,
            gct_ms=row.hop_gct_ms,
            ratio_pct=row.phase_ratio_hop,
        ),
        PhaseRatioData(
            phase="step",
            ft_ms=row.step_ft_ms,
            gct_ms=row.step_gct_ms,
            ratio_pct=row.phase_ratio_step,
        ),
        PhaseRatioData(
            phase="jump",
            ft_ms=row.jump_ft_ms,
            gct_ms=row.jump_gct_ms,
            ratio_pct=row.phase_ratio_jump,
        ),
    ]


def transform_tj_contact_efficiency(
    row: TripleJumpMetricRow,
) -> TjContactEfficiencyData:
    return TjContactEfficiencyData(
        hop_gct_ms=row.hop_gct_ms,
        step_gct_ms=row.step_gct_ms,
        jump_gct_ms=row.jump_gct_ms,
        hop_ft_ms=row.hop_ft_ms,
        step_ft_ms=row.step_ft_ms,
        jump_ft_ms=row.jump_ft_ms,
        contact_time_efficiency=row.contact_time_efficiency,
    )

from app.transformations.bosco_transformations import (
    transform_stride_cycles_to_bosco_tests,
)

from app.repositories.bosco_repository import BoscoRepository
from app.schemas.bosco_schemas import BoscoMetricsResponse, Run


class BoscoService:
    def __init__(self, repository: BoscoRepository) -> None:
        self.repository = repository

    def get_bosco_metrics(self, run_id: str) -> BoscoMetricsResponse:
        """Fetches run metrics and applies bosco transformations"""
        df = self.repository.get_run_metrics_by_run_id(run_id)
        metrics = transform_stride_cycles_to_bosco_tests(df)

        return BoscoMetricsResponse(
            run_id=run_id,
            jump_heights=metrics["jump_heights"].tolist(),
            mean_jump_height=round(metrics["mean_jump_height"], 4),
            peak_jump_height=round(metrics["peak_jump_height"], 4),
            peak_jump_index=int(metrics["jump_heights"].idxmax()) + 1,
            jump_frequency=round(metrics["jump_frequency"], 3),
            rsi_per_jump=[round(rsi, 3) for rsi in metrics["rsi_per_jump"]],
            fatigue_index_pct=round(metrics["fatigue_index_pct"], 2),
        )

    def get_bosco_runs_for_athlete(self, athlete_id: str) -> list[Run]:
        """Returns all Bosco test runs for a given athlete."""
        return self.repository.get_bosco_runs_by_athlete_id(athlete_id)

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.schemas.reaction_time_schemas import ReactionTimeRunMetric
from app.services.reaction_time_service import ReactionTimeService, _classify_zone


def _make_metric(
    ic_time: float, to_time: float, gct_ms: float = 100.0
) -> ReactionTimeRunMetric:
    return ReactionTimeRunMetric(ic_time=ic_time, to_time=to_time, gct_ms=gct_ms)


def _make_service(metrics: list[ReactionTimeRunMetric]) -> ReactionTimeService:
    """Create a ReactionTimeService with a stubbed repository."""
    repo = AsyncMock()
    repo.get_run_metrics.return_value = metrics
    return ReactionTimeService(repository=repo)


# ── _classify_zone ──


@pytest.mark.unit
class TestClassifyZone:
    def test_below_200_is_green(self) -> None:
        zone, desc = _classify_zone(150.0)
        assert zone == "green"
        assert "200" in desc

    def test_exactly_200_is_yellow(self) -> None:
        zone, _ = _classify_zone(200.0)
        assert zone == "yellow"

    def test_between_200_and_300_is_yellow(self) -> None:
        zone, _ = _classify_zone(250.0)
        assert zone == "yellow"

    def test_exactly_300_is_yellow(self) -> None:
        zone, _ = _classify_zone(300.0)
        assert zone == "yellow"

    def test_above_300_is_red(self) -> None:
        zone, desc = _classify_zone(350.0)
        assert zone == "red"
        assert "300" in desc

    def test_zero_is_green(self) -> None:
        zone, _ = _classify_zone(0.0)
        assert zone == "green"


# ── ReactionTimeService.get_reaction_time ──


@pytest.mark.unit
class TestGetReactionTime:
    """Unit tests for ReactionTimeService.get_reaction_time."""

    @pytest.mark.asyncio
    async def test_uses_to_time_of_first_metric(self) -> None:
        """Reaction time should equal to_time of the first row."""
        service = _make_service(
            [
                _make_metric(ic_time=0, to_time=175),
                _make_metric(ic_time=175, to_time=350),
            ]
        )
        result = await service.get_reaction_time(uuid4())
        assert result.reaction_time_ms == 175.0

    @pytest.mark.asyncio
    async def test_green_zone_for_fast_reaction(self) -> None:
        """to_time of 150ms should produce green zone."""
        service = _make_service([_make_metric(ic_time=0, to_time=150)])
        result = await service.get_reaction_time(uuid4())
        assert result.zone == "green"

    @pytest.mark.asyncio
    async def test_yellow_zone_for_average_reaction(self) -> None:
        """to_time of 250ms should produce yellow zone."""
        service = _make_service([_make_metric(ic_time=0, to_time=250)])
        result = await service.get_reaction_time(uuid4())
        assert result.zone == "yellow"

    @pytest.mark.asyncio
    async def test_red_zone_for_slow_reaction(self) -> None:
        """to_time of 1290ms should produce red zone."""
        service = _make_service([_make_metric(ic_time=0, to_time=1290)])
        result = await service.get_reaction_time(uuid4())
        assert result.zone == "red"

    @pytest.mark.asyncio
    async def test_reaction_time_is_rounded(self) -> None:
        """Reaction time should be rounded to 2 decimal places."""
        service = _make_service([_make_metric(ic_time=0, to_time=175.123456)])
        result = await service.get_reaction_time(uuid4())
        assert result.reaction_time_ms == 175.12

    @pytest.mark.asyncio
    async def test_run_id_is_in_response(self) -> None:
        """The run_id in the response should match the requested run_id."""
        run_id = uuid4()
        service = _make_service([_make_metric(ic_time=0, to_time=175)])
        result = await service.get_reaction_time(run_id)
        assert result.run_id == str(run_id)

    @pytest.mark.asyncio
    async def test_onset_timestamp_matches_to_time(self) -> None:
        """onset_timestamp_ms should equal to_time of first metric."""
        service = _make_service([_make_metric(ic_time=0, to_time=200)])
        result = await service.get_reaction_time(uuid4())
        assert result.onset_timestamp_ms == 200.0

    @pytest.mark.asyncio
    async def test_empty_metrics_raises_value_error(self) -> None:
        """An empty metrics list should raise a ValueError."""
        service = _make_service([])
        with pytest.raises(ValueError):
            await service.get_reaction_time(uuid4())

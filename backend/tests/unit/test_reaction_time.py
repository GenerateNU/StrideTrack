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
    """Create a ReactionTimeService with a stubbed repository returning fixed metrics."""
    repo = AsyncMock()
    repo.get_run_metrics.return_value = metrics
    return ReactionTimeService(repository=repo)


# ── _classify_zone ──


@pytest.mark.unit
class TestClassifyZone:
    """Tests for the _classify_zone helper."""

    def test_below_200_is_green(self) -> None:
        """Any reaction time below 200ms should be classified as green."""
        zone, desc = _classify_zone(150.0)
        assert zone == "green"
        assert "200" in desc

    def test_exactly_200_is_yellow(self) -> None:
        """200ms sits on the green/yellow boundary and should be yellow."""
        zone, _ = _classify_zone(200.0)
        assert zone == "yellow"

    def test_between_200_and_300_is_yellow(self) -> None:
        """Values between 200 and 300ms should be yellow."""
        zone, _ = _classify_zone(250.0)
        assert zone == "yellow"

    def test_exactly_300_is_yellow(self) -> None:
        """300ms sits on the yellow/red boundary and should be yellow."""
        zone, _ = _classify_zone(300.0)
        assert zone == "yellow"

    def test_above_300_is_red(self) -> None:
        """Any reaction time above 300ms should be classified as red."""
        zone, desc = _classify_zone(350.0)
        assert zone == "red"
        assert "300" in desc

    def test_zero_is_green(self) -> None:
        """Zero reaction time should be classified as green."""
        zone, _ = _classify_zone(0.0)
        assert zone == "green"


# ── ReactionTimeService.get_reaction_time ──


@pytest.mark.unit
class TestGetReactionTime:
    """Tests for ReactionTimeService.get_reaction_time."""

    @pytest.mark.asyncio
    async def test_reaction_time_equals_first_to_time(self) -> None:
        """Reaction time should equal to_time of the first stride row."""
        service = _make_service(
            [
                _make_metric(ic_time=0, to_time=175),
                _make_metric(ic_time=175, to_time=350),
            ]
        )
        result = await service.get_reaction_time(uuid4())
        assert result.reaction_time_ms == 175.0

    @pytest.mark.asyncio
    async def test_ignores_subsequent_strides(self) -> None:
        """Only the first stride's to_time should be used, not later ones."""
        service = _make_service(
            [
                _make_metric(ic_time=0, to_time=150),
                _make_metric(ic_time=150, to_time=5000),
            ]
        )
        result = await service.get_reaction_time(uuid4())
        assert result.reaction_time_ms == 150.0

    @pytest.mark.asyncio
    async def test_fast_reaction_is_green(self) -> None:
        """A to_time of 150ms should produce a green zone."""
        service = _make_service([_make_metric(ic_time=0, to_time=150)])
        result = await service.get_reaction_time(uuid4())
        assert result.zone == "green"

    @pytest.mark.asyncio
    async def test_average_reaction_is_yellow(self) -> None:
        """A to_time of 250ms should produce a yellow zone."""
        service = _make_service([_make_metric(ic_time=0, to_time=250)])
        result = await service.get_reaction_time(uuid4())
        assert result.zone == "yellow"

    @pytest.mark.asyncio
    async def test_slow_reaction_is_red(self) -> None:
        """A to_time of 1290ms (typical seed data block start) should produce red."""
        service = _make_service([_make_metric(ic_time=0, to_time=1290)])
        result = await service.get_reaction_time(uuid4())
        assert result.zone == "red"

    @pytest.mark.asyncio
    async def test_reaction_time_is_rounded_to_two_decimals(self) -> None:
        """Reaction time should be rounded to 2 decimal places."""
        service = _make_service([_make_metric(ic_time=0, to_time=175.123456)])
        result = await service.get_reaction_time(uuid4())
        assert result.reaction_time_ms == 175.12

    @pytest.mark.asyncio
    async def test_onset_timestamp_matches_to_time(self) -> None:
        """onset_timestamp_ms should equal to_time of first metric."""
        service = _make_service([_make_metric(ic_time=0, to_time=200)])
        result = await service.get_reaction_time(uuid4())
        assert result.onset_timestamp_ms == 200.0

    @pytest.mark.asyncio
    async def test_run_id_in_response_matches_input(self) -> None:
        """The run_id in the response should match the requested run_id."""
        run_id = uuid4()
        service = _make_service([_make_metric(ic_time=0, to_time=175)])
        result = await service.get_reaction_time(run_id)
        assert result.run_id == str(run_id)

    @pytest.mark.asyncio
    async def test_empty_metrics_raises_value_error(self) -> None:
        """An empty metrics list should raise a ValueError."""
        service = _make_service([])
        with pytest.raises(ValueError):
            await service.get_reaction_time(uuid4())

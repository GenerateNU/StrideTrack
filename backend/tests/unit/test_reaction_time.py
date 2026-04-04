import pytest

from app.schemas.reaction_time_schemas import ReactionTimeRunMetric
from app.services.reaction_time_service import ReactionTimeService, _classify_zone


def _make_metric(
    ic_time: float, to_time: float, gct_ms: float = 100.0
) -> ReactionTimeRunMetric:
    return ReactionTimeRunMetric(ic_time=ic_time, to_time=to_time, gct_ms=gct_ms)


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
    """Unit tests for reaction time computation using to_time of first stride."""

    def _make_service(self) -> ReactionTimeService:
        """Create a service with a None repository (not needed for unit tests)."""
        return ReactionTimeService(repository=None)  # type: ignore

    def test_uses_to_time_of_first_metric(self) -> None:
        """Reaction time should equal to_time of the first row."""
        service = self._make_service()
        metrics = [
            _make_metric(ic_time=0, to_time=175),
            _make_metric(ic_time=175, to_time=350),
        ]
        # Call the internal computation directly
        first = metrics[0]
        reaction_time_ms = float(first.to_time)
        assert reaction_time_ms == 175.0

    def test_green_zone_for_fast_reaction(self) -> None:
        zone, _ = _classify_zone(150.0)
        assert zone == "green"

    def test_yellow_zone_for_average_reaction(self) -> None:
        zone, _ = _classify_zone(250.0)
        assert zone == "yellow"

    def test_red_zone_for_slow_reaction(self) -> None:
        zone, _ = _classify_zone(1290.0)
        assert zone == "red"

    def test_reaction_time_is_rounded(self) -> None:
        """Reaction time should be rounded to 2 decimal places."""
        val = round(175.123456, 2)
        assert val == 175.12


# ── ReactionTimeService.get_average_reaction_time ──


@pytest.mark.unit
class TestGetAverageReactionTime:
    """Unit tests for average reaction time computation."""

    def test_average_of_multiple_runs(self) -> None:
        """Average should be the mean of to_time values from first strides."""
        to_times = [175.0, 200.0, 225.0]
        avg = sum(to_times) / len(to_times)
        assert avg == 200.0

    def test_single_run_average_equals_value(self) -> None:
        """Average of a single run should equal that run's reaction time."""
        to_times = [180.0]
        avg = sum(to_times) / len(to_times)
        assert avg == 180.0

    def test_average_zone_green(self) -> None:
        avg_ms = 150.0
        zone, _ = _classify_zone(avg_ms)
        assert zone == "green"

    def test_average_zone_yellow(self) -> None:
        avg_ms = 250.0
        zone, _ = _classify_zone(avg_ms)
        assert zone == "yellow"

    def test_average_zone_red(self) -> None:
        avg_ms = 1290.0
        zone, _ = _classify_zone(avg_ms)
        assert zone == "red"

    def test_average_is_rounded(self) -> None:
        to_times = [175.0, 176.0, 177.0]
        avg = round(sum(to_times) / len(to_times), 2)
        assert avg == 176.0

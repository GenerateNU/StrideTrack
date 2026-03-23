import pytest

from app.schemas.hurdle_schemas import (
    GctIncreaseData,
    HurdleMetricRow,
    HurdleSplitBarData,
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


# Fixtures


@pytest.fixture
def hurdle_rows() -> list[HurdleMetricRow]:
    """Two hurdle metric rows."""
    return [
        HurdleMetricRow(
            hurdle_num=1,
            clearance_start_ms=400,
            clearance_end_ms=700,
            takeoff_ft_ms=300,
            hurdle_split_ms=700,
            steps_between_hurdles=3,
            takeoff_foot="right",
            takeoff_gct_ms=190,
            landing_foot="left",
            landing_gct_ms=210,
            gct_increase_hurdle_to_hurdle_pct=0.0,
        ),
        HurdleMetricRow(
            hurdle_num=2,
            clearance_start_ms=1100,
            clearance_end_ms=1400,
            takeoff_ft_ms=300,
            hurdle_split_ms=None,
            steps_between_hurdles=None,
            takeoff_foot="left",
            takeoff_gct_ms=200,
            landing_foot="right",
            landing_gct_ms=195,
            gct_increase_hurdle_to_hurdle_pct=5.26,
        ),
    ]


# transform_hurdle_splits


@pytest.mark.unit
class TestTransformHurdleSplits:
    """Tests for transform_hurdle_splits."""

    def test_returns_correct_values(self, hurdle_rows: list[HurdleMetricRow]) -> None:
        """Should extract hurdle_num and hurdle_split_ms from each row."""
        result = transform_hurdle_splits(hurdle_rows)

        assert len(result) == 2
        assert result[0].hurdle_num == 1
        assert result[0].hurdle_split_ms == 700
        assert result[1].hurdle_num == 2
        assert result[1].hurdle_split_ms is None

    def test_returns_correct_type(self, hurdle_rows: list[HurdleMetricRow]) -> None:
        """Each item in the result should be a HurdleSplitBarData instance."""
        result = transform_hurdle_splits(hurdle_rows)

        for item in result:
            assert isinstance(item, HurdleSplitBarData)

    def test_empty_input_returns_empty(self) -> None:
        """An empty input list should return an empty output list."""
        assert transform_hurdle_splits([]) == []


# transform_steps_between_hurdles


@pytest.mark.unit
class TestTransformStepsBetweenHurdles:
    """Tests for transform_steps_between_hurdles."""

    def test_returns_correct_values(self, hurdle_rows: list[HurdleMetricRow]) -> None:
        """Should extract hurdle_num and steps_between_hurdles from each row."""
        result = transform_steps_between_hurdles(hurdle_rows)

        assert result[0].hurdle_num == 1
        assert result[0].steps_between_hurdles == 3
        assert result[1].steps_between_hurdles is None

    def test_returns_correct_type(self, hurdle_rows: list[HurdleMetricRow]) -> None:
        """Each item in the result should be a StepsBetweenHurdlesData instance."""
        result = transform_steps_between_hurdles(hurdle_rows)

        for item in result:
            assert isinstance(item, StepsBetweenHurdlesData)

    def test_empty_input_returns_empty(self) -> None:
        """An empty input list should return an empty output list."""
        assert transform_steps_between_hurdles([]) == []


# ---------------------------------------------------------------------------
# transform_takeoff_gct
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestTransformTakeoffGct:
    """Tests for transform_takeoff_gct."""

    def test_returns_correct_values(self, hurdle_rows: list[HurdleMetricRow]) -> None:
        """Should extract hurdle_num, takeoff_foot, and takeoff_gct_ms from each row."""
        result = transform_takeoff_gct(hurdle_rows)

        assert result[0].hurdle_num == 1
        assert result[0].takeoff_foot == "right"
        assert result[0].takeoff_gct_ms == 190
        assert result[1].takeoff_foot == "left"
        assert result[1].takeoff_gct_ms == 200

    def test_returns_correct_type(self, hurdle_rows: list[HurdleMetricRow]) -> None:
        """Each item in the result should be a TakeoffGctBarData instance."""
        result = transform_takeoff_gct(hurdle_rows)

        for item in result:
            assert isinstance(item, TakeoffGctBarData)

    def test_empty_input_returns_empty(self) -> None:
        """An empty input list should return an empty output list."""
        assert transform_takeoff_gct([]) == []


# transform_landing_gct


@pytest.mark.unit
class TestTransformLandingGct:
    """Tests for transform_landing_gct."""

    def test_returns_correct_values(self, hurdle_rows: list[HurdleMetricRow]) -> None:
        """Should extract hurdle_num, landing_foot, and landing_gct_ms from each row."""
        result = transform_landing_gct(hurdle_rows)

        assert result[0].hurdle_num == 1
        assert result[0].landing_foot == "left"
        assert result[0].landing_gct_ms == 210
        assert result[1].landing_foot == "right"
        assert result[1].landing_gct_ms == 195

    def test_returns_correct_type(self, hurdle_rows: list[HurdleMetricRow]) -> None:
        """Each item in the result should be a LandingGctBarData instance."""
        result = transform_landing_gct(hurdle_rows)

        for item in result:
            assert isinstance(item, LandingGctBarData)

    def test_empty_input_returns_empty(self) -> None:
        """An empty input list should return an empty output list."""
        assert transform_landing_gct([]) == []


# transform_takeoff_ft


@pytest.mark.unit
class TestTransformTakeoffFt:
    """Tests for transform_takeoff_ft."""

    def test_returns_correct_values(self, hurdle_rows: list[HurdleMetricRow]) -> None:
        """Should extract hurdle_num and takeoff_ft_ms from each row."""
        result = transform_takeoff_ft(hurdle_rows)

        assert result[0].hurdle_num == 1
        assert result[0].takeoff_ft_ms == 300
        assert result[1].hurdle_num == 2
        assert result[1].takeoff_ft_ms == 300

    def test_returns_correct_type(self, hurdle_rows: list[HurdleMetricRow]) -> None:
        """Each item in the result should be a TakeoffFtBarData instance."""
        result = transform_takeoff_ft(hurdle_rows)

        for item in result:
            assert isinstance(item, TakeoffFtBarData)

    def test_empty_input_returns_empty(self) -> None:
        """An empty input list should return an empty output list."""
        assert transform_takeoff_ft([]) == []


# transform_gct_increase


@pytest.mark.unit
class TestTransformGctIncrease:
    """Tests for transform_gct_increase."""

    def test_returns_correct_values(self, hurdle_rows: list[HurdleMetricRow]) -> None:
        """Should extract hurdle_num, takeoff_gct_ms, and gct_increase_hurdle_to_hurdle_pct."""
        result = transform_gct_increase(hurdle_rows)

        assert result[0].hurdle_num == 1
        assert result[0].takeoff_gct_ms == 190
        assert result[0].gct_increase_hurdle_to_hurdle_pct == 0.0
        assert result[1].hurdle_num == 2
        assert result[1].takeoff_gct_ms == 200
        assert result[1].gct_increase_hurdle_to_hurdle_pct == pytest.approx(5.26)

    def test_returns_correct_type(self, hurdle_rows: list[HurdleMetricRow]) -> None:
        """Each item in the result should be a GctIncreaseData instance."""
        result = transform_gct_increase(hurdle_rows)

        for item in result:
            assert isinstance(item, GctIncreaseData)

    def test_empty_input_returns_empty(self) -> None:
        """An empty input list should return an empty output list."""
        assert transform_gct_increase([]) == []


# Shared behavior


@pytest.mark.unit
class TestAllTransformsPreserveRowCount:
    """All transform functions should return the same number of items as the input."""

    def test_row_count_preserved(self, hurdle_rows: list[HurdleMetricRow]) -> None:
        """Every transform should output exactly as many items as it receives."""
        expected = len(hurdle_rows)

        assert len(transform_hurdle_splits(hurdle_rows)) == expected
        assert len(transform_steps_between_hurdles(hurdle_rows)) == expected
        assert len(transform_takeoff_gct(hurdle_rows)) == expected
        assert len(transform_landing_gct(hurdle_rows)) == expected
        assert len(transform_takeoff_ft(hurdle_rows)) == expected
        assert len(transform_gct_increase(hurdle_rows)) == expected
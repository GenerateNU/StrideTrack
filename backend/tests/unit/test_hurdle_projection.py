import numpy as np
import pytest

from app.schemas.hurdle_schemas import HurdleMetricRow
from app.utils.hurdle_projection import (
    EVENT_CONFIG,
    _compute_confidence,
    _fit_linear_trend,
    project_hurdle_race,
)

# Fixtures


@pytest.fixture
def five_hurdle_metrics() -> list[HurdleMetricRow]:
    """Five hurdles with increasing splits (typical fatigue pattern)."""
    return [
        HurdleMetricRow(
            hurdle_num=1,
            clearance_start_ms=2180,
            clearance_end_ms=2760,
            takeoff_ft_ms=580,
            hurdle_split_ms=1070,
            steps_between_hurdles=3,
            takeoff_foot="right",
            takeoff_gct_ms=100,
            landing_foot="left",
            landing_gct_ms=100,
            gct_increase_hurdle_to_hurdle_pct=0.0,
        ),
        HurdleMetricRow(
            hurdle_num=2,
            clearance_start_ms=3250,
            clearance_end_ms=3840,
            takeoff_ft_ms=590,
            hurdle_split_ms=1100,
            steps_between_hurdles=3,
            takeoff_foot="right",
            takeoff_gct_ms=110,
            landing_foot="left",
            landing_gct_ms=110,
            gct_increase_hurdle_to_hurdle_pct=10.0,
        ),
        HurdleMetricRow(
            hurdle_num=3,
            clearance_start_ms=4350,
            clearance_end_ms=4910,
            takeoff_ft_ms=560,
            hurdle_split_ms=1130,
            steps_between_hurdles=3,
            takeoff_foot="right",
            takeoff_gct_ms=100,
            landing_foot="left",
            landing_gct_ms=110,
            gct_increase_hurdle_to_hurdle_pct=0.0,
        ),
        HurdleMetricRow(
            hurdle_num=4,
            clearance_start_ms=5480,
            clearance_end_ms=6080,
            takeoff_ft_ms=600,
            hurdle_split_ms=1160,
            steps_between_hurdles=3,
            takeoff_foot="right",
            takeoff_gct_ms=90,
            landing_foot="left",
            landing_gct_ms=110,
            gct_increase_hurdle_to_hurdle_pct=-10.0,
        ),
        HurdleMetricRow(
            hurdle_num=5,
            clearance_start_ms=6640,
            clearance_end_ms=7180,
            takeoff_ft_ms=540,
            hurdle_split_ms=None,
            steps_between_hurdles=None,
            takeoff_foot="right",
            takeoff_gct_ms=110,
            landing_foot="left",
            landing_gct_ms=120,
            gct_increase_hurdle_to_hurdle_pct=10.0,
        ),
    ]


@pytest.fixture
def two_hurdle_metrics() -> list[HurdleMetricRow]:
    """Minimal case: two hurdles, one split."""
    return [
        HurdleMetricRow(
            hurdle_num=1,
            clearance_start_ms=2180,
            clearance_end_ms=2760,
            takeoff_ft_ms=580,
            hurdle_split_ms=1100,
            steps_between_hurdles=3,
            takeoff_foot="right",
            takeoff_gct_ms=100,
            landing_foot="left",
            landing_gct_ms=100,
            gct_increase_hurdle_to_hurdle_pct=0.0,
        ),
        HurdleMetricRow(
            hurdle_num=2,
            clearance_start_ms=3280,
            clearance_end_ms=3840,
            takeoff_ft_ms=560,
            hurdle_split_ms=None,
            steps_between_hurdles=None,
            takeoff_foot="right",
            takeoff_gct_ms=110,
            landing_foot="left",
            landing_gct_ms=110,
            gct_increase_hurdle_to_hurdle_pct=10.0,
        ),
    ]


@pytest.fixture
def single_hurdle_metric() -> list[HurdleMetricRow]:
    """Only one hurdle, not enough data for a trend."""
    return [
        HurdleMetricRow(
            hurdle_num=1,
            clearance_start_ms=2180,
            clearance_end_ms=2760,
            takeoff_ft_ms=580,
            hurdle_split_ms=None,
            steps_between_hurdles=None,
            takeoff_foot="right",
            takeoff_gct_ms=100,
            landing_foot="left",
            landing_gct_ms=100,
            gct_increase_hurdle_to_hurdle_pct=0.0,
        ),
    ]


# _fit_linear_trend


@pytest.mark.unit
class TestFitLinearTrend:
    """Tests for _fit_linear_trend."""

    def test_perfect_linear_data(self) -> None:
        """With perfectly linear data (y = 30x + 1000), slope should be 30
        and intercept should be 1000."""
        hurdle_nums = np.array([1, 2, 3, 4])
        split_values = np.array([1030, 1060, 1090, 1120])

        slope, intercept = _fit_linear_trend(hurdle_nums, split_values)

        assert slope == pytest.approx(30.0)
        assert intercept == pytest.approx(1000.0)

    def test_constant_data_gives_zero_slope(self) -> None:
        """When all splits are identical, the slope should be 0."""
        hurdle_nums = np.array([1, 2, 3, 4])
        split_values = np.array([1100, 1100, 1100, 1100])

        slope, intercept = _fit_linear_trend(hurdle_nums, split_values)

        assert slope == pytest.approx(0.0)
        assert intercept == pytest.approx(1100.0)

    def test_two_points(self) -> None:
        """With exactly two points, the fit should be exact."""
        hurdle_nums = np.array([1, 2])
        split_values = np.array([1000, 1050])

        slope, intercept = _fit_linear_trend(hurdle_nums, split_values)

        assert slope == pytest.approx(50.0)
        assert intercept == pytest.approx(950.0)

    def test_negative_slope(self) -> None:
        """Decreasing splits should produce a negative slope."""
        hurdle_nums = np.array([1, 2, 3])
        split_values = np.array([1200, 1150, 1100])

        slope, _intercept = _fit_linear_trend(hurdle_nums, split_values)

        assert slope < 0


# _compute_confidence


@pytest.mark.unit
class TestComputeConfidence:
    """Tests for _compute_confidence."""

    def test_zero_completed_returns_zero(self) -> None:
        """With no completed splits, confidence should be 0."""
        assert _compute_confidence(0, 9) == 0.0

    def test_one_completed_returns_zero(self) -> None:
        """With only one split, we can't fit a trend, so confidence is 0."""
        assert _compute_confidence(1, 9) == 0.0

    def test_zero_total_returns_zero(self) -> None:
        """If total is 0, confidence should be 0 (avoid division by zero)."""
        assert _compute_confidence(3, 0) == 0.0

    def test_all_completed_gives_high_confidence(self) -> None:
        """Completing all splits should give confidence near 1.0."""
        result = _compute_confidence(9, 9)
        assert result >= 0.9

    def test_half_completed_gives_moderate_confidence(self) -> None:
        """Completing roughly half should give moderate confidence."""
        result = _compute_confidence(4, 9)
        assert 0.3 < result < 0.7

    def test_confidence_increases_with_more_data(self) -> None:
        """More completed splits should yield higher confidence."""
        c3 = _compute_confidence(3, 9)
        c6 = _compute_confidence(6, 9)
        c8 = _compute_confidence(8, 9)

        assert c3 < c6 < c8

    def test_result_is_between_zero_and_one(self) -> None:
        """Confidence should always be in [0, 1]."""
        for completed in range(0, 10):
            result = _compute_confidence(completed, 9)
            assert 0.0 <= result <= 1.0


# project_hurdle_race


@pytest.mark.unit
class TestProjectHurdleRace:
    """Tests for the main projection function."""

    def test_unknown_target_event_raises(
        self, five_hurdle_metrics: list[HurdleMetricRow]
    ) -> None:
        """An unrecognized target event should raise a ValueError."""
        with pytest.raises(ValueError, match="Unknown target event"):
            project_hurdle_race(five_hurdle_metrics, target_event="hurdles_999m")

    def test_insufficient_data_returns_no_projection(
        self, single_hurdle_metric: list[HurdleMetricRow]
    ) -> None:
        """With only one hurdle (zero splits), projected_total_ms should be None
        and confidence should be 0."""
        result = project_hurdle_race(single_hurdle_metric, target_event="hurdles_110m")

        assert result["projected_total_ms"] is None
        assert result["confidence"] == 0.0
        assert result["projected_splits"] == []

    def test_completed_splits_extracted_correctly(
        self, five_hurdle_metrics: list[HurdleMetricRow]
    ) -> None:
        """Should extract 4 completed splits (hurdle 5 has no split)."""
        result = project_hurdle_race(five_hurdle_metrics, target_event="hurdles_110m")

        assert len(result["completed_splits"]) == 4
        assert result["completed_splits"][0]["split_ms"] == 1070
        assert result["completed_splits"][1]["split_ms"] == 1100
        assert result["completed_splits"][2]["split_ms"] == 1130
        assert result["completed_splits"][3]["split_ms"] == 1160

    def test_projected_splits_count(
        self, five_hurdle_metrics: list[HurdleMetricRow]
    ) -> None:
        """For a 110mH (10 hurdles, 9 total splits), with 4 completed splits,
        we should get 5 projected splits (hurdles 5-9)."""
        result = project_hurdle_race(five_hurdle_metrics, target_event="hurdles_110m")

        assert len(result["projected_splits"]) == 5

    def test_projected_splits_hurdle_numbers(
        self, five_hurdle_metrics: list[HurdleMetricRow]
    ) -> None:
        """Projected splits should cover hurdle numbers 5 through 9."""
        result = project_hurdle_race(five_hurdle_metrics, target_event="hurdles_110m")

        projected_nums = [s["hurdle_num"] for s in result["projected_splits"]]
        assert projected_nums == [5, 6, 7, 8, 9]

    def test_projected_splits_increase_with_positive_trend(
        self, five_hurdle_metrics: list[HurdleMetricRow]
    ) -> None:
        """With increasing completed splits, projected splits should also increase."""
        result = project_hurdle_race(five_hurdle_metrics, target_event="hurdles_110m")

        projected_values = [s["split_ms"] for s in result["projected_splits"]]
        for i in range(1, len(projected_values)):
            assert projected_values[i] >= projected_values[i - 1]

    def test_projected_splits_are_non_negative(
        self, five_hurdle_metrics: list[HurdleMetricRow]
    ) -> None:
        """Projected split values should never be negative."""
        result = project_hurdle_race(five_hurdle_metrics, target_event="hurdles_110m")

        for s in result["projected_splits"]:
            assert s["split_ms"] >= 0

    def test_final_segment_matches_config(
        self, five_hurdle_metrics: list[HurdleMetricRow]
    ) -> None:
        """The projected final segment should match the EVENT_CONFIG value."""
        result = project_hurdle_race(five_hurdle_metrics, target_event="hurdles_110m")

        assert (
            result["projected_final_segment_ms"]
            == EVENT_CONFIG["hurdles_110m"]["final_segment_ms"]
        )

    def test_total_time_is_sum_of_parts(
        self, five_hurdle_metrics: list[HurdleMetricRow]
    ) -> None:
        """projected_total_ms should equal first_clearance + completed_sum +
        projected_sum + final_segment."""
        result = project_hurdle_race(five_hurdle_metrics, target_event="hurdles_110m")

        first_clearance = five_hurdle_metrics[0].clearance_start_ms
        completed_sum = sum(s["split_ms"] for s in result["completed_splits"])
        projected_sum = sum(s["split_ms"] for s in result["projected_splits"])
        final_segment = result["projected_final_segment_ms"]

        expected = first_clearance + completed_sum + projected_sum + final_segment
        assert result["projected_total_ms"] == expected

    def test_confidence_is_between_zero_and_one(
        self, five_hurdle_metrics: list[HurdleMetricRow]
    ) -> None:
        """Confidence should be in [0, 1]."""
        result = project_hurdle_race(five_hurdle_metrics, target_event="hurdles_110m")

        assert 0.0 <= result["confidence"] <= 1.0

    def test_target_event_and_total_hurdles_in_response(
        self, five_hurdle_metrics: list[HurdleMetricRow]
    ) -> None:
        """Response should include the target event and total hurdle count."""
        result = project_hurdle_race(five_hurdle_metrics, target_event="hurdles_110m")

        assert result["target_event"] == "hurdles_110m"
        assert result["total_hurdles"] == 10

    def test_different_target_events(
        self, five_hurdle_metrics: list[HurdleMetricRow]
    ) -> None:
        """Projections for different target events should use different configs."""
        result_110 = project_hurdle_race(
            five_hurdle_metrics, target_event="hurdles_110m"
        )
        result_100 = project_hurdle_race(
            five_hurdle_metrics, target_event="hurdles_100m"
        )

        assert (
            result_110["projected_final_segment_ms"]
            != result_100["projected_final_segment_ms"]
        )
        assert result_110["total_hurdles"] == result_100["total_hurdles"]

    def test_minimal_two_splits(
        self, two_hurdle_metrics: list[HurdleMetricRow]
    ) -> None:
        """With only one completed split, we can't fit a trend (need 2).
        Should return no projection."""
        result = project_hurdle_race(two_hurdle_metrics, target_event="hurdles_110m")

        assert result["projected_total_ms"] is None
        assert result["confidence"] == 0.0

    def test_empty_metrics_returns_no_projection(self) -> None:
        """An empty metrics list should return no projection."""
        result = project_hurdle_race([], target_event="hurdles_110m")

        assert result["projected_total_ms"] is None
        assert result["confidence"] == 0.0
        assert result["completed_splits"] == []
        assert result["projected_splits"] == []

    def test_all_event_configs_are_valid(self) -> None:
        """Every event in EVENT_CONFIG should have hurdle_count and final_segment_ms."""
        for _event, config in EVENT_CONFIG.items():
            assert "hurdle_count" in config
            assert "final_segment_ms" in config
            assert config["hurdle_count"] > 0
            assert config["final_segment_ms"] > 0

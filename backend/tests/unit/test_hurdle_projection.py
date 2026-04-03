import numpy as np
import pytest

from app.schemas.hurdle_schemas import HurdleMetricRow
from app.utils.hurdle_projection import (
    EVENT_CONFIG,
    _compute_confidence,
    _estimate_final_segment,
    _fit_phase_trends,
    _phases_covered,
    project_hurdle_race,
)

# Fixtures


@pytest.fixture
def five_hurdle_metrics() -> list[HurdleMetricRow]:
    """Five hurdles with gently decreasing splits (acceleration phase pattern)."""
    return [
        HurdleMetricRow(
            hurdle_num=1,
            clearance_start_ms=2380,
            clearance_end_ms=2740,
            takeoff_ft_ms=360,
            hurdle_split_ms=1080,
            steps_between_hurdles=3,
            takeoff_foot="left",
            takeoff_gct_ms=90,
            landing_foot="left",
            landing_gct_ms=100,
            gct_increase_hurdle_to_hurdle_pct=0.0,
        ),
        HurdleMetricRow(
            hurdle_num=2,
            clearance_start_ms=3460,
            clearance_end_ms=3830,
            takeoff_ft_ms=370,
            hurdle_split_ms=1070,
            steps_between_hurdles=3,
            takeoff_foot="left",
            takeoff_gct_ms=90,
            landing_foot="left",
            landing_gct_ms=100,
            gct_increase_hurdle_to_hurdle_pct=0.0,
        ),
        HurdleMetricRow(
            hurdle_num=3,
            clearance_start_ms=4530,
            clearance_end_ms=4900,
            takeoff_ft_ms=370,
            hurdle_split_ms=1065,
            steps_between_hurdles=3,
            takeoff_foot="left",
            takeoff_gct_ms=90,
            landing_foot="left",
            landing_gct_ms=100,
            gct_increase_hurdle_to_hurdle_pct=0.0,
        ),
        HurdleMetricRow(
            hurdle_num=4,
            clearance_start_ms=5595,
            clearance_end_ms=5960,
            takeoff_ft_ms=365,
            hurdle_split_ms=1060,
            steps_between_hurdles=3,
            takeoff_foot="left",
            takeoff_gct_ms=90,
            landing_foot="left",
            landing_gct_ms=100,
            gct_increase_hurdle_to_hurdle_pct=0.0,
        ),
        HurdleMetricRow(
            hurdle_num=5,
            clearance_start_ms=6655,
            clearance_end_ms=7020,
            takeoff_ft_ms=365,
            hurdle_split_ms=None,
            steps_between_hurdles=None,
            takeoff_foot="left",
            takeoff_gct_ms=90,
            landing_foot="left",
            landing_gct_ms=100,
            gct_increase_hurdle_to_hurdle_pct=0.0,
        ),
    ]


@pytest.fixture
def two_hurdle_metrics() -> list[HurdleMetricRow]:
    """Minimal case: two hurdles, one split."""
    return [
        HurdleMetricRow(
            hurdle_num=1,
            clearance_start_ms=2380,
            clearance_end_ms=2740,
            takeoff_ft_ms=360,
            hurdle_split_ms=1080,
            steps_between_hurdles=3,
            takeoff_foot="left",
            takeoff_gct_ms=90,
            landing_foot="left",
            landing_gct_ms=100,
            gct_increase_hurdle_to_hurdle_pct=0.0,
        ),
        HurdleMetricRow(
            hurdle_num=2,
            clearance_start_ms=3460,
            clearance_end_ms=3830,
            takeoff_ft_ms=370,
            hurdle_split_ms=None,
            steps_between_hurdles=None,
            takeoff_foot="left",
            takeoff_gct_ms=90,
            landing_foot="left",
            landing_gct_ms=100,
            gct_increase_hurdle_to_hurdle_pct=0.0,
        ),
    ]


@pytest.fixture
def single_hurdle_metric() -> list[HurdleMetricRow]:
    """Only one hurdle, not enough data for a trend."""
    return [
        HurdleMetricRow(
            hurdle_num=1,
            clearance_start_ms=2380,
            clearance_end_ms=2740,
            takeoff_ft_ms=360,
            hurdle_split_ms=None,
            steps_between_hurdles=None,
            takeoff_foot="left",
            takeoff_gct_ms=90,
            landing_foot="left",
            landing_gct_ms=100,
            gct_increase_hurdle_to_hurdle_pct=0.0,
        ),
    ]


# _fit_phase_trends


@pytest.mark.unit
class TestFitPhaseTrends:
    """Tests for _fit_phase_trends."""

    def test_fits_trend_for_phase_with_enough_data(self) -> None:
        """Phase 0 with 3 data points should produce a trend."""
        hurdle_indices = np.array([1, 2, 3])
        split_values = np.array([1080, 1070, 1065])
        boundaries = (4, 7)

        trends = _fit_phase_trends(hurdle_indices, split_values, boundaries)

        assert 0 in trends
        slope, _intercept = trends[0]
        assert slope < 0  # decreasing splits

    def test_no_trend_for_phase_with_insufficient_data(self) -> None:
        """A phase with only 1 data point should not produce a trend."""
        hurdle_indices = np.array([1, 2, 3, 5])
        split_values = np.array([1080, 1070, 1065, 1050])
        boundaries = (4, 7)

        trends = _fit_phase_trends(hurdle_indices, split_values, boundaries)

        assert 0 in trends
        assert 1 not in trends

    def test_multiple_phases_fitted(self) -> None:
        """Data spanning two phases should produce trends for both."""
        hurdle_indices = np.array([1, 2, 3, 4, 5, 6])
        split_values = np.array([1080, 1070, 1065, 1055, 1050, 1060])
        boundaries = (4, 7)

        trends = _fit_phase_trends(hurdle_indices, split_values, boundaries)

        assert 0 in trends  # indices 1,2,3
        assert 1 in trends  # indices 4,5,6

    def test_empty_input_returns_no_trends(self) -> None:
        """Empty arrays should return no trends."""
        trends = _fit_phase_trends(np.array([]), np.array([]), (4, 7))

        assert trends == {}


# _compute_confidence


@pytest.mark.unit
class TestComputeConfidence:
    """Tests for _compute_confidence."""

    def test_zero_completed_returns_zero(self) -> None:
        assert _compute_confidence(0, 10, 0) == 0.0

    def test_one_completed_returns_zero(self) -> None:
        assert _compute_confidence(1, 10, 1) == 0.0

    def test_zero_total_returns_zero(self) -> None:
        assert _compute_confidence(3, 0, 1) == 0.0

    def test_all_completed_all_phases_gives_high_confidence(self) -> None:
        result = _compute_confidence(9, 10, 3)
        assert result >= 0.9

    def test_half_completed_one_phase_gives_moderate_confidence(self) -> None:
        result = _compute_confidence(4, 10, 1)
        assert 0.2 < result < 0.6

    def test_more_phases_increases_confidence(self) -> None:
        """Same number of splits, but covering more phases should score higher."""
        c1 = _compute_confidence(4, 10, 1)
        c2 = _compute_confidence(4, 10, 2)
        c3 = _compute_confidence(4, 10, 3)

        assert c1 < c2 < c3

    def test_more_data_increases_confidence(self) -> None:
        c3 = _compute_confidence(3, 10, 1)
        c6 = _compute_confidence(6, 10, 2)
        c8 = _compute_confidence(8, 10, 3)

        assert c3 < c6 < c8

    def test_result_is_between_zero_and_one(self) -> None:
        for completed in range(0, 10):
            for phases in range(0, 4):
                result = _compute_confidence(completed, 10, phases)
                assert 0.0 <= result <= 1.0


# _phases_covered


@pytest.mark.unit
class TestPhasesCovered:
    """Tests for _phases_covered."""

    def test_single_phase(self) -> None:
        assert _phases_covered([1, 2, 3], (4, 7)) == 1

    def test_two_phases(self) -> None:
        assert _phases_covered([1, 2, 5, 6], (4, 7)) == 2

    def test_all_three_phases(self) -> None:
        assert _phases_covered([1, 5, 8], (4, 7)) == 3

    def test_empty_list(self) -> None:
        assert _phases_covered([], (4, 7)) == 0


# _estimate_final_segment


@pytest.mark.unit
class TestEstimateFinalSegment:
    """Tests for _estimate_final_segment."""

    def test_empty_splits_returns_zero(self) -> None:
        assert _estimate_final_segment([], 9.14, 13.02) == 0

    def test_uses_last_two_splits(self) -> None:
        """The estimate should be based on the last 2 splits, not all of them."""
        result_all_same = _estimate_final_segment([1000, 1000, 1000], 9.14, 13.02)
        result_late_higher = _estimate_final_segment([1000, 1000, 1200], 9.14, 13.02)

        assert result_late_higher > result_all_same

    def test_longer_segment_gives_higher_estimate(self) -> None:
        short = _estimate_final_segment([1000], 9.14, 8.72)
        long = _estimate_final_segment([1000], 9.14, 13.02)

        assert long > short

    def test_result_is_positive(self) -> None:
        result = _estimate_final_segment([1080, 1060], 9.14, 13.02)
        assert result > 0


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
        assert result["projected_final_segment_ms"] is None
        assert result["confidence"] == 0.0
        assert result["projected_splits"] == []

    def test_completed_splits_extracted_correctly(
        self, five_hurdle_metrics: list[HurdleMetricRow]
    ) -> None:
        """Should extract 4 completed splits (hurdle 5 has no split)."""
        result = project_hurdle_race(five_hurdle_metrics, target_event="hurdles_110m")

        assert len(result["completed_splits"]) == 4
        assert result["completed_splits"][0]["split_ms"] == 1080
        assert result["completed_splits"][1]["split_ms"] == 1070
        assert result["completed_splits"][2]["split_ms"] == 1065
        assert result["completed_splits"][3]["split_ms"] == 1060

    def test_projected_splits_count(
        self, five_hurdle_metrics: list[HurdleMetricRow]
    ) -> None:
        """For 110mH (10 hurdles, 9 splits), with 4 completed, we get 5 projected."""
        result = project_hurdle_race(five_hurdle_metrics, target_event="hurdles_110m")

        assert len(result["projected_splits"]) == 5

    def test_projected_splits_hurdle_numbers(
        self, five_hurdle_metrics: list[HurdleMetricRow]
    ) -> None:
        """Projected splits should cover hurdle numbers 5 through 9."""
        result = project_hurdle_race(five_hurdle_metrics, target_event="hurdles_110m")

        projected_nums = [s["hurdle_num"] for s in result["projected_splits"]]
        assert projected_nums == [5, 6, 7, 8, 9]

    def test_projected_splits_show_three_phase_shape(
        self, five_hurdle_metrics: list[HurdleMetricRow]
    ) -> None:
        """Projected splits should dip at peak speed then climb through fatigue."""
        result = project_hurdle_race(five_hurdle_metrics, target_event="hurdles_110m")

        projected = result["projected_splits"]
        # H5 (peak) should be lower than H9 (fatigue)
        assert projected[0]["split_ms"] < projected[-1]["split_ms"]
        # Late splits should climb
        assert projected[-1]["split_ms"] > projected[-2]["split_ms"]

    def test_final_segment_is_pace_based(
        self, five_hurdle_metrics: list[HurdleMetricRow]
    ) -> None:
        """Final segment should be a positive value derived from pace, not a config lookup."""
        result = project_hurdle_race(five_hurdle_metrics, target_event="hurdles_110m")

        assert result["projected_final_segment_ms"] is not None
        assert result["projected_final_segment_ms"] > 0

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

    def test_different_target_events_produce_different_final_segments(
        self, five_hurdle_metrics: list[HurdleMetricRow]
    ) -> None:
        """Different events have different distances, so final segments should differ."""
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

    def test_minimal_two_splits(
        self, two_hurdle_metrics: list[HurdleMetricRow]
    ) -> None:
        """With only one completed split, should return no projection."""
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
        """Every event in EVENT_CONFIG should have the required fields."""
        required_keys = {
            "hurdle_count",
            "inter_hurdle_m",
            "final_segment_m",
            "phase_boundaries",
            "template_ratios",
        }
        for event, config in EVENT_CONFIG.items():
            missing = required_keys - set(config.keys())
            assert not missing, f"{event} missing keys: {missing}"
            assert config["hurdle_count"] > 0
            assert config["inter_hurdle_m"] > 0
            assert config["final_segment_m"] > 0
            assert len(config["template_ratios"]) == config["hurdle_count"]

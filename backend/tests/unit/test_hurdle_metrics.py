import numpy as np
import pandas as pd
import pytest
 
from app.utils.hurdle_metrics import (
    Interval,
    _compute_gaps,
    _count_steps_between,
    _filter_hurdle_gaps,
    _first_contact_after,
    _last_contact_before,
    calc_gct_increase_hurdle_to_hurdle_pct,
    calc_hurdle_split_ms,
    calc_landing_gct_ms,
    calc_steps_between_hurdles,
    calc_takeoff_ft_ms,
    calc_takeoff_gct_ms,
    transform_stride_cycles_to_hurdle_metrics,
)


# Fixtures
 
 
@pytest.fixture
def steps_df() -> pd.DataFrame:
    """A DataFrame with two hurdle-length gaps."""
    return pd.DataFrame(
        {
            "foot": ["left", "right", "left", "right", "left"],
            "ic_time": [0, 210, 700, 910, 1400],
            "to_time": [200, 400, 900, 1100, 1600],
            "gct_ms": [200, 190, 200, 190, 200],
        }
    )
 

@pytest.fixture
def empty_steps_df() -> pd.DataFrame:
    """An empty DataFrame with the required columns."""
    return pd.DataFrame(columns=["foot", "ic_time", "to_time", "gct_ms"])


# _compute_gaps
 
 
@pytest.mark.unit
class TestComputeGaps:
    """Tests for _compute_gaps."""
 
    def test_gap_between_two_intervals(self) -> None:
        """Two non-overlapping intervals with space between them should produce one gap."""
        contacts = [Interval(0, 100), Interval(200, 300)]
        gaps = _compute_gaps(contacts)
 
        assert len(gaps) == 1
        assert gaps[0].start == 100
        assert gaps[0].end == 200
 
    def test_adjacent_intervals_produce_no_gap(self) -> None:
        """When one interval ends exactly where the next begins, there's no gap."""
        contacts = [Interval(0, 100), Interval(100, 200)]
        gaps = _compute_gaps(contacts)
 
        assert len(gaps) == 0
 
    def test_overlapping_intervals_produce_no_gap(self) -> None:
        """When intervals overlap, there's no gap."""
        contacts = [Interval(0, 150), Interval(100, 200)]
        gaps = _compute_gaps(contacts)
 
        assert len(gaps) == 0
 
    def test_multiple_gaps(self) -> None:
        """Three intervals with gaps between each pair should produce two gaps."""
        contacts = [Interval(0, 100), Interval(200, 300), Interval(500, 600)]
        gaps = _compute_gaps(contacts)
 
        assert len(gaps) == 2
        assert gaps[0] == Interval(100, 200)
        assert gaps[1] == Interval(300, 500)
 
    def test_single_interval_returns_empty(self) -> None:
        """A single contact interval has nothing to compare against, so no gaps."""
        gaps = _compute_gaps([Interval(0, 100)])
        assert len(gaps) == 0
 
    def test_empty_list_returns_empty(self) -> None:
        """An empty contact list should return an empty gap list."""
        gaps = _compute_gaps([])
        assert len(gaps) == 0


# _filter_hurdle_gaps
 
 
@pytest.mark.unit
class TestFilterHurdleGaps:
    """Tests for _filter_hurdle_gaps."""
 
    def test_keeps_gaps_above_min(self) -> None:
        """Gaps with duration >= min_ms should be kept."""
        gaps = [Interval(0, 300), Interval(500, 600)]
        result = _filter_hurdle_gaps(gaps, min_ms=260)
 
        assert len(result) == 1
        assert result[0] == Interval(0, 300)
 
    def test_filters_gaps_below_min(self) -> None:
        """Gaps with duration < min_ms should be excluded."""
        gaps = [Interval(0, 100)]
        result = _filter_hurdle_gaps(gaps, min_ms=260)
 
        assert len(result) == 0
 
    def test_max_ms_filters_long_gaps(self) -> None:
        """When max_ms is set, gaps exceeding it should be excluded."""
        gaps = [Interval(0, 300), Interval(500, 1200)]
        result = _filter_hurdle_gaps(gaps, min_ms=260, max_ms=500)
 
        assert len(result) == 1
        assert result[0] == Interval(0, 300)
 
    def test_max_ms_none_allows_all_long_gaps(self) -> None:
        """When max_ms is None, no upper limit is applied."""
        gaps = [Interval(0, 5000)]
        result = _filter_hurdle_gaps(gaps, min_ms=260, max_ms=None)
 
        assert len(result) == 1
 
    def test_empty_input_returns_empty(self) -> None:
        """An empty gap list should return an empty result."""
        result = _filter_hurdle_gaps([], min_ms=260)
        assert len(result) == 0
 
    def test_exact_min_boundary_included(self) -> None:
        """A gap whose duration exactly equals min_ms should NOT be included."""
        gaps = [Interval(0, 260)]
        result = _filter_hurdle_gaps(gaps, min_ms=260)
 
        assert len(result) == 1


# Step Lookup Helpers
 
 
@pytest.mark.unit
class TestLastContactBefore:
    """Tests for _last_contact_before."""
 
    def test_finds_correct_step(self, steps_df: pd.DataFrame) -> None:
        """At t_ms=400 (hurdle gap 1 start), the last contact ending at or before 400
        is step 2 (to_time=400)."""
        result = _last_contact_before(steps_df, t_ms=400)
 
        assert result is not None
        assert result["to_time"] == 400
 
    def test_returns_none_when_no_candidates(self, steps_df: pd.DataFrame) -> None:
        """When t_ms is before any step's to_time, there are no candidates."""
        result = _last_contact_before(steps_df, t_ms=0)

        assert result is None
 
    def test_returns_none_on_empty_df(self, empty_steps_df: pd.DataFrame) -> None:
        """An empty DataFrame should return None."""
        result = _last_contact_before(empty_steps_df, t_ms=500)
        assert result is None
 
 
@pytest.mark.unit
class TestFirstContactAfter:
    """Tests for _first_contact_after."""
 
    def test_finds_correct_step(self, steps_df: pd.DataFrame) -> None:
        """At t_ms=700 (hurdle gap 1 end), the first contact starting at or after 700
        is step 3 (ic_time=700)."""
        result = _first_contact_after(steps_df, t_ms=700)
 
        assert result is not None
        assert result["ic_time"] == 700
 
    def test_returns_none_when_no_candidates(self, steps_df: pd.DataFrame) -> None:
        """When t_ms is after every step's ic_time, there are no candidates."""
        result = _first_contact_after(steps_df, t_ms=9999)
        assert result is None
 
    def test_returns_none_on_empty_df(self, empty_steps_df: pd.DataFrame) -> None:
        """An empty DataFrame should return None."""
        result = _first_contact_after(empty_steps_df, t_ms=0)
        assert result is None
 
 
@pytest.mark.unit
class TestCountStepsBetween:
    """Tests for _count_steps_between."""
 
    def test_counts_correctly(self, steps_df: pd.DataFrame) -> None:
        """Between hurdle gap 1 end (700) and hurdle gap 2 start (1100), the ICs
        strictly between are ic_time=910, count of 1."""
        result = _count_steps_between(steps_df, t_start_exclusive=700, t_end_exclusive=1100)
        assert result == 1
 
    def test_excludes_boundary_values(self, steps_df: pd.DataFrame) -> None:
        """ICs exactly at the boundaries should not be counted (strictly between)."""
        result = _count_steps_between(steps_df, t_start_exclusive=700, t_end_exclusive=910)
        assert result == 0
 
    def test_empty_range_returns_zero(self, steps_df: pd.DataFrame) -> None:
        """When start >= end, no ICs can fall strictly between them."""
        result = _count_steps_between(steps_df, t_start_exclusive=500, t_end_exclusive=500)
        assert result == 0
 
    def test_empty_df_returns_zero(self, empty_steps_df: pd.DataFrame) -> None:
        """An empty DataFrame should return 0."""
        result = _count_steps_between(empty_steps_df, t_start_exclusive=0, t_end_exclusive=9999)
        assert result == 0


# transform_stride_cycles_to_hurdle_metrics (main pipeline)
 
 
@pytest.mark.unit
class TestTransformStrideCyclesToHurdleMetrics:
    """Tests for the main hurdle metrics transformation."""
 
    def test_missing_columns_raises_value_error(self) -> None:
        """A DataFrame missing required columns should raise a ValueError."""
        df = pd.DataFrame({"foot": ["left"], "ic_time": [0]})
 
        with pytest.raises(ValueError, match="Missing required columns"):
            transform_stride_cycles_to_hurdle_metrics(df)
 
    def test_empty_input_returns_empty_with_schema(self, empty_steps_df: pd.DataFrame) -> None:
        """An empty DataFrame should return an empty DataFrame with the full output
        column schema."""
        result = transform_stride_cycles_to_hurdle_metrics(empty_steps_df)
 
        assert result.empty
        expected_cols = [
            "hurdle_num", "clearance_start_ms", "clearance_end_ms", "takeoff_ft_ms",
            "hurdle_split_ms", "steps_between_hurdles", "takeoff_foot", "takeoff_gct_ms",
            "landing_foot", "landing_gct_ms", "gct_increase_hurdle_to_hurdle_pct",
        ]
        assert list(result.columns) == expected_cols
 
    def test_detects_correct_number_of_hurdles(self, steps_df: pd.DataFrame) -> None:
        """The fixture has two gaps of 300ms each (above default min of 260ms),
        so two hurdles should be detected."""
        result = transform_stride_cycles_to_hurdle_metrics(steps_df)
 
        assert len(result) == 2
        assert list(result["hurdle_num"]) == [1, 2]
 
    def test_clearance_times_are_correct(self, steps_df: pd.DataFrame) -> None:
        """Hurdle 1 clearance should be 400-700 and hurdle 2 should be 1100-1400."""
        result = transform_stride_cycles_to_hurdle_metrics(steps_df)
 
        assert result.iloc[0]["clearance_start_ms"] == 400
        assert result.iloc[0]["clearance_end_ms"] == 700
        assert result.iloc[1]["clearance_start_ms"] == 1100
        assert result.iloc[1]["clearance_end_ms"] == 1400
 
    def test_takeoff_ft_is_gap_duration(self, steps_df: pd.DataFrame) -> None:
        """Takeoff flight time should equal the gap duration (end - start).
        Both gaps are 300ms."""
        result = transform_stride_cycles_to_hurdle_metrics(steps_df)
 
        assert result.iloc[0]["takeoff_ft_ms"] == 300
        assert result.iloc[1]["takeoff_ft_ms"] == 300
 
    def test_hurdle_split_ms(self, steps_df: pd.DataFrame) -> None:
        """Hurdle split is the time between consecutive hurdle clearance starts.
        Hurdle 1 start=400, hurdle 2 start=1100, so split = 700ms.
        The last hurdle has no next hurdle, so its split is NaN."""
        result = transform_stride_cycles_to_hurdle_metrics(steps_df)
 
        assert result.iloc[0]["hurdle_split_ms"] == 700
        assert pd.isna(result.iloc[1]["hurdle_split_ms"])
 
    def test_steps_between_hurdles(self, steps_df: pd.DataFrame) -> None:
        """Between hurdle 1 end (700) and hurdle 2 start (1100), the ICs strictly
        between are 910, 1 step. The last hurdle has no next, so NaN."""
        result = transform_stride_cycles_to_hurdle_metrics(steps_df)
 
        assert result.iloc[0]["steps_between_hurdles"] == 1
        assert pd.isna(result.iloc[1]["steps_between_hurdles"])
 
    def test_takeoff_and_landing_foot_and_gct(self, steps_df: pd.DataFrame) -> None:
        """Hurdle 1: takeoff step is the last contact before 400 (step 2, right, gct=190),
        landing step is the first contact after 700 (step 3, left, gct=200)."""
        result = transform_stride_cycles_to_hurdle_metrics(steps_df)
 
        assert result.iloc[0]["takeoff_foot"] == "right"
        assert result.iloc[0]["takeoff_gct_ms"] == 190
        assert result.iloc[0]["landing_foot"] == "left"
        assert result.iloc[0]["landing_gct_ms"] == 200
 
    def test_gct_increase_hurdle_to_hurdle(self, steps_df: pd.DataFrame) -> None:
        """Both hurdles have takeoff_gct_ms=190, so the increase from hurdle 1 to
        hurdle 2 is (190-190)/190*100 = 0%."""
        result = transform_stride_cycles_to_hurdle_metrics(steps_df)
 
        assert result.iloc[0]["gct_increase_hurdle_to_hurdle_pct"] == pytest.approx(0.0)
        assert result.iloc[1]["gct_increase_hurdle_to_hurdle_pct"] == pytest.approx(0.0)
 
    def test_no_hurdle_gaps_returns_empty(self) -> None:
        """When no gaps exceed the minimum flight time, no hurdles are detected
        and the output should be empty with the correct schema."""
        df = pd.DataFrame(
            {
                "foot": ["left", "right"],
                "ic_time": [0, 100],
                "to_time": [90, 190],
                "gct_ms": [90, 90],
            }
        )
        result = transform_stride_cycles_to_hurdle_metrics(df)
 
        assert result.empty
 
    def test_custom_min_ft_parameter(self, steps_df: pd.DataFrame) -> None:
        """Raising hurdle_min_ft_ms above the gap duration (300) should result in
        no hurdles being detected."""
        result = transform_stride_cycles_to_hurdle_metrics(
            steps_df, hurdle_min_ft_ms=400
        )
 
        assert result.empty
 
    def test_output_has_correct_columns(self, steps_df: pd.DataFrame) -> None:
        """The output should contain all 11 expected columns."""
        result = transform_stride_cycles_to_hurdle_metrics(steps_df)
 
        expected_cols = [
            "hurdle_num", "clearance_start_ms", "clearance_end_ms", "takeoff_ft_ms",
            "hurdle_split_ms", "steps_between_hurdles", "takeoff_foot", "takeoff_gct_ms",
            "landing_foot", "landing_gct_ms", "gct_increase_hurdle_to_hurdle_pct",
        ]
        assert list(result.columns) == expected_cols


# Individual metric accessor functions
 
 
@pytest.mark.unit
class TestIndividualMetricAccessors:
    """Tests for the individual metric accessor functions."""
 
    def test_calc_hurdle_split_ms_columns(self, steps_df: pd.DataFrame) -> None:
        """Should return only hurdle_num and hurdle_split_ms columns."""
        result = calc_hurdle_split_ms(steps_df)
        assert list(result.columns) == ["hurdle_num", "hurdle_split_ms"]
 
    def test_calc_steps_between_hurdles_columns(self, steps_df: pd.DataFrame) -> None:
        """Should return only hurdle_num and steps_between_hurdles columns."""
        result = calc_steps_between_hurdles(steps_df)
        assert list(result.columns) == ["hurdle_num", "steps_between_hurdles"]
 
    def test_calc_takeoff_gct_ms_columns(self, steps_df: pd.DataFrame) -> None:
        """Should return only hurdle_num and takeoff_gct_ms columns."""
        result = calc_takeoff_gct_ms(steps_df)
        assert list(result.columns) == ["hurdle_num", "takeoff_gct_ms"]
 
    def test_calc_landing_gct_ms_columns(self, steps_df: pd.DataFrame) -> None:
        """Should return only hurdle_num and landing_gct_ms columns."""
        result = calc_landing_gct_ms(steps_df)
        assert list(result.columns) == ["hurdle_num", "landing_gct_ms"]
 
    def test_calc_takeoff_ft_ms_columns(self, steps_df: pd.DataFrame) -> None:
        """Should return only hurdle_num and takeoff_ft_ms columns."""
        result = calc_takeoff_ft_ms(steps_df)
        assert list(result.columns) == ["hurdle_num", "takeoff_ft_ms"]
 
    def test_calc_gct_increase_columns(self, steps_df: pd.DataFrame) -> None:
        """Should return only hurdle_num and gct_increase_hurdle_to_hurdle_pct columns."""
        result = calc_gct_increase_hurdle_to_hurdle_pct(steps_df)
        assert list(result.columns) == ["hurdle_num", "gct_increase_hurdle_to_hurdle_pct"]
 
    def test_accessor_row_counts_match_main(self, steps_df: pd.DataFrame) -> None:
        """All accessors should return the same number of rows as the main transformation."""
        main_result = transform_stride_cycles_to_hurdle_metrics(steps_df)
        expected_len = len(main_result)
 
        assert len(calc_hurdle_split_ms(steps_df)) == expected_len
        assert len(calc_steps_between_hurdles(steps_df)) == expected_len
        assert len(calc_takeoff_gct_ms(steps_df)) == expected_len
        assert len(calc_landing_gct_ms(steps_df)) == expected_len
        assert len(calc_takeoff_ft_ms(steps_df)) == expected_len
        assert len(calc_gct_increase_hurdle_to_hurdle_pct(steps_df)) == expected_len
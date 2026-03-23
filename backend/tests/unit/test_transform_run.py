import numpy as np
import pandas as pd
import pytest

from app.utils.transform_run import (
    _assign_stride_numbers,
    _build_stride_rows,
    _extract_stance_intervals,
    _fill_short_zero_dropouts_in_contact,
    _median_dt_ms,
    transform_feet_to_stride_cycles,
)

# _median_dt_ms


@pytest.mark.unit
class TestMedianDtMs:
    """Tests for _median_dt_ms."""

    def test_uniform_spacing(self) -> None:
        """Evenly spaced timestamps, should return exactly 10.0."""
        time = np.array([0, 10, 20, 30, 40], dtype=np.int64)
        assert _median_dt_ms(time) == pytest.approx(10.0)

    def test_varying_spacing_returns_median(self) -> None:
        """Non-uniform deltas, should return the statistical median 10.0."""
        time = np.array([0, 5, 15, 30], dtype=np.int64)
        assert _median_dt_ms(time) == pytest.approx(10.0)

    def test_single_element_returns_default(self) -> None:
        """A single timestamp produces no diffs, so the fallback default of 1.0 is returned."""
        time = np.array([100], dtype=np.int64)
        assert _median_dt_ms(time) == pytest.approx(1.0)

    def test_empty_array_returns_default(self) -> None:
        """An empty timestamp array has no diffs and should return the fallback default of 1.0."""
        time = np.array([], dtype=np.int64)
        assert _median_dt_ms(time) == pytest.approx(1.0)

    def test_zero_diffs_are_excluded(self) -> None:
        """Duplicate timestamps produce zero-valued diffs which should be filtered out
        before computing the median, so [10, 0, 10] becomes [10, 10] and should return 10.0"""
        time = np.array([0, 10, 10, 20], dtype=np.int64)
        assert _median_dt_ms(time) == pytest.approx(10.0)

    def test_all_zero_diffs_returns_default(self) -> None:
        """If every diff is zero (all identical timestamps), filtering removes all values
        and the fallback default of 1.0 is returned."""
        time = np.array([5, 5, 5], dtype=np.int64)
        assert _median_dt_ms(time) == pytest.approx(1.0)


# _fill_short_zero_dropouts_in_contact


@pytest.mark.unit
class TestFillShortZeroDropouts:
    """Tests for _fill_short_zero_dropouts_in_contact."""

    def test_no_gaps_unchanged(self) -> None:
        """An all-True contact signal has no gaps to fill and should be returned as-is."""
        contact = np.array([True, True, True, True])
        result = _fill_short_zero_dropouts_in_contact(contact, max_hole_len_samples=2)
        np.testing.assert_array_equal(result, contact)

    def test_short_gap_filled(self) -> None:
        """A single-sample False gap bounded by True on both sides should be filled
        when max_hole_len_samples is large enough (2 >= gap length 1)."""
        contact = np.array([True, False, True])
        result = _fill_short_zero_dropouts_in_contact(contact, max_hole_len_samples=2)
        np.testing.assert_array_equal(result, [True, True, True])

    def test_gap_exactly_at_max_hole_len_filled(self) -> None:
        """A gap whose length exactly equals max_hole_len_samples should still be filled."""
        contact = np.array([True, False, False, True])
        result = _fill_short_zero_dropouts_in_contact(contact, max_hole_len_samples=2)
        np.testing.assert_array_equal(result, [True, True, True, True])

    def test_gap_exceeding_max_hole_len_not_filled(self) -> None:
        """A gap of 3 samples exceeds max_hole_len_samples=2, so it should be left as-is
        to avoid merging genuinely separate stance phases."""
        contact = np.array([True, False, False, False, True])
        result = _fill_short_zero_dropouts_in_contact(contact, max_hole_len_samples=2)
        np.testing.assert_array_equal(result, [True, False, False, False, True])

    def test_leading_false_not_filled(self) -> None:
        """A False gap at the very start of the signal is not bounded by True on its left
        side, so it must not be filled regardless of its length."""
        contact = np.array([False, True, True])
        result = _fill_short_zero_dropouts_in_contact(contact, max_hole_len_samples=1)
        np.testing.assert_array_equal(result, [False, True, True])

    def test_trailing_false_not_filled(self) -> None:
        """A False gap at the very end of the signal is not bounded by True on its right
        side, so it must not be filled regardless of its length."""
        contact = np.array([True, True, False])
        result = _fill_short_zero_dropouts_in_contact(contact, max_hole_len_samples=1)
        np.testing.assert_array_equal(result, [True, True, False])

    def test_max_hole_len_zero_does_nothing(self) -> None:
        """When max_hole_len_samples is 0, the early-return guard should skip all
        processing and return the input unchanged."""
        contact = np.array([True, False, True])
        result = _fill_short_zero_dropouts_in_contact(contact, max_hole_len_samples=0)
        np.testing.assert_array_equal(result, [True, False, True])

    def test_negative_max_hole_len_does_nothing(self) -> None:
        """A negative max_hole_len_samples should trigger the early-return guard,
        leaving the signal unchanged."""
        contact = np.array([True, False, True])
        result = _fill_short_zero_dropouts_in_contact(contact, max_hole_len_samples=-1)
        np.testing.assert_array_equal(result, [True, False, True])

    def test_empty_array_returns_empty(self) -> None:
        """An empty contact array should pass through the early-return guard and
        produce an empty result."""
        contact = np.array([], dtype=bool)
        result = _fill_short_zero_dropouts_in_contact(contact, max_hole_len_samples=2)
        assert result.size == 0

    def test_does_not_mutate_input(self) -> None:
        """The function copies the input internally, so the original array must remain
        unchanged after the call even when gaps are filled."""
        contact = np.array([True, False, True])
        original = contact.copy()
        _fill_short_zero_dropouts_in_contact(contact, max_hole_len_samples=2)
        np.testing.assert_array_equal(contact, original)

    def test_multiple_gaps_filled_independently(self) -> None:
        """Two separate single-sample gaps should each be evaluated and filled
        independently when both are within max_hole_len_samples."""
        contact = np.array([True, False, True, False, True])
        result = _fill_short_zero_dropouts_in_contact(contact, max_hole_len_samples=1)
        np.testing.assert_array_equal(result, [True, True, True, True, True])

    def test_mixed_short_and_long_gaps(self) -> None:
        """When the signal contains both a fillable gap (length 1) and a too-long gap
        (length 3, with max=2), only the short one should be filled."""
        contact = np.array([True, False, True, False, False, False, True])
        result = _fill_short_zero_dropouts_in_contact(contact, max_hole_len_samples=2)
        np.testing.assert_array_equal(
            result, [True, True, True, False, False, False, True]
        )


# _extract_stance_intervals


@pytest.mark.unit
class TestExtractStanceIntervals:
    """Tests for _extract_stance_intervals."""

    def test_single_stance_phase(self) -> None:
        """A force signal that goes above threshold at index 1 and drops at index 4
        should produce exactly one stance interval."""
        time = np.array([0, 10, 20, 30, 40], dtype=np.int64)
        force = np.array([0, 100, 100, 100, 0], dtype=np.int64)

        result = _extract_stance_intervals(time, force, threshold=0)

        assert len(result) == 1
        assert result.iloc[0]["ic_idx"] == 1
        assert result.iloc[0]["to_idx"] == 4
        assert result.iloc[0]["ic_time_raw"] == 10
        assert result.iloc[0]["to_time_raw"] == 40

    def test_two_stance_phases(self) -> None:
        """Two separate above-threshold segments separated by a below-threshold gap
        should be detected as two distinct stance intervals."""
        time = np.array([0, 10, 20, 30, 40, 50, 60], dtype=np.int64)
        force = np.array([0, 100, 0, 0, 100, 100, 0], dtype=np.int64)

        result = _extract_stance_intervals(time, force, threshold=0)

        assert len(result) == 2

    def test_empty_arrays_return_empty_df(self) -> None:
        """Empty time/force arrays should return an empty DataFrame that still has
        the expected column schema."""
        time = np.array([], dtype=np.int64)
        force = np.array([], dtype=np.int64)

        result = _extract_stance_intervals(time, force, threshold=0)

        assert result.empty
        assert list(result.columns) == [
            "ic_idx",
            "to_idx",
            "ic_time_raw",
            "to_time_raw",
        ]

    def test_no_contact_returns_empty(self) -> None:
        """When force never exceeds the threshold, no stance intervals exist and the
        result should be an empty DataFrame."""
        time = np.array([0, 10, 20, 30], dtype=np.int64)
        force = np.array([0, 0, 0, 0], dtype=np.int64)

        result = _extract_stance_intervals(time, force, threshold=0)

        assert result.empty

    def test_all_contact_returns_single_interval(self) -> None:
        """When force exceeds threshold for the entire signal, one stance interval
        spanning the full array should be returned, with to_time_raw clamped to the
        last timestamp."""
        time = np.array([0, 10, 20, 30], dtype=np.int64)
        force = np.array([100, 100, 100, 100], dtype=np.int64)

        result = _extract_stance_intervals(time, force, threshold=0)

        assert len(result) == 1
        assert result.iloc[0]["ic_idx"] == 0
        assert result.iloc[0]["to_time_raw"] == 30

    def test_threshold_filters_low_force(self) -> None:
        """Readings at or below the threshold should be treated as non-contact, so
        only the higher-force segment is detected."""
        time = np.array([0, 10, 20, 30], dtype=np.int64)
        force = np.array([5, 50, 50, 5], dtype=np.int64)

        result = _extract_stance_intervals(time, force, threshold=10)
        assert len(result) == 1
        assert result.iloc[0]["ic_time_raw"] == 10

    def test_contact_at_start(self) -> None:
        """When force is above threshold starting from index 0, the stance interval
        should begin at ic_idx=0 / ic_time_raw=time[0]."""
        time = np.array([0, 10, 20, 30], dtype=np.int64)
        force = np.array([100, 100, 0, 0], dtype=np.int64)

        result = _extract_stance_intervals(time, force, threshold=0)

        assert len(result) == 1
        assert result.iloc[0]["ic_idx"] == 0
        assert result.iloc[0]["ic_time_raw"] == 0

    def test_contact_at_end(self) -> None:
        """When force is above threshold at the end of the signal, the stance interval
        should use time[-1] as to_time_raw since to_idx may equal n (past the array)."""
        time = np.array([0, 10, 20, 30], dtype=np.int64)
        force = np.array([0, 0, 100, 100], dtype=np.int64)

        result = _extract_stance_intervals(time, force, threshold=0)

        assert len(result) == 1
        assert result.iloc[0]["to_time_raw"] == 30


# _build_stride_rows


@pytest.mark.unit
class TestBuildStrideRows:
    """Tests for _build_stride_rows."""

    def _make_stance_df(
        self, intervals: list[tuple[int, int, int, int]]
    ) -> pd.DataFrame:
        """Create a stance df from (ic_idx, to_idx, ic_time_raw, to_time_raw) tuples."""
        return pd.DataFrame(
            intervals, columns=["ic_idx", "to_idx", "ic_time_raw", "to_time_raw"]
        )

    def test_two_stances_produce_one_stride(self) -> None:
        """Two consecutive stance intervals should be paired into one stride row where
        the first stance's IC/TO and the second stance's IC form ic_time, to_time,
        and next_ic_time respectively, and gct/flight/step_time are derived from those."""
        stance_df = self._make_stance_df(
            [
                (0, 3, 1000, 1030),
                (5, 8, 1050, 1080),
            ]
        )

        result = _build_stride_rows(stance_df, "left", t0_raw=1000)

        assert len(result) == 1
        row = result.iloc[0]
        assert row["foot"] == "left"
        assert row["ic_time"] == 0  # 1000 - 1000
        assert row["to_time"] == 30  # 1030 - 1000
        assert row["next_ic_time"] == 50  # 1050 - 1000
        assert row["gct_ms"] == 30  # to - ic
        assert row["flight_ms"] == 20  # next_ic - to
        assert row["step_time_ms"] == 50  # gct + flight

    def test_single_stance_returns_empty(self) -> None:
        """A single stance has no subsequent IC to pair with, so the next_ic_time
        column is NaN and the row is dropped, producing an empty result."""
        stance_df = self._make_stance_df(
            [
                (0, 3, 1000, 1030),
            ]
        )

        result = _build_stride_rows(stance_df, "right", t0_raw=1000)

        assert result.empty

    def test_empty_stance_df_returns_empty(self) -> None:
        """An empty stance DataFrame should return an empty DataFrame that still
        contains the full expected column schema."""
        stance_df = pd.DataFrame(
            columns=["ic_idx", "to_idx", "ic_time_raw", "to_time_raw"]
        )

        result = _build_stride_rows(stance_df, "left", t0_raw=0)

        assert result.empty
        expected_cols = [
            "foot",
            "ic_time",
            "to_time",
            "next_ic_time",
            "gct_ms",
            "flight_ms",
            "step_time_ms",
        ]
        assert list(result.columns) == expected_cols

    def test_three_stances_produce_two_strides(self) -> None:
        """Three consecutive stances create two stride rows: stance 1-2 and stance 2-3.
        The last stance has no next IC so it is not included as a stride origin."""
        stance_df = self._make_stance_df(
            [
                (0, 2, 100, 120),
                (4, 6, 140, 160),
                (8, 10, 180, 200),
            ]
        )

        result = _build_stride_rows(stance_df, "right", t0_raw=100)

        assert len(result) == 2

    def test_t0_raw_offsets_all_times(self) -> None:
        """All output timestamps (ic_time, to_time, next_ic_time) should be expressed
        relative to t0_raw, so subtracting the file's first timestamp makes them
        zero-based."""
        stance_df = self._make_stance_df(
            [
                (0, 2, 5000, 5020),
                (4, 6, 5040, 5060),
            ]
        )

        result = _build_stride_rows(stance_df, "left", t0_raw=5000)

        row = result.iloc[0]
        assert row["ic_time"] == 0
        assert row["to_time"] == 20
        assert row["next_ic_time"] == 40


# _assign_stride_numbers


@pytest.mark.unit
class TestAssignStrideNumbers:
    """Tests for _assign_stride_numbers."""

    def test_alternating_left_right(self) -> None:
        """A clean left-right-left-right sequence should assign stride 1 to the first
        pair and stride 2 to the second pair, incrementing only after both feet
        have been seen."""
        df = pd.DataFrame(
            {
                "foot": ["left", "right", "left", "right"],
                "ic_time": [0, 10, 50, 60],
            }
        )

        result = _assign_stride_numbers(df)

        assert list(result["stride_num"]) == [1, 1, 2, 2]

    def test_same_foot_twice_before_other(self) -> None:
        """When the same foot appears consecutively (left, left, right), the stride
        number should not increment until both feet have been seen."""
        df = pd.DataFrame(
            {
                "foot": ["left", "left", "right"],
                "ic_time": [0, 10, 20],
            }
        )

        result = _assign_stride_numbers(df)

        assert list(result["stride_num"]) == [1, 1, 1]

    def test_empty_df_returns_empty(self) -> None:
        """An empty DataFrame should pass through the early-return guard and be
        returned as-is without adding a stride_num column."""
        df = pd.DataFrame(columns=["foot", "ic_time"])

        result = _assign_stride_numbers(df)

        assert result.empty

    def test_single_foot_never_increments(self) -> None:
        """If only one foot is ever seen, the stride counter never reaches the
        both-feet-seen condition and stays at 1 for every row."""
        df = pd.DataFrame(
            {
                "foot": ["left", "left", "left"],
                "ic_time": [0, 50, 100],
            }
        )

        result = _assign_stride_numbers(df)

        assert list(result["stride_num"]) == [1, 1, 1]


# transform_feet_to_stride_cycles (wiring & structural tests)
# transformation logic has been tested in the above classes


@pytest.mark.unit
class TestTransformFeetToStrideCycles:
    """Tests for the main transformation entry point."""

    def test_missing_column_raises_value_error(self) -> None:
        """Passing a DataFrame that lacks one of the three required columns
        (Time, Force_Foot1, Force_Foot2) should raise a ValueError."""
        df = pd.DataFrame({"Time": [0], "Force_Foot1": [0]})

        with pytest.raises(ValueError, match="Missing required column"):
            transform_feet_to_stride_cycles(df)

    def test_empty_dataframe_returns_empty_with_correct_columns(self) -> None:
        """A DataFrame with the right columns but zero rows should return an empty
        DataFrame that still has the full 8-column output schema."""
        df = pd.DataFrame({"Time": [], "Force_Foot1": [], "Force_Foot2": []})

        result = transform_feet_to_stride_cycles(df)

        assert result.empty
        expected_cols = [
            "stride_num",
            "foot",
            "ic_time",
            "to_time",
            "next_ic_time",
            "gct_ms",
            "flight_ms",
            "step_time_ms",
        ]
        assert list(result.columns) == expected_cols

    def test_valid_input_produces_non_empty_output_with_expected_columns(self) -> None:
        """A well-formed signal with two stance phases per foot should produce a
        non-empty DataFrame containing all 8 expected output columns."""
        n = 14
        time = np.arange(0, n * 10, 10, dtype=np.int64)
        f1 = np.zeros(n, dtype=np.int64)
        f2 = np.zeros(n, dtype=np.int64)

        f1[1:4] = 100
        f2[4:7] = 100
        f1[7:10] = 100
        f2[10:13] = 100

        df = pd.DataFrame({"Time": time, "Force_Foot1": f1, "Force_Foot2": f2})

        result = transform_feet_to_stride_cycles(df)

        assert not result.empty
        expected_cols = [
            "stride_num",
            "foot",
            "ic_time",
            "to_time",
            "next_ic_time",
            "gct_ms",
            "flight_ms",
            "step_time_ms",
        ]
        assert list(result.columns) == expected_cols

    def test_no_contact_returns_empty(self) -> None:
        """When both force channels are all zeros (never exceeding threshold=0),
        no stance intervals are found and the output should be empty."""
        time = np.arange(0, 100, 10, dtype=np.int64)
        df = pd.DataFrame(
            {
                "Time": time,
                "Force_Foot1": np.zeros(len(time), dtype=np.int64),
                "Force_Foot2": np.zeros(len(time), dtype=np.int64),
            }
        )

        result = transform_feet_to_stride_cycles(df)

        assert result.empty

    def test_csv_factory_data_smoke_test(self) -> None:
        """Feed the same CSV content that CSVFactory.create_valid_csv_content()
        generates through the full pipeline to verify it produces a non-empty
        DataFrame — a realistic end-to-end smoke test."""
        csv_text = """Time,Force_Foot1,Force_Foot2
                      1296674,0,4095
                      1296684,0,4095
                      1296694,0,4095
                      1296704,0,4095
                      1296714,0,4095
                      1296724,0,0
                      1296734,4095,0
                      1296744,4095,0
                      1296754,4095,0
                      1296764,4095,0
                      1296774,0,0
                      1296784,0,4095
                      1296794,0,4095"""

        from io import StringIO

        df = pd.read_csv(StringIO(csv_text))
        result = transform_feet_to_stride_cycles(df)

        assert not result.empty
        assert isinstance(result, pd.DataFrame)

import pandas as pd
import pytest

from app.utils.stride_metrics import (
    calculate_all_metrics,
    calculate_contact_flight_index,
    calculate_duty_factor,
    calculate_ft_asymmetry_percent,
    calculate_ft_difference_lr,
    calculate_gct_asymmetry_percent,
    calculate_gct_difference_lr,
    calculate_mean_flight_time,
    calculate_mean_ft_asymmetry,
    calculate_mean_gct,
    calculate_mean_gct_asymmetry,
    calculate_mean_rsi,
    calculate_rsi,
    calculate_total_steps,
)

# Fixtures


@pytest.fixture
def two_stride_df() -> pd.DataFrame:
    """A two-stride DataFrame."""
    return pd.DataFrame(
        {
            "stride_num": [1, 1, 2, 2],
            "foot": ["left", "right", "left", "right"],
            "ic_time": [0, 100, 500, 600],
            "to_time": [200, 300, 700, 800],
            "next_ic_time": [500, 600, 1000, 1100],
            "gct_ms": [200, 220, 210, 180],
            "flight_ms": [300, 300, 290, 320],
            "step_time_ms": [500, 520, 500, 500],
        }
    )


@pytest.fixture
def empty_stride_df() -> pd.DataFrame:
    """An empty DataFrame."""
    return pd.DataFrame(
        columns=[
            "stride_num",
            "foot",
            "ic_time",
            "to_time",
            "next_ic_time",
            "gct_ms",
            "flight_ms",
            "step_time_ms",
        ]
    )


@pytest.fixture
def single_foot_df() -> pd.DataFrame:
    """A DataFrame with only left foot data."""
    return pd.DataFrame(
        {
            "stride_num": [1, 2],
            "foot": ["left", "left"],
            "ic_time": [0, 500],
            "to_time": [200, 700],
            "next_ic_time": [500, 1000],
            "gct_ms": [200, 210],
            "flight_ms": [300, 290],
            "step_time_ms": [500, 500],
        }
    )


# Counting Metrics


@pytest.mark.unit
class TestCalculateTotalSteps:
    """Tests for calculate_total_steps."""

    def test_counts_all_rows(self, two_stride_df: pd.DataFrame) -> None:
        """Each row represents one step, so total steps equals the row count."""
        assert calculate_total_steps(two_stride_df) == 4

    def test_empty_returns_zero(self, empty_stride_df: pd.DataFrame) -> None:
        """An empty DataFrame has zero steps."""
        assert calculate_total_steps(empty_stride_df) == 0


@pytest.mark.unit
class TestCalculateMeanGct:
    """Tests for calculate_mean_gct."""

    def test_computes_correct_mean(self, two_stride_df: pd.DataFrame) -> None:
        """Mean of [200, 220, 210, 180] should be 202.5."""
        assert calculate_mean_gct(two_stride_df) == pytest.approx(202.5)

    def test_empty_returns_zero(self, empty_stride_df: pd.DataFrame) -> None:
        """An empty DataFrame should return 0.0."""
        assert calculate_mean_gct(empty_stride_df) == 0.0

    def test_single_row(self) -> None:
        """A single-row DataFrame should return that row's gct_ms value."""
        df = pd.DataFrame({"gct_ms": [250]})
        assert calculate_mean_gct(df) == pytest.approx(250.0)


@pytest.mark.unit
class TestCalculateMeanFlightTime:
    """Tests for calculate_mean_flight_time."""

    def test_computes_correct_mean(self, two_stride_df: pd.DataFrame) -> None:
        """Mean of [300, 300, 290, 320] should be 302.5."""
        assert calculate_mean_flight_time(two_stride_df) == pytest.approx(302.5)

    def test_empty_returns_zero(self, empty_stride_df: pd.DataFrame) -> None:
        """An empty DataFrame should return 0.0."""
        assert calculate_mean_flight_time(empty_stride_df) == 0.0


# Ratio Metrics


@pytest.mark.unit
class TestCalculateRsi:
    """Tests for calculate_rsi."""

    def test_correct_rsi_values(self) -> None:
        """With flight_ms=300 and gct_ms=200, RSI should be 300/200 = 1.5."""
        df = pd.DataFrame(
            {
                "stride_num": [1, 1],
                "foot": ["left", "right"],
                "ic_time": [0, 100],
                "gct_ms": [200, 210],
                "flight_ms": [300, 315],
            }
        )
        result = calculate_rsi(df)

        assert list(result.columns) == ["stride_num", "foot", "ic_time", "rsi"]
        assert result["rsi"].iloc[0] == pytest.approx(1.5)
        assert result["rsi"].iloc[1] == pytest.approx(1.5)

    def test_empty_returns_empty_with_schema(
        self, empty_stride_df: pd.DataFrame
    ) -> None:
        """An empty input should return an empty DataFrame."""
        result = calculate_rsi(empty_stride_df)

        assert result.empty
        assert list(result.columns) == ["stride_num", "foot", "ic_time", "rsi"]

    def test_preserves_row_count(self, two_stride_df: pd.DataFrame) -> None:
        """Output should have the same number of rows as the input."""
        result = calculate_rsi(two_stride_df)
        assert len(result) == len(two_stride_df)


@pytest.mark.unit
class TestCalculateMeanRsi:
    """Tests for calculate_mean_rsi."""

    def test_correct_mean(self) -> None:
        """With flight_ms=[300, 400] and gct_ms=[200, 200], RSI values are
        1.5 and 2.0, so the mean should be 1.75."""
        df = pd.DataFrame({"gct_ms": [200, 200], "flight_ms": [300, 400]})
        assert calculate_mean_rsi(df) == pytest.approx(1.75)

    def test_empty_returns_zero(self, empty_stride_df: pd.DataFrame) -> None:
        """An empty DataFrame should return 0.0."""
        assert calculate_mean_rsi(empty_stride_df) == 0.0


@pytest.mark.unit
class TestCalculateDutyFactor:
    """Tests for calculate_duty_factor."""

    def test_correct_duty_factor_values(self) -> None:
        """With gct_ms=200 and step_time_ms=500, duty factor should be 200/500 = 0.4."""
        df = pd.DataFrame(
            {
                "stride_num": [1, 1],
                "foot": ["left", "right"],
                "ic_time": [0, 100],
                "gct_ms": [200, 300],
                "step_time_ms": [500, 600],
            }
        )
        result = calculate_duty_factor(df)

        assert list(result.columns) == ["stride_num", "foot", "ic_time", "duty_factor"]
        assert result["duty_factor"].iloc[0] == pytest.approx(0.4)
        assert result["duty_factor"].iloc[1] == pytest.approx(0.5)

    def test_empty_returns_empty_with_schema(
        self, empty_stride_df: pd.DataFrame
    ) -> None:
        """An empty input should return an empty DataFrame."""
        result = calculate_duty_factor(empty_stride_df)

        assert result.empty
        assert list(result.columns) == ["stride_num", "foot", "ic_time", "duty_factor"]


@pytest.mark.unit
class TestCalculateContactFlightIndex:
    """Tests for calculate_contact_flight_index."""

    def test_positive_flight_dominant(self) -> None:
        """When FT > GCT, the index should be positive (flight-dominant)."""
        df = pd.DataFrame(
            {
                "stride_num": [1],
                "foot": ["left"],
                "ic_time": [0],
                "gct_ms": [200],
                "flight_ms": [300],
                "step_time_ms": [500],
            }
        )
        result = calculate_contact_flight_index(df)

        assert result["contact_flight_index"].iloc[0] == pytest.approx(0.2)

    def test_negative_contact_dominant(self) -> None:
        """When GCT > FT, the index should be negative (contact-dominant)."""
        df = pd.DataFrame(
            {
                "stride_num": [1],
                "foot": ["right"],
                "ic_time": [0],
                "gct_ms": [300],
                "flight_ms": [200],
                "step_time_ms": [500],
            }
        )
        result = calculate_contact_flight_index(df)

        assert result["contact_flight_index"].iloc[0] == pytest.approx(-0.2)

    def test_empty_returns_empty_with_schema(
        self, empty_stride_df: pd.DataFrame
    ) -> None:
        """An empty input should return an empty DataFrame."""
        result = calculate_contact_flight_index(empty_stride_df)

        assert result.empty
        assert list(result.columns) == [
            "stride_num",
            "foot",
            "ic_time",
            "contact_flight_index",
        ]


# Asymmetry Metrics


@pytest.mark.unit
class TestCalculateGctAsymmetryPercent:
    """Tests for calculate_gct_asymmetry_percent."""

    def test_correct_asymmetry_value(self) -> None:
        """With gct_left=200 and gct_right=220, asymmetry is |200-220| / 210 * 100 ≈ 9.52%."""
        df = pd.DataFrame(
            {
                "stride_num": [1, 1],
                "foot": ["left", "right"],
                "ic_time": [0, 100],
                "gct_ms": [200, 220],
            }
        )
        result = calculate_gct_asymmetry_percent(df)

        assert len(result) == 1
        assert result["gct_asymmetry_percent"].iloc[0] == pytest.approx(
            9.5238, rel=1e-3
        )
        assert result["gct_left"].iloc[0] == 200
        assert result["gct_right"].iloc[0] == 220

    def test_symmetric_returns_zero(self) -> None:
        """Identical GCT for both feet should produce 0% asymmetry."""
        df = pd.DataFrame(
            {
                "stride_num": [1, 1],
                "foot": ["left", "right"],
                "ic_time": [0, 100],
                "gct_ms": [200, 200],
            }
        )
        result = calculate_gct_asymmetry_percent(df)

        assert result["gct_asymmetry_percent"].iloc[0] == pytest.approx(0.0)

    def test_output_columns(self) -> None:
        """Output should contain stride_num, ic_time, gct_asymmetry_percent, gct_left, gct_right."""
        df = pd.DataFrame(
            {
                "stride_num": [1, 1],
                "foot": ["left", "right"],
                "ic_time": [0, 100],
                "gct_ms": [200, 220],
            }
        )
        result = calculate_gct_asymmetry_percent(df)

        assert list(result.columns) == [
            "stride_num",
            "ic_time",
            "gct_asymmetry_percent",
            "gct_left",
            "gct_right",
        ]

    def test_empty_returns_empty_with_schema(
        self, empty_stride_df: pd.DataFrame
    ) -> None:
        """An empty input should return an empty DataFrame."""
        result = calculate_gct_asymmetry_percent(empty_stride_df)

        assert result.empty
        assert list(result.columns) == [
            "stride_num",
            "ic_time",
            "gct_asymmetry_percent",
            "gct_left",
            "gct_right",
        ]

    def test_single_foot_returns_empty(self, single_foot_df: pd.DataFrame) -> None:
        """No left-right pairing possible should return an empty DataFrame."""
        result = calculate_gct_asymmetry_percent(single_foot_df)
        assert result.empty


@pytest.mark.unit
class TestCalculateFtAsymmetryPercent:
    """Tests for calculate_ft_asymmetry_percent."""

    def test_correct_asymmetry_value(self) -> None:
        """With ft_left=100 and ft_right=120, asymmetry is |100-120| / 110 * 100 ≈ 18.18%."""
        df = pd.DataFrame(
            {
                "stride_num": [1, 1],
                "foot": ["left", "right"],
                "ic_time": [0, 100],
                "flight_ms": [100, 120],
            }
        )
        result = calculate_ft_asymmetry_percent(df)

        assert len(result) == 1
        assert result["ft_asymmetry_percent"].iloc[0] == pytest.approx(
            18.1818, rel=1e-3
        )

    def test_symmetric_returns_zero(self) -> None:
        """Identical flight times for both feet should produce 0% asymmetry."""
        df = pd.DataFrame(
            {
                "stride_num": [1, 1],
                "foot": ["left", "right"],
                "ic_time": [0, 100],
                "flight_ms": [300, 300],
            }
        )
        result = calculate_ft_asymmetry_percent(df)

        assert result["ft_asymmetry_percent"].iloc[0] == pytest.approx(0.0)

    def test_output_columns(self) -> None:
        """Output should contain stride_num, ic_time, ft_asymmetry_percent, ft_left, ft_right."""
        df = pd.DataFrame(
            {
                "stride_num": [1, 1],
                "foot": ["left", "right"],
                "ic_time": [0, 100],
                "flight_ms": [100, 120],
            }
        )
        result = calculate_ft_asymmetry_percent(df)

        assert list(result.columns) == [
            "stride_num",
            "ic_time",
            "ft_asymmetry_percent",
            "ft_left",
            "ft_right",
        ]

    def test_empty_returns_empty_with_schema(
        self, empty_stride_df: pd.DataFrame
    ) -> None:
        """An empty input should return an empty DataFrame."""
        result = calculate_ft_asymmetry_percent(empty_stride_df)

        assert result.empty
        assert list(result.columns) == [
            "stride_num",
            "ic_time",
            "ft_asymmetry_percent",
            "ft_left",
            "ft_right",
        ]


# Difference Metrics


@pytest.mark.unit
class TestCalculateGctDifferenceLr:
    """Tests for calculate_gct_difference_lr."""

    def test_positive_when_left_longer(self) -> None:
        """When left GCT (250) > right GCT (200), the difference should be 50."""
        df = pd.DataFrame(
            {
                "stride_num": [1, 1],
                "foot": ["left", "right"],
                "ic_time": [0, 100],
                "gct_ms": [250, 200],
            }
        )
        result = calculate_gct_difference_lr(df)

        assert result["gct_diff_lr_ms"].iloc[0] == 50

    def test_negative_when_right_longer(self) -> None:
        """When right GCT (220) > left GCT (200), the difference should be -20."""
        df = pd.DataFrame(
            {
                "stride_num": [1, 1],
                "foot": ["left", "right"],
                "ic_time": [0, 100],
                "gct_ms": [200, 220],
            }
        )
        result = calculate_gct_difference_lr(df)

        assert result["gct_diff_lr_ms"].iloc[0] == -20

    def test_zero_when_symmetric(self) -> None:
        """Identical GCT values should produce a difference of 0."""
        df = pd.DataFrame(
            {
                "stride_num": [1, 1],
                "foot": ["left", "right"],
                "ic_time": [0, 100],
                "gct_ms": [200, 200],
            }
        )
        result = calculate_gct_difference_lr(df)

        assert result["gct_diff_lr_ms"].iloc[0] == 0

    def test_output_columns(self) -> None:
        """Output should contain stride_num, ic_time, gct_diff_lr_ms, gct_left, gct_right."""
        df = pd.DataFrame(
            {
                "stride_num": [1, 1],
                "foot": ["left", "right"],
                "ic_time": [0, 100],
                "gct_ms": [200, 220],
            }
        )
        result = calculate_gct_difference_lr(df)

        assert list(result.columns) == [
            "stride_num",
            "ic_time",
            "gct_diff_lr_ms",
            "gct_left",
            "gct_right",
        ]

    def test_empty_returns_empty_with_schema(
        self, empty_stride_df: pd.DataFrame
    ) -> None:
        """An empty input should return an empty DataFrame."""
        result = calculate_gct_difference_lr(empty_stride_df)

        assert result.empty
        assert list(result.columns) == [
            "stride_num",
            "ic_time",
            "gct_diff_lr_ms",
            "gct_left",
            "gct_right",
        ]


@pytest.mark.unit
class TestCalculateFtDifferenceLr:
    """Tests for calculate_ft_difference_lr."""

    def test_positive_when_left_longer(self) -> None:
        """When left FT (120) > right FT (100), the difference should be 20."""
        df = pd.DataFrame(
            {
                "stride_num": [1, 1],
                "foot": ["left", "right"],
                "ic_time": [0, 100],
                "flight_ms": [120, 100],
            }
        )
        result = calculate_ft_difference_lr(df)

        assert result["ft_diff_lr_ms"].iloc[0] == 20

    def test_negative_when_right_longer(self) -> None:
        """When right FT (120) > left FT (100), the difference should be -20."""
        df = pd.DataFrame(
            {
                "stride_num": [1, 1],
                "foot": ["left", "right"],
                "ic_time": [0, 100],
                "flight_ms": [100, 120],
            }
        )
        result = calculate_ft_difference_lr(df)

        assert result["ft_diff_lr_ms"].iloc[0] == -20

    def test_output_columns(self) -> None:
        """Output should contain stride_num, ic_time, ft_diff_lr_ms, ft_left, ft_right."""
        df = pd.DataFrame(
            {
                "stride_num": [1, 1],
                "foot": ["left", "right"],
                "ic_time": [0, 100],
                "flight_ms": [100, 120],
            }
        )
        result = calculate_ft_difference_lr(df)

        assert list(result.columns) == [
            "stride_num",
            "ic_time",
            "ft_diff_lr_ms",
            "ft_left",
            "ft_right",
        ]

    def test_empty_returns_empty_with_schema(
        self, empty_stride_df: pd.DataFrame
    ) -> None:
        """An empty input should return an empty DataFrame."""
        result = calculate_ft_difference_lr(empty_stride_df)

        assert result.empty
        assert list(result.columns) == [
            "stride_num",
            "ic_time",
            "ft_diff_lr_ms",
            "ft_left",
            "ft_right",
        ]


# Mean Asymmetry Aggregators


@pytest.mark.unit
class TestCalculateMeanGctAsymmetry:
    """Tests for calculate_mean_gct_asymmetry."""

    def test_correct_mean(self, two_stride_df: pd.DataFrame) -> None:
        """Using the two_stride_df fixture, stride 1 asymmetry is 9.52% and stride 2
        is 15.38%, so the mean should be 12.45%."""
        result = calculate_mean_gct_asymmetry(two_stride_df)
        assert result == pytest.approx(12.4542, rel=1e-3)

    def test_empty_returns_zero(self, empty_stride_df: pd.DataFrame) -> None:
        """An empty DataFrame should return 0.0."""
        assert calculate_mean_gct_asymmetry(empty_stride_df) == 0.0

    def test_symmetric_data_returns_zero(self) -> None:
        """When left and right GCT are identical, mean asymmetry should be 0."""
        df = pd.DataFrame(
            {
                "stride_num": [1, 1],
                "foot": ["left", "right"],
                "ic_time": [0, 100],
                "gct_ms": [200, 200],
            }
        )
        assert calculate_mean_gct_asymmetry(df) == pytest.approx(0.0)


@pytest.mark.unit
class TestCalculateMeanFtAsymmetry:
    """Tests for calculate_mean_ft_asymmetry."""

    def test_correct_mean(self, two_stride_df: pd.DataFrame) -> None:
        """Using the two_stride_df fixture, stride 1 asymmetry is 0% (both 300) and
        stride 2 is 9.84% (|290-320|/305), so the mean should be 4.92%."""
        result = calculate_mean_ft_asymmetry(two_stride_df)
        assert result == pytest.approx(4.918, rel=1e-3)

    def test_empty_returns_zero(self, empty_stride_df: pd.DataFrame) -> None:
        """An empty DataFrame should return 0.0."""
        assert calculate_mean_ft_asymmetry(empty_stride_df) == 0.0


# calculate_all_metrics


@pytest.mark.unit
class TestCalculateAllMetrics:
    """Tests for calculate_all_metrics."""

    def test_returns_expected_structure(self, two_stride_df: pd.DataFrame) -> None:
        """The returned dict should contain 'summary_metrics' and 'time_series_metrics'
        keys, each populated with the expected sub-keys."""
        result = calculate_all_metrics(two_stride_df)

        assert "summary_metrics" in result
        assert "time_series_metrics" in result

        summary = result["summary_metrics"]
        assert "total_steps" in summary
        assert "mean_gct_ms" in summary
        assert "mean_flight_time_ms" in summary
        assert "mean_rsi" in summary
        assert "mean_gct_asymmetry_percent" in summary
        assert "mean_ft_asymmetry_percent" in summary

        ts = result["time_series_metrics"]
        assert "rsi" in ts
        assert "duty_factor" in ts
        assert "contact_flight_index" in ts
        assert "gct_asymmetry_percent" in ts
        assert "ft_asymmetry_percent" in ts
        assert "gct_difference_lr" in ts
        assert "ft_difference_lr" in ts

    def test_summary_values_are_correct_types(
        self, two_stride_df: pd.DataFrame
    ) -> None:
        """All summary metrics should be numeric (int or float)."""
        result = calculate_all_metrics(two_stride_df)
        summary = result["summary_metrics"]

        assert isinstance(summary["total_steps"], int)
        assert isinstance(summary["mean_gct_ms"], float)
        assert isinstance(summary["mean_flight_time_ms"], float)
        assert isinstance(summary["mean_rsi"], float)

    def test_time_series_values_are_dataframes(
        self, two_stride_df: pd.DataFrame
    ) -> None:
        """All time series metrics should be pandas DataFrames."""
        result = calculate_all_metrics(two_stride_df)
        ts = result["time_series_metrics"]

        for key, value in ts.items():
            assert isinstance(value, pd.DataFrame), f"{key} should be a DataFrame"

    def test_empty_input_does_not_error(self, empty_stride_df: pd.DataFrame) -> None:
        """An empty DataFrame should produce the full structure without raising."""
        result = calculate_all_metrics(empty_stride_df)

        assert result["summary_metrics"]["total_steps"] == 0
        assert result["summary_metrics"]["mean_gct_ms"] == 0.0

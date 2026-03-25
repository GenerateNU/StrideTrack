import pytest

from app.schemas.run_schemas import RunResponse, SprintDriftData
from app.utils.sprint_metrics import _drift_window, calculate_drift

# _drift_window


@pytest.mark.unit
class TestDriftWindow:
    """Tests for _drift_window."""

    def test_ten_percent_of_total(self) -> None:
        """For 50 strides, the window should be round(50 * 0.1) = 5."""
        assert _drift_window(50) == 5

    def test_clamps_to_minimum_of_three(self) -> None:
        """For very small datasets (e.g. 10 strides), round(10 * 0.1) = 1, but the
        minimum clamp of 3 should override."""
        assert _drift_window(10) == 3

    def test_clamps_to_maximum_of_ten(self) -> None:
        """For large datasets (e.g. 200 strides), round(200 * 0.1) = 20, but the
        maximum clamp of 10 should override."""
        assert _drift_window(200) == 10

    def test_exact_lower_boundary(self) -> None:
        """For 30 strides, round(30 * 0.1) = 3, which equals the minimum, should
        return exactly 3."""
        assert _drift_window(30) == 3

    def test_exact_upper_boundary(self) -> None:
        """For 100 strides, round(100 * 0.1) = 10, which equals the maximum, should
        return exactly 10."""
        assert _drift_window(100) == 10


# calculate_drift


@pytest.mark.unit
class TestCalculateDrift:
    """Tests for calculate_drift."""

    def test_no_drift_with_constant_data(self) -> None:
        """When every stride has identical GCT and FT, both drift values should be 0%."""
        data = [
            RunResponse(
                stride_num=i,
                foot="left",
                ic_time=0,
                gct_ms=200,
                flight_ms=300,
                step_time_ms=500,
            )
            for i in range(1, 21)
        ]

        result = calculate_drift(data)

        assert result.gct_drift_pct == 0.0
        assert result.ft_drift_pct == 0.0

    def test_positive_gct_drift_indicates_fatigue(self) -> None:
        """When terminal GCT is higher than the best (shortest) GCT values, gct_drift_pct
        should be positive, indicating the athlete is spending more time on the ground."""
        data = [
            RunResponse(
                stride_num=i,
                foot="left",
                ic_time=0,
                gct_ms=180,
                flight_ms=300,
                step_time_ms=480,
            )
            for i in range(1, 11)
        ] + [
            RunResponse(
                stride_num=i,
                foot="left",
                ic_time=0,
                gct_ms=250,
                flight_ms=300,
                step_time_ms=550,
            )
            for i in range(11, 21)
        ]

        result = calculate_drift(data)

        assert result.gct_drift_pct > 0.0

    def test_negative_ft_drift_indicates_power_loss(self) -> None:
        """When terminal FT is lower than the best (longest) FT values, ft_drift_pct
        should be negative, indicating the athlete is losing push-off power."""
        data = [
            RunResponse(
                stride_num=i,
                foot="left",
                ic_time=0,
                gct_ms=200,
                flight_ms=350,
                step_time_ms=550,
            )
            for i in range(1, 11)
        ] + [
            RunResponse(
                stride_num=i,
                foot="left",
                ic_time=0,
                gct_ms=200,
                flight_ms=250,
                step_time_ms=450,
            )
            for i in range(11, 21)
        ]

        result = calculate_drift(data)

        assert result.ft_drift_pct < 0.0

    def test_output_is_sprint_drift_data(self) -> None:
        """The returned value should be a SprintDriftData instance with both fields."""
        data = [
            RunResponse(
                stride_num=i,
                foot="left",
                ic_time=0,
                gct_ms=200,
                flight_ms=300,
                step_time_ms=500,
            )
            for i in range(1, 21)
        ]

        result = calculate_drift(data)

        assert isinstance(result, SprintDriftData)
        assert hasattr(result, "gct_drift_pct")
        assert hasattr(result, "ft_drift_pct")

    def test_known_drift_values(self) -> None:
        """Where the first 10 strides have gct=180 and the last 10 have gct=216,
        the N=3 shortest GCTs are all 180 (baseline=180) and the terminal window
        (last 3) averages 216. Drift = (216-180)/180*100 = 20%."""
        data = [
            RunResponse(
                stride_num=i,
                foot="left",
                ic_time=0,
                gct_ms=180,
                flight_ms=300,
                step_time_ms=480,
            )
            for i in range(1, 11)
        ] + [
            RunResponse(
                stride_num=i,
                foot="left",
                ic_time=0,
                gct_ms=216,
                flight_ms=240,
                step_time_ms=456,
            )
            for i in range(11, 21)
        ]

        result = calculate_drift(data)

        assert result.gct_drift_pct == pytest.approx(20.0)
        assert result.ft_drift_pct == pytest.approx(-20.0)

    def test_minimum_viable_dataset(self) -> None:
        """With only 3 data points (the minimum window size), the function should
        still compute without error."""
        data = [
            RunResponse(
                stride_num=1,
                foot="left",
                ic_time=0,
                gct_ms=180,
                flight_ms=300,
                step_time_ms=480,
            ),
            RunResponse(
                stride_num=2,
                foot="left",
                ic_time=0,
                gct_ms=190,
                flight_ms=290,
                step_time_ms=480,
            ),
            RunResponse(
                stride_num=3,
                foot="left",
                ic_time=0,
                gct_ms=200,
                flight_ms=280,
                step_time_ms=480,
            ),
        ]

        result = calculate_drift(data)

        assert isinstance(result.gct_drift_pct, float)
        assert isinstance(result.ft_drift_pct, float)

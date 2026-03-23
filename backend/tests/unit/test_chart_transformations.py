import pytest

from app.utils.chart_transformations import (
    transform_data_for_lr_overlay,
    transform_data_for_stacked_bar,
    transform_data_for_step_frequency,
)

# Fixtures


@pytest.fixture
def sample_run_data() -> list[dict]:
    """Two complete strides with known values."""
    return [
        {
            "stride_num": 1,
            "foot": "left",
            "gct_ms": 200,
            "flight_ms": 300,
            "step_time_ms": 500,
        },
        {
            "stride_num": 1,
            "foot": "right",
            "gct_ms": 220,
            "flight_ms": 280,
            "step_time_ms": 500,
        },
        {
            "stride_num": 2,
            "foot": "left",
            "gct_ms": 210,
            "flight_ms": 290,
            "step_time_ms": 500,
        },
        {
            "stride_num": 2,
            "foot": "right",
            "gct_ms": 190,
            "flight_ms": 310,
            "step_time_ms": 500,
        },
    ]


# transform_data_for_lr_overlay


@pytest.mark.unit
class TestTransformDataForLrOverlay:
    """Tests for transform_data_for_lr_overlay"""

    def test_groups_left_and_right_by_stride(self, sample_run_data: list[dict]) -> None:
        """Each stride should become one dict with both left and right values nested
        under the stride_num key."""
        result = transform_data_for_lr_overlay(sample_run_data, metric="gct_ms")

        assert len(result) == 2
        assert result[0]["stride_num"] == 1
        assert result[0]["left"] == 200
        assert result[0]["right"] == 220

    def test_works_with_flight_ms_metric(self, sample_run_data: list[dict]) -> None:
        """Passing metric='flight_ms' should pull flight_ms values instead of gct_ms."""
        result = transform_data_for_lr_overlay(sample_run_data, metric="flight_ms")

        assert result[0]["left"] == 300
        assert result[0]["right"] == 280

    def test_empty_input_returns_empty(self) -> None:
        """An empty input list should return an empty output list."""
        result = transform_data_for_lr_overlay([], metric="gct_ms")
        assert result == []

    def test_single_foot_stride(self) -> None:
        """A stride with only one foot should still appear, with only that foot's value."""
        data = [
            {
                "stride_num": 1,
                "foot": "left",
                "gct_ms": 200,
                "flight_ms": 300,
                "step_time_ms": 500,
            },
        ]
        result = transform_data_for_lr_overlay(data, metric="gct_ms")

        assert len(result) == 1
        assert result[0]["left"] == 200
        assert "right" not in result[0]


# transform_data_for_stacked_bar


@pytest.mark.unit
class TestTransformDataForStackedBar:
    """Tests for transform_data_for_stacked_bar."""

    def test_output_has_correct_keys(self, sample_run_data: list[dict]) -> None:
        """Each output dict should have stride_num, foot, label, gct_ms, and flight_ms."""
        result = transform_data_for_stacked_bar(sample_run_data)

        for row in result:
            assert "stride_num" in row
            assert "foot" in row
            assert "label" in row
            assert "gct_ms" in row
            assert "flight_ms" in row

    def test_label_format_left(self, sample_run_data: list[dict]) -> None:
        """Left foot steps should get a label like '1L'."""
        result = transform_data_for_stacked_bar(sample_run_data)
        left_rows = [r for r in result if r["foot"] == "left"]

        assert left_rows[0]["label"] == "1L"

    def test_label_format_right(self, sample_run_data: list[dict]) -> None:
        """Right foot steps should get a label like '1R'."""
        result = transform_data_for_stacked_bar(sample_run_data)
        right_rows = [r for r in result if r["foot"] == "right"]

        assert right_rows[0]["label"] == "1R"

    def test_preserves_row_count(self, sample_run_data: list[dict]) -> None:
        """Output should have the same number of rows as the input (one per step)."""
        result = transform_data_for_stacked_bar(sample_run_data)
        assert len(result) == len(sample_run_data)

    def test_sorted_by_stride_num(self) -> None:
        """Output should be sorted by stride_num even if input is unordered."""
        data = [
            {
                "stride_num": 2,
                "foot": "left",
                "gct_ms": 210,
                "flight_ms": 290,
                "step_time_ms": 500,
            },
            {
                "stride_num": 1,
                "foot": "right",
                "gct_ms": 220,
                "flight_ms": 280,
                "step_time_ms": 500,
            },
        ]
        result = transform_data_for_stacked_bar(data)

        assert result[0]["stride_num"] == 1
        assert result[1]["stride_num"] == 2

    def test_empty_input_returns_empty(self) -> None:
        """An empty input list should return an empty output list."""
        result = transform_data_for_stacked_bar([])
        assert result == []


# transform_data_for_step_frequency


@pytest.mark.unit
class TestTransformDataForStepFrequency:
    """Tests for transform_data_for_step_frequency."""

    def test_correct_frequency_calculation(self, sample_run_data: list[dict]) -> None:
        """With step_time_ms=500, step_frequency_hz should be 1000/500 = 2.0 Hz."""
        result = transform_data_for_step_frequency(sample_run_data)

        for row in result:
            assert row["step_frequency_hz"] == 2.0

    def test_frequency_rounded_to_three_decimals(self) -> None:
        """The frequency value should be rounded to 3 decimal places."""
        data = [
            {
                "stride_num": 1,
                "foot": "left",
                "gct_ms": 200,
                "flight_ms": 300,
                "step_time_ms": 333,
            },
        ]
        result = transform_data_for_step_frequency(data)

        assert result[0]["step_frequency_hz"] == 3.003

    def test_output_has_correct_keys(self, sample_run_data: list[dict]) -> None:
        """Each output dict should have stride_num, foot, label, and step_frequency_hz."""
        result = transform_data_for_step_frequency(sample_run_data)

        for row in result:
            assert "stride_num" in row
            assert "foot" in row
            assert "label" in row
            assert "step_frequency_hz" in row

    def test_label_format(self, sample_run_data: list[dict]) -> None:
        """Labels should follow the '{stride_num}L' or '{stride_num}R' format."""
        result = transform_data_for_step_frequency(sample_run_data)

        labels = [r["label"] for r in result]
        assert "1L" in labels
        assert "1R" in labels

    def test_sorted_by_stride_num_then_foot(self) -> None:
        """Output should be sorted by (stride_num, foot) even if input is unordered."""
        data = [
            {
                "stride_num": 2,
                "foot": "right",
                "gct_ms": 190,
                "flight_ms": 310,
                "step_time_ms": 500,
            },
            {
                "stride_num": 1,
                "foot": "right",
                "gct_ms": 220,
                "flight_ms": 280,
                "step_time_ms": 500,
            },
            {
                "stride_num": 1,
                "foot": "left",
                "gct_ms": 200,
                "flight_ms": 300,
                "step_time_ms": 500,
            },
        ]
        result = transform_data_for_step_frequency(data)

        assert result[0]["stride_num"] == 1
        assert result[0]["foot"] == "left"
        assert result[1]["stride_num"] == 1
        assert result[1]["foot"] == "right"
        assert result[2]["stride_num"] == 2

    def test_empty_input_returns_empty(self) -> None:
        """An empty input list should return an empty output list."""
        result = transform_data_for_step_frequency([])
        assert result == []

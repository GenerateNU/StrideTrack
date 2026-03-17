"""
Example unit tests demonstrating the unit testing pattern for utility functions.

This file is the reference template. Copy it when adding tests for a new util module:
  1. Import the functions you want to test
  2. Group tests by function in a class named Test<FunctionName>
  3. Mark each class with @pytest.mark.unit
  4. Cover: happy path, edge cases, and error cases
  5. No fixtures, no DB, no network — pure Python only
"""

import pytest

from app.utils.example_utils import clamp, normalize, percent_change


@pytest.mark.unit
class TestClamp:
    def test_value_within_range_unchanged(self) -> None:
        assert clamp(5.0, 0.0, 10.0) == 5.0

    def test_value_below_min_returns_min(self) -> None:
        assert clamp(-3.0, 0.0, 10.0) == 0.0

    def test_value_above_max_returns_max(self) -> None:
        assert clamp(15.0, 0.0, 10.0) == 10.0

    def test_value_at_boundary_min(self) -> None:
        assert clamp(0.0, 0.0, 10.0) == 0.0

    def test_value_at_boundary_max(self) -> None:
        assert clamp(10.0, 0.0, 10.0) == 10.0


@pytest.mark.unit
class TestPercentChange:
    def test_positive_increase(self) -> None:
        assert percent_change(100.0, 110.0) == pytest.approx(10.0)

    def test_negative_decrease(self) -> None:
        assert percent_change(200.0, 150.0) == pytest.approx(-25.0)

    def test_no_change_returns_zero(self) -> None:
        assert percent_change(50.0, 50.0) == pytest.approx(0.0)

    def test_zero_old_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="zero"):
            percent_change(0.0, 100.0)


@pytest.mark.unit
class TestNormalize:
    def test_docstring_example(self) -> None:
        result = normalize([0.0, 50.0, 100.0])
        assert result == pytest.approx([0.0, 0.5, 1.0])

    def test_all_same_values_returns_unchanged(self) -> None:
        result = normalize([5.0, 5.0, 5.0])
        assert result == [5.0, 5.0, 5.0]

    def test_empty_list_returns_empty(self) -> None:
        assert normalize([]) == []

    def test_single_value(self) -> None:
        result = normalize([42.0])
        assert result == [42.0]

    def test_min_is_zero_max_is_one(self) -> None:
        result = normalize([10.0, 20.0, 30.0])
        assert result[0] == pytest.approx(0.0)
        assert result[-1] == pytest.approx(1.0)

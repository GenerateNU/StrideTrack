from io import BytesIO
from pathlib import Path
from uuid import uuid4

MOCK_DATA_DIR = Path(__file__).parent.parent / "test_data"


class CSVFactory:
    """Factory for creating CSV test data and files.

    CSV content is read from pre-generated files in tests/test_data/.
    """

    # ── CSV content from fixture files ──

    @staticmethod
    def create_sprint_csv_content() -> str:
        """Read sprint 100m CSV content from fixture file."""
        return (MOCK_DATA_DIR / "sprint_100m.csv").read_text()

    @staticmethod
    def create_hurdle_110m_csv_content() -> str:
        """Read 110m hurdle CSV content from fixture file."""
        return (MOCK_DATA_DIR / "hurdle_110m.csv").read_text()

    @staticmethod
    def create_hurdle_400m_csv_content() -> str:
        """Read 400m hurdle CSV content from fixture file."""
        return (MOCK_DATA_DIR / "hurdle_400m.csv").read_text()

    # ── Invalid CSVs ──

    @staticmethod
    def create_invalid_csv_missing_columns() -> str:
        """Creates CSV with missing required columns."""
        return """Time,Force_Foot1
1296674,0
1296684,4095"""

    @staticmethod
    def create_invalid_csv_bad_data() -> str:
        """Creates CSV with invalid data types."""
        return """Time,Force_Foot1,Force_Foot2
not_a_number,0,4095
1296684,invalid,4095"""

    # ── File helpers ──

    @staticmethod
    def create_csv_file(
        content: str | None = None, filename: str = "test_run.csv"
    ) -> tuple[str, BytesIO, str]:
        """
        Creates a file-like object for upload.

        Args:
            content: CSV content string. If None, uses create_sprint_csv_content()
            filename: Name of the file

        Returns:
            Tuple of (filename, file_content, content_type)
        """
        if content is None:
            content = CSVFactory.create_sprint_csv_content()

        return (filename, BytesIO(content.encode("utf-8")), "text/csv")

    @staticmethod
    def create_form_data(
        athlete_id: str | None = None,
        event_type: str = "sprint_100m",
        name: str | None = "Test Run",
    ) -> dict:
        """
        Creates form data for CSV upload.

        Args:
            athlete_id: UUID of athlete. If None, generates a random UUID.
                        NOTE: the athlete must exist in the DB for the upload to succeed.
            event_type: Type of event from event_type_enum
            name: Optional name for the run

        Returns:
            Dictionary of form fields
        """
        data: dict = {
            "athlete_id": athlete_id or str(uuid4()),
            "event_type": event_type,
        }
        if name is not None:
            data["name"] = name
        return data

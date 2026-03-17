"""Factory for creating test CSV data."""

from io import BytesIO
from uuid import uuid4


class CSVFactory:
    """Factory for creating CSV test data and files. Always generates unique UUIDs."""

    @staticmethod
    def create_valid_csv_content() -> str:
        """Creates valid CSV content with stride data."""
        return """Time,Force_Foot1,Force_Foot2
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

    @staticmethod
    def create_minimal_csv_content() -> str:
        """Creates minimal valid CSV with just two rows."""
        return """Time,Force_Foot1,Force_Foot2
1296674,0,4095
1296684,4095,0"""

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

    @staticmethod
    def create_csv_file(
        content: str | None = None, filename: str = "test_run.csv"
    ) -> tuple[str, BytesIO, str]:
        """
        Creates a file-like object for upload.

        Args:
            content: CSV content string. If None, uses create_valid_csv_content()
            filename: Name of the file

        Returns:
            Tuple of (filename, file_content, content_type)
        """
        if content is None:
            content = CSVFactory.create_valid_csv_content()

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

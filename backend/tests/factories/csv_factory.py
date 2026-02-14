"""Factory for creating test CSV data."""

from io import BytesIO


class CSVFactory:
    """Factory for creating CSV test data and files."""

    @staticmethod
    def create_valid_csv_content() -> str:
        """Creates valid CSV content with stride data."""
        return """Time,Force_Foot1,Force_Foot2
left,100,150,200
right,200,250,300
left,300,350,400
right,400,450,500"""

    @staticmethod
    def create_minimal_csv_content() -> str:
        """Creates minimal valid CSV with just two rows."""
        return """Time,Force_Foot1,Force_Foot2
left,100,150,200
right,200,250,300"""

    @staticmethod
    def create_invalid_csv_missing_columns() -> str:
        """Creates CSV with missing required columns."""
        return """foot,ic_time
left,100
right,200"""

    @staticmethod
    def create_invalid_csv_bad_data() -> str:
        """Creates CSV with invalid data types."""
        return """Time,Force_Foot1,Force_Foot2
left,not_a_number,150,200
right,200,invalid,300"""

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
        athlete_id: str = "00000000-0000-0000-0000-000000000001",
        event_type: str = "sprint_100m",
        name: str | None = "Test Run",
    ) -> dict:
        """
        Creates form data for CSV upload.

        Args:
            athlete_id: UUID of athlete
            event_type: Type of event from event_type_enum
            name: Optional name for the run

        Returns:
            Dictionary of form fields
        """
        data = {
            "athlete_id": athlete_id,
            "event_type": event_type,
        }
        if name is not None:
            data["name"] = name
        return data

"""Tests for CSV upload endpoint."""

from io import BytesIO  # ← ADD THIS

from fastapi.testclient import TestClient

from tests.factories.csv_factory import CSVFactory


class TestUploadCSV:
    """Tests for POST /api/csv/upload-run"""

    def test_upload_with_all_fields(self, test_client: TestClient) -> None:
        """Uploads CSV with all form fields provided."""
        csv_file = CSVFactory.create_csv_file()
        form_data = CSVFactory.create_form_data(
            athlete_id="00000000-0000-0000-0000-000000000003",
            event_type="sprint_100m",
            name="Morning Sprint",
        )

        response = test_client.post(
            "/api/csv/upload-run", files={"file": csv_file}, data=form_data
        )

        assert response.status_code == 201
        data = response.json()
        assert "message" in data
        assert "successfully" in data["message"].lower()

    def test_upload_minimal_fields(self, test_client: TestClient) -> None:
        """Uploads CSV with only required form fields."""
        csv_file = CSVFactory.create_csv_file()
        form_data = CSVFactory.create_form_data(name=None)

        response = test_client.post(
            "/api/csv/upload-run", files={"file": csv_file}, data=form_data
        )

        assert response.status_code == 201
        assert "successfully" in response.json()["message"].lower()

    def test_upload_minimal_csv_content(self, test_client: TestClient) -> None:
        """Uploads CSV with minimal valid content."""
        csv_content = CSVFactory.create_minimal_csv_content()
        csv_file = CSVFactory.create_csv_file(content=csv_content)
        form_data = CSVFactory.create_form_data()

        response = test_client.post(
            "/api/csv/upload-run", files={"file": csv_file}, data=form_data
        )

        assert response.status_code == 201

    def test_upload_missing_file(self, test_client: TestClient) -> None:
        """Returns 422 when file is missing."""
        form_data = CSVFactory.create_form_data()

        response = test_client.post("/api/csv/upload-run", data=form_data)

        assert response.status_code == 422

    def test_upload_missing_athlete_id(self, test_client: TestClient) -> None:
        """Returns 422 when athlete_id is missing."""
        csv_file = CSVFactory.create_csv_file()

        response = test_client.post(
            "/api/csv/upload-run",
            files={"file": csv_file},
            data={"event_type": "sprint_100m"},
        )

        assert response.status_code == 422

    def test_upload_missing_event_type(self, test_client: TestClient) -> None:
        """Returns 422 when event_type is missing."""
        csv_file = CSVFactory.create_csv_file()

        response = test_client.post(
            "/api/csv/upload-run",
            files={"file": csv_file},
            data={"athlete_id": "00000000-0000-0000-0000-000000000003"},
        )

        assert response.status_code == 422

    def test_upload_invalid_file_type(self, test_client: TestClient) -> None:
        """Returns 400 when file is not a CSV."""
        txt_file = ("test.txt", BytesIO(b"not a csv"), "text/plain")
        form_data = CSVFactory.create_form_data()

        response = test_client.post(
            "/api/csv/upload-run", files={"file": txt_file}, data=form_data
        )

        assert response.status_code == 400
        assert "csv" in response.json()["detail"].lower()

    def test_upload_invalid_athlete_id_format(self, test_client: TestClient) -> None:
        """Returns 422 when athlete_id is not a valid UUID."""
        csv_file = CSVFactory.create_csv_file()
        form_data = CSVFactory.create_form_data(athlete_id="not-a-uuid")

        response = test_client.post(
            "/api/csv/upload-run", files={"file": csv_file}, data=form_data
        )

        # Depending on your validation, this might be 422 or 400
        assert response.status_code in [400, 422]

    def test_upload_invalid_event_type(self, test_client: TestClient) -> None:
        """Returns 422 when event_type is not valid enum value."""
        csv_file = CSVFactory.create_csv_file()
        form_data = CSVFactory.create_form_data(event_type="invalid_event")

        response = test_client.post(
            "/csv/upload-run", files={"file": csv_file}, data=form_data
        )

        # This should fail at database level due to enum constraint
        assert response.status_code in [400, 422, 500]

    def test_upload_csv_missing_required_columns(self, test_client: TestClient) -> None:
        """Returns 400 or 500 when CSV is missing required columns."""
        csv_content = CSVFactory.create_invalid_csv_missing_columns()
        csv_file = CSVFactory.create_csv_file(content=csv_content)
        form_data = CSVFactory.create_form_data()

        response = test_client.post(
            "/api/csv/upload-run", files={"file": csv_file}, data=form_data
        )

        assert response.status_code in [400, 500]

    def test_upload_csv_invalid_data_types(self, test_client: TestClient) -> None:
        """Returns 400 or 500 when CSV contains invalid data types."""
        csv_content = CSVFactory.create_invalid_csv_bad_data()
        csv_file = CSVFactory.create_csv_file(content=csv_content)
        form_data = CSVFactory.create_form_data()

        response = test_client.post(
            "/csv/upload-run", files={"file": csv_file}, data=form_data
        )

        assert response.status_code in [400, 500]

    def test_upload_empty_csv(self, test_client: TestClient) -> None:
        """Returns 400 when CSV file is empty."""
        csv_file = CSVFactory.create_csv_file(content="")
        form_data = CSVFactory.create_form_data()

        response = test_client.post(
            "/api/csv/upload-run", files={"file": csv_file}, data=form_data
        )

        assert response.status_code in [400, 500]

    def test_upload_nonexistent_athlete(self, test_client: TestClient) -> None:
        """Returns 500 when athlete_id doesn't exist in database."""
        csv_file = CSVFactory.create_csv_file()
        form_data = CSVFactory.create_form_data(
            athlete_id="99999999-9999-9999-9999-999999999999"
        )

        response = test_client.post(
            "/api/csv/upload-run", files={"file": csv_file}, data=form_data
        )

        # Should fail due to foreign key constraint
        assert response.status_code == 500

import logging

import pandas as pd
from supabase._async.client import AsyncClient

logger = logging.getLogger(__name__)


class CSVRepository:
    def __init__(self, supabase: AsyncClient) -> None:
        self.supabase = supabase
        self.metrics_table = "run_metrics"
        self.run_table = "run"

    async def create_record(
        self,
        athlete_id: str,
        event_type: str,
        name: str | None = None,
        elapsed_ms: int | None = None,
    ) -> str:
        """Create a new record in the run table and return the run_id."""
        run_data: dict[str, str | int | None] = {
            "athlete_id": athlete_id,
            "event_type": event_type,
            "name": name,
        }
        if elapsed_ms is not None:
            run_data["elapsed_ms"] = elapsed_ms
        response = await self.supabase.table(self.run_table).insert(run_data).execute()
        run_id = response.data[0]["run_id"]
        logger.info(f"Repository: Created new run record with run_id: {run_id}")
        return run_id

    async def insert_transformed_stride_rows(
        self,
        df: pd.DataFrame,
    ) -> int:
        """
        Inserts transformed data into stride_data table
        """
        if df.empty:
            logger.info("Repository: No transformed rows to insert")
            return 0

        df["run_id"] = df["run_id"].astype(str)
        data = df.to_dict(orient="records")
        logger.info(f"Repository: Inserting {len(data)} transformed rows")
        response = await self.supabase.table(self.metrics_table).insert(data).execute()

        rows_inserted = len(response.data)
        logger.info(f"Repository: Successfully inserted {rows_inserted} rows")

        return rows_inserted

    async def insert_complete_run(
        self,
        df: pd.DataFrame,
        athlete_id: str,
        event_type: str,
        name: str | None = None,
        elapsed_ms: int | None = None,
    ) -> dict[str, str | int]:
        """Insert a complete run with all stride data and return the run_id and row count."""
        run_id = await self.create_record(
            athlete_id, event_type, name, elapsed_ms=elapsed_ms
        )
        df["run_id"] = run_id
        rows_inserted = await self.insert_transformed_stride_rows(df)

        return {"run_id": run_id, "rows_inserted": rows_inserted}

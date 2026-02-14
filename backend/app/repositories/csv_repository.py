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
            name: str = None
    ) -> str:
        """
        Creates a new record in the run table and returns the run_id
        """
        run_data = {
            "athlete_id": athlete_id,
            "event_type": event_type,
            "name": name
        }
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
        logger.info(f"Repository: Inserted {len(df)} transformed rows")

        df["run_id"] = df["run_id"].astype(str)
        data = df.to_dict(orient="records")
        response = await self.supabase.table(self.metrics_table).insert(data).execute()

        rows_inserted = len(response.data)
        logger.info(f"Repository: Successfully inserted {rows_inserted} rows")

        return rows_inserted

    async def insert_complete_run(
        self,
        df: pd.DataFrame,
        athlete_id: str,
        event_type: str,
        name: str = None,
    ) -> dict:
        """
        Inserts a complete run with all stride data and returns the run_id and number of rows inserted
        """
        run_id = await self.create_record(athlete_id, event_type, name)
        df["run_id"] = run_id
        rows_inserted = await self.insert_transformed_stride_rows(df)

        return {"run_id": run_id, "rows_inserted": rows_inserted}

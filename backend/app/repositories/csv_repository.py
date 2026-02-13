import logging

import pandas as pd
from supabase._async.client import AsyncClient

logger = logging.getLogger(__name__)


class CSVRepository:
    def __init__(self, supabase: AsyncClient) -> None:
        self.supabase = supabase

    async def insert_transformed_stride_rows(
        self, df: pd.DataFrame, athlete_id: str, event_type: str, run_name: str
    ) -> dict:
        """
        Creates a RUN record and inserts all associated stride metrics into RUN_METRICS.

        This function performs a database insertion:
        1. Creates a parent RUN record linking the run to an athlete and event type
        2. Inserts all stride-by-stride metrics as child RUN_METRICS records
        """

        run_data = {"athlete_id": athlete_id, "event_type": event_type}

        if run_name:
            run_data["name"] = run_name

        run_response = await self.supabase.table("RUN").insert(run_data).execute()
        run_record = run_response.data[0]
        run_id = run_record["run_id"]

        metrics_df = df.copy()
        metrics_df["run_id"] = run_id

        metrics_data = metrics_df.to_dict("records")
        await self.supabase.table("RUN_METRICS").insert(metrics_data).execute()

        return run_record

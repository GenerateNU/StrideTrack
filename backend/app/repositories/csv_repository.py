import logging

import pandas as pd
from supabase._async.client import AsyncClient

logger = logging.getLogger(__name__)


class CSVRepository:
    def _init_(self, supabase: AsyncClient) -> None:
        self.supabse = supabase
        self.table = "stride_data"

    async def insert_transformed_stride_rows(
        self,
        df: pd.DataFrame,
    ) -> int:
        """
        Inserts transformed data into stride_data table
        """
        logger.info(f"Repository: Inserted {len(df)} transformed rows")

        data = df.to_dict("response")
        response = await self.supabase.table(self.table).insert(data)

        rows_inserted = len(response.data)
        logger.info(f"Repository: Successfully inserted {rows_inserted} rows")

        return rows_inserted

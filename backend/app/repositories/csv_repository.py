import logging
import pandas as pd

logger = logging.getLogger(__name__)


class CSVRepository:
    async def insert_transformed_stride_rows(
        self,
        df: pd.DataFrame,
    ) -> int:
        """
        No-op.
        """
        logger.info(f"Repository (NO-OP): Discarding {len(df)} transformed rows")
        
        return int(len(df))

"testing model option with tabula"

import tabula
import pandas as pd
import requests
from typing import Optional, Tuple


class W100H_DEMO:
    """
    demoing with one page of one pdf from athletefirst.org
        -extracting, cleaning, and exporting data to csv
    """

    def __init__(self) -> None:
        pass

    def data(self, path: str) -> Optional[pd.DataFrame]:
        # default is 1 page for read_pdf!
        table_data = tabula.read_pdf(
            path,
            pages=1,
            multiple_tables=True,
            pandas_options={"header": None},
            force_subprocess=True,
            encoding="cp1252",
        )
        if not table_data:
            return None
        return pd.concat(table_data, ignore_index=True)

    def clean(self, df: pd.DataFrame, m: float) -> Tuple[pd.DataFrame, pd.DataFrame]:
        df = df.copy()
        df = df.dropna(how="all").drop_duplicates()
        cols = df.select_dtypes(include="number").columns
        valid = pd.Series(True, index=df.index)
        for col in cols:
            Q1, Q3 = df[col].quantile([0.25, 0.75])
            IQR = Q3 - Q1
            lower = Q1 - m * IQR
            upper = Q3 + m * IQR
            valid &= df[col].between(lower, upper) | df[col].isna()
        clean = df[valid].reset_index(drop=True)
        outliers = df[~valid].reset_index(drop=True)
        return clean, outliers

    def csv(self, df: pd.DataFrame, path: str) -> None:
        df.to_csv(path, index=False)

    def download(self, url: str, path: str) -> str:
        re = requests.get(url)
        with open(path, "wb") as pdf:
            pdf.write(re.content)
        return path


if __name__ == "__main__":
    W100H_DEMO_TEST = W100H_DEMO()
    url = "https://www.athletefirst.org/wp-content/uploads/2025/10/20251010-Womens-100m-Hurdles-meeting.pdf"
    path = W100H_DEMO_TEST.download(url, "W100H.pdf")
    pdf = W100H_DEMO_TEST.data(path)
    if pdf is not None:
        clean, outliers = W100H_DEMO_TEST.clean(pdf, m=1.5)
        W100H_DEMO_TEST.csv(clean, "W100H_DEMO_PG1_CLEAN.csv")
        W100H_DEMO_TEST.csv(outliers, "W100H_DEMO_PG1_OUTLIERS.csv")
    print("Cleaned and exported PDF data to csvs")

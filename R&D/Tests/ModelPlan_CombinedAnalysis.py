import re
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import numpy as np
import pandas as pd
import pdfplumber
import requests
import tabula

class W100H_DEMO:
    def __init__(self) -> None:
        pass

    def download_pdf(self, url: str, save_path: Path) -> bool:
        """Downloads PDF from URL"""
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()

            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(response.content)

            return True
        except Exception as e:
            print(f"Error: {e}")
            return False

    def parse_athlete_data(self, lines, start_idx, current_wind, current_event): #type: ignore
        """
        Parse athlete data from 3 consecutive lines
        Returns dict with athlete info and race data
        """
        try:
            # Line 1- Name and hurdle times
            name_line = lines[start_idx]

            # Extract athlete name and country - handles malformed years and Unicode names
            name_match = re.match(
                r"^([^,]+),\s+([^\(]+)\s+\(([A-Z]{3})\)\s+\(([^\)]+)\)", name_line
            )
            if not name_match:
                return None

            last_name = name_match.group(1).strip()
            first_name = name_match.group(2).strip()
            country = name_match.group(3)
            year_text = name_match.group(4)  # Could be "1995" or "199t5im" or "2t0im00e"

            # Extract all digits from year text and take first 4
            digits = "".join(c for c in year_text if c.isdigit())
            if len(digits) < 4:
                return None
            birth_year = digits[:4]

            athlete_name = f"{first_name} {last_name}"

            # Extract times after "time" keyword - handles malformed "time"
            time_match = re.search(r"t[^\d]*ime?\s*([\d\.\s]+)", name_line, re.IGNORECASE)

            # If no time keyword, grab numbers after both parentheses (country and year)
            if not time_match:
                # Looks for pattern: (COUNTRY) (year_junk) THEN grab all numbers
                time_match = re.search(
                    r"\([A-Z]{3}\)\s*\([^\)]+\)[^\d]+([\d\.\s]+)", name_line
                )

            if not time_match:
                return None

            times_str = time_match.group(1).strip()
            times = [float(t) for t in times_str.split() if t.replace(".", "").replace("-", "").isdigit()]

            # Gets H1-H10 times + official time
            if len(times) < 11:
                return None

            # Official time is the 11th time (index 10)
            # But if it's unreasonably small (< H10), use H10 instead (malformed data)
            official_time = times[10] if len(times) > 10 else times[-1]
            if official_time < times[9]:  # Official time index should be >= H10
                official_time = times[9]

            # Extracting lane/place
            lane_place_match = re.search(r"(\d+)\s*/\s*(\d+)", name_line)
            lane = lane_place_match.group(1) if lane_place_match else None
            place = lane_place_match.group(2) if lane_place_match else None

            # Line 2 - Intervals (sometimes reaction time)
            interval_line = lines[start_idx + 1] if start_idx + 1 < len(lines) else ""
            reaction_time = None

            reaction_match = re.search(r"reaction time\s+([\d\.]+)", interval_line)
            if reaction_match:
                reaction_time = float(reaction_match.group(1))

            # Build dictionary
            record = {
                "athlete_name": athlete_name,
                "country": country,
                "birth_year": birth_year,
                "event": current_event,
                "wind": current_wind,
                "lane": lane,
                "place": place,
                "reaction_time": reaction_time,
                "official_time": official_time,
            }

            # Add hurdle times H1-H10
            for i in range(min(10, len(times) - 1)):
                record[f"H{i + 1}"] = times[i]

            # Add and calculate split sections
            if len(times) >= 4:
                record["split_H1_H4"] = times[3]
            if len(times) >= 7:
                record["split_H4_H7"] = times[6] - times[3]
            if len(times) >= 10:
                record["split_H7_H10"] = times[9] - times[6]

            return record

        # If none of the logic works
        except Exception:
            return None

    def extract_first_page_to_df(self, pdf_path: Path): #type: ignore
        """Extract first page data and return as DataFrame"""
        with pdfplumber.open(pdf_path) as pdf:
            first_page = pdf.pages[0]
            text = first_page.extract_text()
            lines = text.split("\n")

            records = []
            current_wind = None
            current_event = None

            i = 0
            while i < len(lines):
                line = lines[i]

                # Check for wind data
                wind_match = re.search(r"wind\s*([-+]?\d+\.\d+)\s*m/s", line)
                if wind_match:
                    current_wind = float(wind_match.group(1))

                # Check for event name
                if "Athlos" in line or "World Athletics" in line or "Championships" in line:
                    current_event = line.strip()

                # Check for athlete data with a flexible pattern for Unicode names
                if re.match(r"^[A-ZÀ-ž][\w]+,\s+[A-ZÀ-ž]", line, re.UNICODE):
                    athlete_record = self.parse_athlete_data(lines, i, current_wind, current_event)
                    if athlete_record:
                        records.append(athlete_record)
                        i += 3
                        continue
                i += 1
            df = pd.DataFrame(records)
            return df

    def data(self, path: str) -> Optional[pd.DataFrame]:
        # default is 1 page for read_pdf!
        table_data = tabula.read_pdf(path, pages=1, multiple_tables=True, pandas_options={'header': None}, force_subprocess=True, encoding='cp1252')
        if not table_data:
            return None
        return pd.concat(table_data, ignore_index=True)

    def clean(self, df: pd.DataFrame, m: float) -> Tuple[pd.DataFrame, pd.DataFrame]:
        df = df.copy()
        df = df.dropna(how="all").drop_duplicates()
        cols = df.select_dtypes(include='number').columns
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
        with open(path, 'wb') as pdf:
            pdf.write(re.content)
        return path

if __name__ == "__main__":
    W100H_DEMO_TEST = W100H_DEMO()
    url = 'https://www.athletefirst.org/wp-content/uploads/2025/10/20251010-Womens-100m-Hurdles-meeting.pdf'
    path = W100H_DEMO_TEST.download(url, 'W100H.pdf')
    df = W100H_DEMO_TEST.extract_first_page_to_df(Path(path))
    if df is not None and not df.empty:
        clean, outliers = W100H_DEMO_TEST.clean(df, m=1.5)
        W100H_DEMO_TEST.csv(clean, 'W100H_DEMO_PG1_CLEAN.csv')
        W100H_DEMO_TEST.csv(outliers, 'W100H_DEMO_PG1_OUTLIERS.csv')
        print("Cleaned and exported PDF data to csvs")


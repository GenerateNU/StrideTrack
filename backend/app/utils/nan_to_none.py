import math


def nan_to_none(rows: list[dict]) -> list[dict]:
    return [
        {
            k: (None if isinstance(v, float) and math.isnan(v) else v)
            for k, v in row.items()
        }
        for row in rows
    ]

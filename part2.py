import sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "cell_counts.db"
OUTPUT_PATH = ROOT / "output" / "population_frequencies.csv"

QUERY = """
    SELECT
        sample,
        SUM(count) OVER (PARTITION BY sample) AS total_count,
        population,
        count,
        100.0 * count / SUM(count) OVER (PARTITION BY sample) AS percentage
    FROM cell_counts
    ORDER BY sample, population;
"""


def main():
    # query
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql(QUERY, conn)
    finally:
        conn.close()

    # save output
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

if __name__ == "__main__":
    main()

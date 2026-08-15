import sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "cell_counts.db"
SAMPLES_OUTPUT_PATH = ROOT / "output" / "part4_baseline_samples.csv"
EXTENSION_OUTPUT_PATH = ROOT / "output" / "part4_extensions.csv"

BASELINE_VIEW_SQL = """
    CREATE TEMP VIEW baseline_samples AS
    SELECT s.sample, sub.subject, sub.project, sub.response, sub.sex
    FROM samples s
    JOIN subjects sub ON sub.subject = s.subject
    WHERE sub.condition = 'melanoma'
      AND sub.treatment = 'miraclib'
      AND s.sample_type = 'PBMC'
      AND s.time_from_treatment_start = 0;
"""

EXTENSION_QUERY = """
    SELECT 'project_sample_size' AS metric, p.project AS identifier, COUNT(bs.sample) AS count
    FROM projects p
    LEFT JOIN baseline_samples bs ON bs.project = p.project
    GROUP BY p.project

    UNION ALL

    SELECT 'response_sample_size', response, COUNT(DISTINCT subject)
    FROM baseline_samples
    GROUP BY response

    UNION ALL

    SELECT 'sex_sample_count', sex, COUNT(DISTINCT subject)
    FROM baseline_samples
    GROUP BY sex;
"""


def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(BASELINE_VIEW_SQL)
        baseline_df = pd.read_sql("SELECT * FROM baseline_samples", conn)
        extension_df = pd.read_sql(EXTENSION_QUERY, conn)
    finally:
        conn.close()

    OUTPUT_DIR = SAMPLES_OUTPUT_PATH.parent
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    baseline_df.to_csv(SAMPLES_OUTPUT_PATH, index=False)
    extension_df.to_csv(EXTENSION_OUTPUT_PATH, index=False)

if __name__ == "__main__":
    main()

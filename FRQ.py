import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "cell_counts.db"

QUERY = """
    SELECT AVG(cc.count)
    FROM cell_counts cc
    JOIN samples s    ON s.sample = cc.sample
    JOIN subjects sub ON sub.subject = s.subject
    WHERE sub.condition = 'melanoma'
      AND sub.sex = 'M'
      AND sub.response = 'yes'
      AND s.time_from_treatment_start = 0
      AND cc.population = 'b_cell';
"""


def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        avg_b_cell = conn.execute(QUERY).fetchone()[0]
    finally:
        conn.close()

    print(f"Average B cell count: {avg_b_cell:.3f}")


if __name__ == "__main__":
    main()

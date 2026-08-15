import sqlite3
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "cell-count.csv"
DB_PATH = ROOT / "cell_counts.db"

SCHEMA_SQL = """
CREATE TABLE projects (
    project TEXT PRIMARY KEY
);

CREATE TABLE subjects (
    subject     TEXT PRIMARY KEY,
    project     TEXT NOT NULL REFERENCES projects(project),
    condition   TEXT NOT NULL,
    age         INTEGER,
    sex         TEXT,
    treatment   TEXT,
    response    TEXT
);

CREATE TABLE samples (
    sample                      TEXT PRIMARY KEY,
    subject                     TEXT NOT NULL REFERENCES subjects(subject),
    sample_type                 TEXT NOT NULL,
    time_from_treatment_start   INTEGER
);

CREATE TABLE cell_counts (
    sample      TEXT NOT NULL REFERENCES samples(sample),
    population  TEXT NOT NULL,
    count       INTEGER NOT NULL,
    PRIMARY KEY (sample, population)
);

CREATE INDEX idx_subjects_project ON subjects(project);
CREATE INDEX idx_samples_subject ON samples(subject);

CREATE INDEX idx_subjects_condition_treatment ON subjects(condition, treatment);
CREATE INDEX idx_samples_type_time ON samples(sample_type, time_from_treatment_start);
"""


def load_csv(conn):
    df = pd.read_csv(CSV_PATH)

    #split up data and save in different tables
    df[["project"]].drop_duplicates().to_sql("projects", conn, if_exists="append", index=False)

    df[["subject", "project", "condition", "age", "sex", "treatment", "response"]].drop_duplicates(subset="subject").to_sql("subjects", conn, if_exists="append", index=False)

    df[["sample", "subject", "sample_type", "time_from_treatment_start"]].to_sql("samples", conn, if_exists="append", index=False)

    #in-line with part 2, split up the cell counts into seperate rows with a "type" column
    df.melt(
        id_vars=["sample"],
        value_vars=["b_cell", "cd8_t_cell", "cd4_t_cell", "nk_cell", "monocyte"],
        var_name="population",
        value_name="count",
    ).to_sql("cell_counts", conn, if_exists="append", index=False)


def main():
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)


    try:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(SCHEMA_SQL)
        load_csv(conn)
        conn.commit()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
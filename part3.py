import sqlite3
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "cell_counts.db"
PLOT_OUTPUT_PATH = ROOT / "output" / "part3_boxplots.png"
STATS_OUTPUT_PATH = ROOT / "output" / "part3_significance.md"

BASE_QUERY = """
    SELECT
        sub.response,
        s.time_from_treatment_start AS time,
        cc.population,
        100.0 * cc.count / SUM(cc.count) OVER (PARTITION BY cc.sample) AS percentage
    FROM cell_counts cc
    JOIN samples s    ON s.sample = cc.sample
    JOIN subjects sub ON sub.subject = s.subject
    WHERE sub.condition = 'melanoma'
      AND sub.treatment = 'miraclib'
      AND s.sample_type = 'PBMC';
"""

POPULATIONS = ["b_cell", "cd4_t_cell", "cd8_t_cell", "monocyte", "nk_cell"]
TIMEPOINTS = [0, 7, 14]


def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql(BASE_QUERY, conn)
    finally:
        conn.close()

    #group data based on my 3 distinguishing features, and then use the percentages which is what we are actually measuring
    groups = df.groupby(["time", "population", "response"])["percentage"]

    #boxplots drawing
    fig, axes = plt.subplots(len(TIMEPOINTS), len(POPULATIONS), figsize=(18, 10), sharey="col")

    for row_idx, t in enumerate(TIMEPOINTS):
        for col_idx, population in enumerate(POPULATIONS):
            ax = axes[row_idx, col_idx]
            
            non_responders = groups.get_group((t, population, "no"))
            responders = groups.get_group((t, population, "yes"))
            
            ax.boxplot([non_responders, responders], tick_labels=["non-resp", "resp"])

            if row_idx == 0:
                ax.set_title(population)
            if col_idx == 0:
                ax.set_ylabel(f"time {t}\n% of total cells")

    fig.suptitle(
        "Population relative frequency by timepoint: responders vs non-responders\n"
        "(melanoma, miraclib, PBMC)"
    )
    fig.tight_layout()

    PLOT_OUTPUT_PATH.parent.mkdir(exist_ok=True)
    fig.savefig(PLOT_OUTPUT_PATH, dpi=150)

    # check normality for t-test vs Mann-Whitney desicion
    # print("Shapiro-Wilk normality check:")
    # for t in TIMEPOINTS:
    #     for population in POPULATIONS:
    #         non_responders = groups.get_group((t, population, "no"))
    #         responders = groups.get_group((t, population, "yes"))

    #         _, shapiro_p_non_responder = stats.shapiro(non_responders)
    #         _, shapiro_p_responder = stats.shapiro(responders)

    #         print(f"  time={t:2d} {population:12s} non-resp p={shapiro_p_non_responder:.3e}  resp p={shapiro_p_responder:.3e}")

    # mann whitney test for significance
    results = []
    for population in POPULATIONS:
        for t in TIMEPOINTS:
            non_responders = groups.get_group((t, population, "no"))
            responders = groups.get_group((t, population, "yes"))

            _, mannwhitney_p = stats.mannwhitneyu(non_responders, responders, alternative="two-sided")

            results.append({
                "time": t,
                "population": population,
                "n_non_responder": len(non_responders),
                "n_responder": len(responders),
                "median_non_responder": non_responders.median(),
                "median_responder": responders.median(),
                "mannwhitney_p": mannwhitney_p,
                "significant": mannwhitney_p < 0.05,
            })

    lines = []
    for r in results:
        verdict = "YES" if r["significant"] else "NO"
        lines.append(
            f"- {verdict} statistically significant difference in relative frequencies "
            f"between responders and non-responders for {r['population']} at time {r['time']}."
        )
        lines.append(
            f"  - Mann-Whitney findings that p={r['mannwhitney_p']:.4f} "
            f"(median non-responder={r['median_non_responder']:.2f}%, median responder={r['median_responder']:.2f}%)."
        )

    STATS_OUTPUT_PATH.parent.mkdir(exist_ok=True)
    STATS_OUTPUT_PATH.write_text("\n".join(lines))


if __name__ == "__main__":
    main()

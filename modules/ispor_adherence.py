# ispor_adherence.py: measure statin adherence as proportion of days covered (PDC)
# Writes output/adherence_results.md
# Data: CMS DE-SynPUF synthetic Medicare claims in OMOP Common Data Model format
# (public data; see README.md for sources)

import numpy as np
import pandas as pd

from config import (
    ADHERENCE_THRESHOLD,
    DATA_FILE,
    MIN_DAYS_FROM_FIRST_RECORD_TO_YEAR_END,
    MIN_STATIN_RECORDS_ON_DIFFERENT_DATES,
    MINIMUM_AGE,
    OUTPUT_DIR,
)

# Groups smaller than this are not shown in results by group
# Basis: analyst choice
MIN_GROUP_SIZE_TO_REPORT = 30

records = pd.read_csv(DATA_FILE)
records["drug_exposure_start_date"] = pd.to_datetime(records["drug_exposure_start_date"])


def markdown_table(frame: pd.DataFrame) -> list[str]:
    # Format a small table as markdown lines
    header = "| " + " | ".join(frame.columns) + " |"
    divider = "| " + " | ".join("---" for _ in frame.columns) + " |"
    rows = ["| " + " | ".join(str(value) for value in row) + " |" for row in frame.values]
    return [header, divider, *rows]


report = [
    "# Standards and public sources",
    "",
    "- **Data:** CMS DE-SynPUF synthetic Medicare claims in OMOP Common Data Model format, "
    "from the BigQuery public dataset `bigquery-public-data.cms_synthetic_patient_data_omop` "
    "([CMS DE-SynPUF](https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files/cms-2008-2010-data-entrepreneurs-synthetic-public-use-file-de-synpuf)). "
    "CMS states the file has very limited value for drawing conclusions about real "
    "Medicare beneficiaries, so results demonstrate methods only.",
    "- **OMOP standards applied:** records from the standard DRUG_EXPOSURE table; drugs identified by "
    "standard RxNorm (the US National Library of Medicine's standard drug names) Ingredient concepts; "
    "all products per ingredient found through CONCEPT_ANCESTOR; ingredient strength from DRUG_STRENGTH "
    "([OMOP CDM](https://ohdsi.github.io/CommonDataModel/))",
    "- **ISPOR standards applied:** adherence as defined by ISPOR "
    "([Cramer et al., 2008](https://www.ispor.org/heor-resources/good-practices/article/medication-compliance-and-persistence-terminology-and-definitions)), "
    "measured as proportion of days covered (PDC) using public Pharmacy Quality Alliance (PQA) "
    "measure conventions ([PQA](https://www.pqaalliance.org/measures-overview))",
    "- **Full list of sources and design choices:** see README.md",
]

# ---------------------------------------------------------------------------
# Adherence: proportion of days covered (PDC)
# ---------------------------------------------------------------------------

report += [
    "",
    "# Adherence: proportion of days covered (PDC)",
    "",
    "**Definition (ISPOR):** adherence is the extent to which a patient takes a medication "
    "according to the prescribed timing, dose, and frequency "
    "([Cramer et al., 2008](https://www.ispor.org/heor-resources/good-practices/article/medication-compliance-and-persistence-terminology-and-definitions)). "
    "Pharmacy records serve as a proxy: if a patient has medication on hand on a given day, "
    "the day counts as covered.",
    "",
    "**Measure:** PDC = days with a statin on hand during the measurement period / days in the "
    "measurement period. PDC ranges from 0% to 100%.",
    "",
    "**Conventions from PQA public measure summaries** "
    "([PQA](https://www.pqaalliance.org/measures-overview)):",
    "",
    "- Measurement period: each calendar year, starting at the patient's first statin record in that year",
    f"- At least {MIN_STATIN_RECORDS_ON_DIFFERENT_DATES} statin records on different dates in the year",
    f"- First statin record at least {MIN_DAYS_FROM_FIRST_RECORD_TO_YEAR_END} days before the end of the year",
    f"- Age {MINIMUM_AGE} or older",
    f"- Adherent: PDC of {ADHERENCE_THRESHOLD:.0%} or higher",
    "",
    "**Additional choices (analyst choice):**",
    "",
    "- All statins count together; combination products containing a statin count as statin.",
    "- Overlapping supply is not shifted forward; each covered day is counted once.",
    "- Only records starting within the year count toward that year.",
    "- Continuous enrollment during the year is not checked (see README for future development).",
    "- Results are descriptive only. With synthetic data, differences between groups are not real-world findings.",
]

# Statin records with usable days supply
statins = records[(records["medication_group"] == "Statin") & (records["days_supply"] > 0)].copy()
statins["start_day"] = (statins["drug_exposure_start_date"] - pd.Timestamp("1970-01-01")).dt.days
statins["year"] = statins["drug_exposure_start_date"].dt.year

results = []
for year in sorted(statins["year"].unique()):
    year_records = statins[statins["year"] == year].copy()
    year_end_day = (pd.Timestamp(f"{year}-12-31") - pd.Timestamp("1970-01-01")).days

    # Each patient's first statin record in the year, and their characteristics at that record
    year_records = year_records.sort_values(["person_id", "start_day", "drug_name_simplified"])
    first_records = year_records.groupby("person_id").first()
    patients = pd.DataFrame(
        {
            "first_day": first_records["start_day"],
            "first_statin": first_records["drug_name_simplified"],
            "age": first_records["age_at_exposure"],
            "gender": first_records["gender"],
            "distinct_dates": year_records.groupby("person_id")["start_day"].nunique(),
        }
    )

    # Apply the PQA public eligibility conventions
    patients = patients[
        (patients["distinct_dates"] >= MIN_STATIN_RECORDS_ON_DIFFERENT_DATES)
        & (year_end_day - patients["first_day"] + 1 >= MIN_DAYS_FROM_FIRST_RECORD_TO_YEAR_END)
        & (patients["age"] >= MINIMUM_AGE)
    ].copy()
    eligible = year_records[year_records["person_id"].isin(patients.index)].copy()

    # Days covered: each record covers its start day through start + days supply - 1,
    # stopping at the end of the year. Count each covered day once per patient.
    eligible["end_day"] = (eligible["start_day"] + eligible["days_supply"] - 1).clip(upper=year_end_day)
    eligible = eligible.sort_values(["person_id", "start_day"])
    latest_prior_end = (
        eligible.groupby("person_id")["end_day"].cummax().groupby(eligible["person_id"]).shift()
    )
    first_new_day = np.maximum(
        eligible["start_day"], (latest_prior_end + 1).where(latest_prior_end.notna(), -np.inf)
    )
    eligible["new_days_covered"] = (eligible["end_day"] - first_new_day + 1).clip(lower=0)

    patients["days_covered"] = eligible.groupby("person_id")["new_days_covered"].sum()
    patients["days_in_period"] = year_end_day - patients["first_day"] + 1
    patients["pdc"] = patients["days_covered"] / patients["days_in_period"]
    patients["adherent"] = patients["pdc"] >= ADHERENCE_THRESHOLD
    patients["year"] = year
    results.append(patients)

pdc = pd.concat(results) if results else pd.DataFrame()


def summarize(frame: pd.DataFrame, group_column: str) -> pd.DataFrame:
    # Patients, average PDC, and share adherent for each group
    summary = frame.groupby(group_column).agg(
        patients=("pdc", "size"),
        average_pdc=("pdc", "mean"),
        median_pdc=("pdc", "median"),
        share_adherent=("adherent", "mean"),
    )
    summary = summary[summary["patients"] >= MIN_GROUP_SIZE_TO_REPORT].reset_index()
    summary["patients"] = summary["patients"].map("{:,}".format)
    summary["average_pdc"] = summary["average_pdc"].map("{:.1%}".format)
    summary["median_pdc"] = summary["median_pdc"].map("{:.1%}".format)
    summary["share_adherent"] = summary["share_adherent"].map("{:.1%}".format)
    return summary.rename(
        columns={
            "patients": "Patients",
            "average_pdc": "Average PDC",
            "median_pdc": "Median PDC",
            "share_adherent": f"Share with PDC >= {ADHERENCE_THRESHOLD:.0%}",
        }
    )


if pdc.empty:
    report += ["", "No patients met the adherence measure conventions."]
else:
    excluded_supply = (
        (records["medication_group"] == "Statin") & ~(records["days_supply"] > 0)
    ).sum()
    report += [
        "",
        f"Statin records excluded for missing, zero, or negative days supply: {excluded_supply:,}",
        "",
        "## By year",
        "",
        *markdown_table(summarize(pdc, "year").rename(columns={"year": "Year"})),
        "",
        "## By first statin in the year (all years combined)",
        "",
        *markdown_table(summarize(pdc, "first_statin").rename(columns={"first_statin": "First statin"})),
    ]
    pdc["age_group"] = pd.cut(
        pdc["age"], bins=[17, 64, 74, 84, 200], labels=["18-64", "65-74", "75-84", "85+"]
    ).astype(str)
    report += [
        "",
        "## By age group (all years combined)",
        "",
        *markdown_table(summarize(pdc, "age_group").rename(columns={"age_group": "Age group"})),
        "",
        "## By gender (all years combined)",
        "",
        *markdown_table(summarize(pdc, "gender").rename(columns={"gender": "Gender"})),
        "",
        f"Groups with fewer than {MIN_GROUP_SIZE_TO_REPORT} patients are not shown.",
    ]

OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "adherence_results.md"
OUTPUT_FILE.write_text("\n".join(report) + "\n")
print(f"Records read: {len(records):,}")
print(f"Summary saved to {OUTPUT_FILE}")

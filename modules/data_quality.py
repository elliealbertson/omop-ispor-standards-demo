# data_quality.py: profile the drug exposure records and report data quality
# Writes output/data_quality.md
# Data: CMS DE-SynPUF synthetic Medicare claims in OMOP Common Data Model format
# (public data; see README.md for sources)

import pandas as pd

from config import DATA_FILE, OUTPUT_DIR

records = pd.read_csv(DATA_FILE)
records["drug_exposure_start_date"] = pd.to_datetime(records["drug_exposure_start_date"])

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
# Data profile
# ---------------------------------------------------------------------------

column_descriptions = {
    "drug_exposure_id": ("OMOP drug exposure record identifier", "drug_exposure.drug_exposure_id"),
    "person_id": ("Patient identifier", "drug_exposure.person_id"),
    "drug_exposure_start_date": ("Start date of the drug exposure record", "drug_exposure.drug_exposure_start_date"),
    "days_supply": ("Days of medication supplied, as recorded", "drug_exposure.days_supply"),
    "drug_concept_id": ("Standard drug product concept", "drug_exposure.drug_concept_id"),
    "ingredients": ("Matched active ingredient or ingredients", "RxNorm Ingredient concepts and CONCEPT_ANCESTOR; niacin requires >=500 mg"),
    "drug_name_simplified": ("Active ingredient name(s), regardless of dose or brand", "Same as ingredients"),
    "medication_group": ("Statin or other lipid-lowering drug", "Statin if any matched ingredient is a statin"),
    "is_combination": ("Whether the product has more than one matched ingredient", "True when more than one ingredient is listed"),
    "drug_name": ("Standard RxNorm drug product name", "concept.concept_name"),
    "brand_name": ("Brand name when shown in the drug name", "Text inside brackets in drug_name"),
    "age_at_exposure": ("Patient age at the record start date", "Start year minus person.year_of_birth"),
    "gender": ("Patient gender", "person.gender_concept_id matched to concept.concept_name"),
}

missing_values = records.isna().sum()
report += [
    "",
    "# Columns",
    "",
    "| Column | Data type | Missing | Contents | Lineage |",
    "| --- | --- | ---: | --- | --- |",
]
for column, (description, lineage) in column_descriptions.items():
    report.append(
        f"| {column} | {records[column].dtype} | {missing_values[column]:,} | {description} | {lineage} |"
    )

report += [
    "",
    "# Dataset size and dates",
    "",
    f"- Drug exposure records: {len(records):,}",
    f"- Unique patients: {records['person_id'].nunique():,}",
    f"- Record start date range: {records['drug_exposure_start_date'].min().date()} "
    f"to {records['drug_exposure_start_date'].max().date()}",
]

# Record counts by drug, combining strengths and brand/generic products
report += [
    "",
    "# Records by drug",
    "",
    "Counts use `drug_name_simplified`, so all strengths, brands, and generics of an "
    "ingredient are combined. Products containing a statin are grouped as Statin.",
]
drug_counts = records.groupby(["medication_group", "drug_name_simplified"]).size()
for group in ["Statin", "Other lipid-lowering"]:
    if group not in drug_counts.index.get_level_values(0):
        continue
    group_counts = drug_counts.loc[group].sort_values(ascending=False)
    report += ["", f"## {group} ({group_counts.sum():,} records)", "", "| Drug | Records |", "| --- | ---: |"]
    report += [f"| {drug} | {count:,} |" for drug, count in group_counts.items()]

# ---------------------------------------------------------------------------
# Data quality
# ---------------------------------------------------------------------------

days_supply = records["days_supply"]
missing_supply = days_supply.isna()
zero_or_negative_supply = days_supply.notna() & (days_supply <= 0)
usable_supply = days_supply[days_supply > 0]

report += [
    "",
    "# Data quality",
    "",
    "## Days supply",
    "",
    f"- Missing: {missing_supply.sum():,} records ({missing_supply.mean():.2%})",
    f"- Zero or negative: {zero_or_negative_supply.sum():,} records ({zero_or_negative_supply.mean():.2%})",
    f"- Positive values: median {usable_supply.median():.0f} days; "
    f"5th percentile {usable_supply.quantile(0.05):.0f}; 95th percentile {usable_supply.quantile(0.95):.0f}; "
    f"maximum {usable_supply.max():.0f}",
    f"- Above 90 days: {(days_supply > 90).sum():,} records",
    f"- Above 180 days: {(days_supply > 180).sum():,} records",
    f"- Above 365 days: {(days_supply > 365).sum():,} records",
    "",
    "**Handling in the adherence analysis:**",
    "",
    "- Records with missing, zero, or negative days supply are excluded, because the days "
    "they cover cannot be determined (analyst choice).",
    "- Records with long days supply are kept as recorded. PDC counts only days inside the "
    "measurement period, so a long supply cannot raise PDC above 100% (analyst choice; no "
    "published standard sets a maximum).",
]

# Multiple records for the same patient, product, and start date
same_day_key = ["person_id", "drug_concept_id", "drug_exposure_start_date"]
same_day_counts = records.groupby(same_day_key).size()
same_day_groups = same_day_counts[same_day_counts > 1]
report += [
    "",
    "## Multiple records for the same patient, product, and start date",
    "",
    f"- Combinations with more than one record: {len(same_day_groups):,}",
    f"- Records involved: {same_day_groups.sum():,} ({same_day_groups.sum() / len(records):.2%} of all records)",
    "",
    "**Handling in the adherence analysis:** records are kept as recorded. PDC counts each "
    "covered day once, so records covering the same days are not double counted (analyst choice).",
]

# ---------------------------------------------------------------------------
# Future development
# ---------------------------------------------------------------------------

combination_records = records["is_combination"].sum()
report += [
    "",
    "# Opportunities for future development",
    "",
    "- **Provider details:** provider identifiers and specialties were not populated in the "
    "drug exposure records; find another way to link providers.",
    f"- **Combination products:** products containing a statin are grouped as Statin for now; "
    f"combination products account for {combination_records:,} records "
    f"({combination_records / len(records):.2%}) and could be handled separately later.",
    "- **Multiple records on the same date:** validate whether multiple records for the same "
    "patient, product, and start date represent one dispensing event or separate events.",
    "- **Continuous enrollment:** use the OMOP OBSERVATION_PERIOD table to confirm each patient "
    "is observable for the full measurement period.",
]

OUTPUT_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "data_quality.md"
OUTPUT_FILE.write_text("\n".join(report) + "\n")
print(f"Records read: {len(records):,}")
print(f"Summary saved to {OUTPUT_FILE}")

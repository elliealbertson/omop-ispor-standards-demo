# config.py: shared settings
# Each setting states its basis: a public industry standard (OMOP or ISPOR),
# a public measure convention (PQA), or an analyst choice where no published
# standard sets the value. README.md lists every source.

# Keep data and output files at the repository root.
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = REPO_ROOT / "drug_exposures_derived_table.csv"
OUTPUT_DIR = REPO_ROOT / "output"

# Data: CMS DE-SynPUF synthetic Medicare claims in OMOP Common Data Model format,
# hosted as a BigQuery public dataset
# https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files/cms-2008-2010-data-entrepreneurs-synthetic-public-use-file-de-synpuf
BIGQUERY_DATASET = "bigquery-public-data.cms_synthetic_patient_data_omop"

# OMOP standard tables used in the query
# https://ohdsi.github.io/CommonDataModel/
DRUG_EXPOSURE_TABLE = f"{BIGQUERY_DATASET}.drug_exposure"
CONCEPT_TABLE = f"{BIGQUERY_DATASET}.concept"
CONCEPT_ANCESTOR_TABLE = f"{BIGQUERY_DATASET}.concept_ancestor"
DRUG_STRENGTH_TABLE = f"{BIGQUERY_DATASET}.drug_strength"
PERSON_TABLE = f"{BIGQUERY_DATASET}.person"

# Statins: the drug class used for the adherence analysis
# Names match RxNorm (the US National Library of Medicine's standard drug names)
# ingredient names in the OMOP Standardized Vocabularies
# https://book.ohdsi.org/StandardizedVocabularies.html
STATIN_INGREDIENTS = (
    "lovastatin",
    "pravastatin",
    "simvastatin",
    "fluvastatin",
    "atorvastatin",
    "cerivastatin",
    "rosuvastatin",
    "pitavastatin",
)

# Other lipid-lowering drugs, included for context on use of similar therapies
OTHER_LIPID_LOWERING_INGREDIENTS = (
    "ezetimibe",
    "niacin",
    "fenofibrate",
    "fenofibric acid",
    "gemfibrozil",
    "cholestyramine",
    "colestipol",
    "colesevelam",
)

# Newer lipid-lowering drugs, checked against the data's date range
NEWER_LIPID_LOWERING_INGREDIENTS = (
    "alirocumab",
    "evolocumab",
    "bempedoic acid",
    "inclisiran",
)

# Count only niacin products at prescription strength (immediate and extended
# release), using the OMOP DRUG_STRENGTH table
# Basis: analyst choice, to exclude multivitamin and vitamin B products
NIACIN_MIN_STRENGTH_MG = 500

# Adherence: proportion of days covered (PDC) in each calendar-year measurement period
# Basis: Pharmacy Quality Alliance (PQA) public measure summaries
# https://www.pqaalliance.org/measures-overview

# Patients need at least this many statin records on different dates in the year
# Basis: PQA public measure summaries
MIN_STATIN_RECORDS_ON_DIFFERENT_DATES = 2

# The first statin record in the year must be at least this many days before the
# end of the year
# Basis: PQA public measure summaries
MIN_DAYS_FROM_FIRST_RECORD_TO_YEAR_END = 91

# Patients with a PDC at or above this value are counted as adherent
# Basis: PQA public measure summaries
ADHERENCE_THRESHOLD = 0.80

# Only include adults (age at the first statin record in the year)
# Basis: PQA public measure summaries (adults 18 and older)
MINIMUM_AGE = 18

# Refuse any billed query that BigQuery estimates will scan more than 10 GB
MAX_BYTES_BILLED = 10_000_000_000

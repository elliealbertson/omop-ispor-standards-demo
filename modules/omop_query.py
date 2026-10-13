# omop_query.py: pull drug exposure records for statins and other lipid-lowering drugs
# One row = one OMOP DRUG_EXPOSURE record, as recorded in the public data
#
# Data: CMS DE-SynPUF synthetic Medicare claims in OMOP Common Data Model format,
# a BigQuery public dataset (see README.md for sources). CMS records prescription
# drug events; the OMOP version stores them in the DRUG_EXPOSURE table.
#
# OMOP standards applied in this query (https://ohdsi.github.io/CommonDataModel/):
# - Records come from the standard DRUG_EXPOSURE table; age and gender from PERSON
# - Each drug is identified by its standard RxNorm "Ingredient" concept
#   (RxNorm: the US National Library of Medicine's standard drug names)
# - CONCEPT_ANCESTOR links each ingredient to every product containing it
#   (every strength, form, brand, and generic), with no hand-typed code lists
# - DRUG_STRENGTH supplies the amount of each ingredient in each product
#
# Records are not merged, filtered, or edited here. data_quality.py reports data quality
# (e.g., missing or unusual days supply) before any analysis decisions.

import os

from google.cloud import bigquery

from config import (
    CONCEPT_ANCESTOR_TABLE,
    CONCEPT_TABLE,
    DATA_FILE,
    DRUG_EXPOSURE_TABLE,
    DRUG_STRENGTH_TABLE,
    MAX_BYTES_BILLED,
    NEWER_LIPID_LOWERING_INGREDIENTS,
    NIACIN_MIN_STRENGTH_MG,
    OTHER_LIPID_LOWERING_INGREDIENTS,
    OUTPUT_DIR,
    PERSON_TABLE,
    STATIN_INGREDIENTS,
)

QUERY = f"""
-- OMOP standard: find the standard RxNorm Ingredient concept for each drug name
WITH ingredients AS (
  SELECT
    concept_id AS ingredient_concept_id,
    LOWER(concept_name) AS ingredient_name
  FROM `{CONCEPT_TABLE}`
  WHERE vocabulary_id = 'RxNorm'
    AND concept_class_id = 'Ingredient'
    AND standard_concept = 'S'
    AND LOWER(concept_name) IN UNNEST(@ingredient_names)
),

-- OMOP standard: CONCEPT_ANCESTOR links each ingredient to every product containing it
products AS (
  SELECT
    ancestor.descendant_concept_id AS drug_concept_id,
    ingredients.ingredient_concept_id,
    ingredients.ingredient_name
  FROM ingredients
  JOIN `{CONCEPT_ANCESTOR_TABLE}` AS ancestor
    ON ancestor.ancestor_concept_id = ingredients.ingredient_concept_id
),

-- OMOP standard: DRUG_STRENGTH gives ingredient amounts; keep niacin at prescription strength
products_without_vitamins AS (
  SELECT products.*
  FROM products
  LEFT JOIN `{DRUG_STRENGTH_TABLE}` AS strength
    ON strength.drug_concept_id = products.drug_concept_id
    AND strength.ingredient_concept_id = products.ingredient_concept_id
  WHERE products.ingredient_name != 'niacin'
    OR strength.amount_value >= @niacin_min_strength_mg
),

-- List the matched ingredients once per drug product
product_list AS (
  SELECT
    drug_concept_id,
    STRING_AGG(DISTINCT ingredient_name, ', ' ORDER BY ingredient_name) AS ingredients
  FROM products_without_vitamins
  GROUP BY drug_concept_id
),

-- Add each product's standard RxNorm name and any brand shown in brackets
product_names AS (
  SELECT
    product_list.drug_concept_id,
    product_list.ingredients,
    drug.concept_name AS drug_name,
    REGEXP_EXTRACT(drug.concept_name, r'\\[([^\\]]+)\\]') AS brand_name
  FROM product_list
  JOIN `{CONCEPT_TABLE}` AS drug
    ON drug.concept_id = product_list.drug_concept_id
)

-- One row per DRUG_EXPOSURE record, with drug details and patient characteristics
SELECT
  exposure.drug_exposure_id,
  exposure.person_id,
  exposure.drug_exposure_start_date,
  exposure.days_supply,
  exposure.drug_concept_id,
  product_names.ingredients,
  product_names.ingredients AS drug_name_simplified,
  CASE
    WHEN EXISTS (
      SELECT 1
      FROM UNNEST(SPLIT(product_names.ingredients, ', ')) AS ingredient
      WHERE ingredient IN UNNEST(@statin_ingredient_names)
    ) THEN 'Statin'
    ELSE 'Other lipid-lowering'
  END AS medication_group,
  ARRAY_LENGTH(SPLIT(product_names.ingredients, ', ')) > 1 AS is_combination,
  product_names.drug_name,
  product_names.brand_name,
  EXTRACT(YEAR FROM exposure.drug_exposure_start_date) - person.year_of_birth
    AS age_at_exposure,
  gender.concept_name AS gender
FROM `{DRUG_EXPOSURE_TABLE}` AS exposure
JOIN product_names
  ON product_names.drug_concept_id = exposure.drug_concept_id
LEFT JOIN `{PERSON_TABLE}` AS person
  ON person.person_id = exposure.person_id
LEFT JOIN `{CONCEPT_TABLE}` AS gender
  ON gender.concept_id = person.gender_concept_id
ORDER BY exposure.person_id, exposure.drug_exposure_start_date
"""

if DATA_FILE.exists():
    print(f"Found existing dataset at {DATA_FILE}; skipping BigQuery query.")
else:
    # Connect to BigQuery using your personal Google Cloud project
    client = bigquery.Client(project=os.environ["GOOGLE_CLOUD_PROJECT"])

    # Search the configured statins, other drugs, and newer drugs
    ingredient_names = list(
        STATIN_INGREDIENTS
        + OTHER_LIPID_LOWERING_INGREDIENTS
        + NEWER_LIPID_LOWERING_INGREDIENTS
    )

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ArrayQueryParameter("ingredient_names", "STRING", ingredient_names),
            bigquery.ArrayQueryParameter(
                "statin_ingredient_names",
                "STRING",
                list(STATIN_INGREDIENTS),
            ),
            bigquery.ScalarQueryParameter(
                "niacin_min_strength_mg",
                "FLOAT64",
                NIACIN_MIN_STRENGTH_MG,
            ),
        ],
        maximum_bytes_billed=MAX_BYTES_BILLED,
    )

    # Run the query and save the results as returned
    records = client.query(QUERY, job_config=job_config).to_dataframe()
    records.to_csv(DATA_FILE, index=False)
    print(f"Saved {len(records):,} drug exposure records to {DATA_FILE}")

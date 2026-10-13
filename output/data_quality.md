# Standards and public sources

- **Data:** CMS DE-SynPUF synthetic Medicare claims in OMOP Common Data Model format, from the BigQuery public dataset `bigquery-public-data.cms_synthetic_patient_data_omop` ([CMS DE-SynPUF](https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files/cms-2008-2010-data-entrepreneurs-synthetic-public-use-file-de-synpuf)). CMS states the file has very limited value for drawing conclusions about real Medicare beneficiaries, so results demonstrate methods only.
- **OMOP standards applied:** records from the standard DRUG_EXPOSURE table; drugs identified by standard RxNorm (the US National Library of Medicine's standard drug names) Ingredient concepts; all products per ingredient found through CONCEPT_ANCESTOR; ingredient strength from DRUG_STRENGTH ([OMOP CDM](https://ohdsi.github.io/CommonDataModel/))
- **ISPOR standards applied:** adherence as defined by ISPOR ([Cramer et al., 2008](https://www.ispor.org/heor-resources/good-practices/article/medication-compliance-and-persistence-terminology-and-definitions)), measured as proportion of days covered (PDC) using public Pharmacy Quality Alliance (PQA) measure conventions ([PQA](https://www.pqaalliance.org/measures-overview))
- **Full list of sources and design choices:** see README.md

# Columns

| Column | Data type | Missing | Contents | Lineage |
| --- | --- | ---: | --- | --- |
| drug_exposure_id | int64 | 0 | OMOP drug exposure record identifier | drug_exposure.drug_exposure_id |
| person_id | int64 | 0 | Patient identifier | drug_exposure.person_id |
| drug_exposure_start_date | datetime64[ns] | 0 | Start date of the drug exposure record | drug_exposure.drug_exposure_start_date |
| days_supply | int64 | 0 | Days of medication supplied, as recorded | drug_exposure.days_supply |
| drug_concept_id | int64 | 0 | Standard drug product concept | drug_exposure.drug_concept_id |
| ingredients | object | 0 | Matched active ingredient or ingredients | RxNorm Ingredient concepts and CONCEPT_ANCESTOR; niacin requires >=500 mg |
| drug_name_simplified | object | 0 | Active ingredient name(s), regardless of dose or brand | Same as ingredients |
| medication_group | object | 0 | Statin or other lipid-lowering drug | Statin if any matched ingredient is a statin |
| is_combination | bool | 0 | Whether the product has more than one matched ingredient | True when more than one ingredient is listed |
| drug_name | object | 0 | Standard RxNorm drug product name | concept.concept_name |
| brand_name | object | 5,860,177 | Brand name when shown in the drug name | Text inside brackets in drug_name |
| age_at_exposure | int64 | 0 | Patient age at the record start date | Start year minus person.year_of_birth |
| gender | object | 0 | Patient gender | person.gender_concept_id matched to concept.concept_name |

# Dataset size and dates

- Drug exposure records: 7,989,814
- Unique patients: 1,387,622
- Record start date range: 2008-01-01 to 2010-12-31

# Records by drug

Counts use `drug_name_simplified`, so all strengths, brands, and generics of an ingredient are combined. Products containing a statin are grouped as Statin.

## Statin (6,419,111 records)

| Drug | Records |
| --- | ---: |
| simvastatin | 2,089,536 |
| lovastatin | 1,825,916 |
| atorvastatin | 1,111,991 |
| pravastatin | 799,728 |
| rosuvastatin | 258,725 |
| ezetimibe, simvastatin | 195,418 |
| fluvastatin | 110,509 |
| cerivastatin | 26,341 |
| pitavastatin | 947 |

## Other lipid-lowering (1,570,703 records)

| Drug | Records |
| --- | ---: |
| gemfibrozil | 785,638 |
| fenofibrate | 460,115 |
| colesevelam | 171,204 |
| ezetimibe | 101,171 |
| colestipol | 43,381 |
| niacin | 9,194 |

# Data quality

## Days supply

- Missing: 0 records (0.00%)
- Zero or negative: 18,719 records (0.23%)
- Positive values: median 30 days; 5th percentile 30; 95th percentile 90; maximum 90
- Above 90 days: 0 records
- Above 180 days: 0 records
- Above 365 days: 0 records

**Handling in the adherence analysis:**

- Records with missing, zero, or negative days supply are excluded, because the days they cover cannot be determined (analyst choice).
- Records with long days supply are kept as recorded. PDC counts only days inside the measurement period, so a long supply cannot raise PDC above 100% (analyst choice; no published standard sets a maximum).

## Multiple records for the same patient, product, and start date

- Combinations with more than one record: 1,472
- Records involved: 2,944 (0.04% of all records)

**Handling in the adherence analysis:** records are kept as recorded. PDC counts each covered day once, so records covering the same days are not double counted (analyst choice).

# Opportunities for future development

- **Provider details:** provider identifiers and specialties were not populated in the drug exposure records; find another way to link providers.
- **Combination products:** products containing a statin are grouped as Statin for now; combination products account for 195,418 records (2.45%) and could be handled separately later.
- **Multiple records on the same date:** validate whether multiple records for the same patient, product, and start date represent one dispensing event or separate events.
- **Continuous enrollment:** use the OMOP OBSERVATION_PERIOD table to confirm each patient is observable for the full measurement period.

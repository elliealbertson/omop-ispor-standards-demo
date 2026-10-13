# Standards and public sources

- **Data:** CMS DE-SynPUF synthetic Medicare claims in OMOP Common Data Model format, from the BigQuery public dataset `bigquery-public-data.cms_synthetic_patient_data_omop` ([CMS DE-SynPUF](https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files/cms-2008-2010-data-entrepreneurs-synthetic-public-use-file-de-synpuf)). CMS states the file has very limited value for drawing conclusions about real Medicare beneficiaries, so results demonstrate methods only.
- **OMOP standards applied:** records from the standard DRUG_EXPOSURE table; drugs identified by standard RxNorm (the US National Library of Medicine's standard drug names) Ingredient concepts; all products per ingredient found through CONCEPT_ANCESTOR; ingredient strength from DRUG_STRENGTH ([OMOP CDM](https://ohdsi.github.io/CommonDataModel/))
- **ISPOR standards applied:** adherence as defined by ISPOR ([Cramer et al., 2008](https://www.ispor.org/heor-resources/good-practices/article/medication-compliance-and-persistence-terminology-and-definitions)), measured as proportion of days covered (PDC) using public Pharmacy Quality Alliance (PQA) measure conventions ([PQA](https://www.pqaalliance.org/measures-overview))
- **Full list of sources and design choices:** see README.md

# Adherence: proportion of days covered (PDC)

**Definition (ISPOR):** adherence is the extent to which a patient takes a medication according to the prescribed timing, dose, and frequency ([Cramer et al., 2008](https://www.ispor.org/heor-resources/good-practices/article/medication-compliance-and-persistence-terminology-and-definitions)). Pharmacy records serve as a proxy: if a patient has medication on hand on a given day, the day counts as covered.

**Measure:** PDC = days with a statin on hand during the measurement period / days in the measurement period. PDC ranges from 0% to 100%.

**Conventions from PQA public measure summaries** ([PQA](https://www.pqaalliance.org/measures-overview)):

- Measurement period: each calendar year, starting at the patient's first statin record in that year
- At least 2 statin records on different dates in the year
- First statin record at least 91 days before the end of the year
- Age 18 or older
- Adherent: PDC of 80% or higher

**Additional choices (analyst choice):**

- All statins count together; combination products containing a statin count as statin.
- Overlapping supply is not shifted forward; each covered day is counted once.
- Only records starting within the year count toward that year.
- Continuous enrollment during the year is not checked (see README for future development).
- Results are descriptive only. With synthetic data, differences between groups are not real-world findings.

Statin records excluded for missing, zero, or negative days supply: 15,037

## By year

| Year | Patients | Average PDC | Median PDC | Share with PDC >= 80% |
| --- | --- | --- | --- | --- |
| 2008 | 587,163 | 41.6% | 38.7% | 3.8% |
| 2009 | 629,972 | 40.2% | 37.4% | 3.3% |
| 2010 | 415,378 | 35.8% | 33.3% | 1.9% |

## By first statin in the year (all years combined)

| First statin | Patients | Average PDC | Median PDC | Share with PDC >= 80% |
| --- | --- | --- | --- | --- |
| atorvastatin | 283,147 | 39.6% | 36.6% | 3.1% |
| cerivastatin | 6,780 | 39.6% | 36.7% | 3.0% |
| ezetimibe, simvastatin | 50,312 | 39.6% | 36.6% | 3.1% |
| fluvastatin | 28,220 | 39.8% | 36.8% | 3.1% |
| lovastatin | 465,342 | 39.7% | 36.7% | 3.2% |
| pitavastatin | 237 | 37.7% | 34.9% | 3.0% |
| pravastatin | 202,586 | 39.4% | 36.4% | 3.1% |
| rosuvastatin | 66,090 | 39.6% | 36.7% | 3.0% |
| simvastatin | 529,799 | 39.6% | 36.6% | 3.1% |

## By age group (all years combined)

| Age group | Patients | Average PDC | Median PDC | Share with PDC >= 80% |
| --- | --- | --- | --- | --- |
| 18-64 | 282,011 | 39.5% | 36.5% | 3.0% |
| 65-74 | 591,764 | 39.8% | 36.8% | 3.2% |
| 75-84 | 495,335 | 39.6% | 36.7% | 3.1% |
| 85+ | 263,403 | 39.2% | 36.2% | 3.0% |

## By gender (all years combined)

| Gender | Patients | Average PDC | Median PDC | Share with PDC >= 80% |
| --- | --- | --- | --- | --- |
| FEMALE | 997,385 | 39.6% | 36.6% | 3.1% |
| MALE | 635,128 | 39.6% | 36.6% | 3.1% |

Groups with fewer than 30 patients are not shown.

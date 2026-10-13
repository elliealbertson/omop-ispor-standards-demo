# OMOP and ISPOR Industry Standards: Proof of Concept with Public Synthetic Drug Data

Work in progress (WIP) proof of concept (POC).

## Purpose

This project tests how two publicly available industry standards apply to the analysis of pharmacy data:

- **OMOP Common Data Model (CDM):** a public standard for structuring health data and coding it with standard vocabularies, maintained by the Observational Health Data Sciences and Informatics (OHDSI) open-science community.
- **ISPOR good practices:** public standards from ISPOR—The Professional Society for Health Economics and Outcomes Research, including a standard definition of medication adherence.

The project works as an inventory. Each section below lists what a standard specifies, then where this project applies it. The example use case measures medication adherence (whether patients take a medication on the prescribed schedule), using public synthetic claims data chosen because it is already in OMOP format.

## Key Terms

- **Drug exposure record:** one record in the OMOP DRUG_EXPOSURE table. In this dataset, each record comes from a CMS prescription drug event and includes a start date and days supply. ([OMOP CDM](https://ohdsi.github.io/CommonDataModel/))
- **RxNorm:** the US National Library of Medicine's standard naming system for prescription drugs. It gives each drug ingredient and product one standard name and code, and links the names used by other drug vocabularies. OMOP uses RxNorm as its standard drug vocabulary. ([RxNorm](https://www.nlm.nih.gov/research/umls/rxnorm/index.html))
- **Indication:** a disease or condition a drug is approved to treat or prevent. FDA regulations require every prescription drug label to include an "Indications and Usage" section listing them. ([21 CFR 201.57](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-C/part-201/subpart-B/section-201.57))
- **Adherence:** the extent to which a patient takes a medication according to the prescribed timing, dose, and frequency (ISPOR definition; see ISPOR Standards).
- **Proportion of days covered (PDC):** the share of days in a measurement period on which a patient has the medication on hand, based on pharmacy records. A common measure of adherence (see ISPOR Standards).

## Public Sources at a Glance

Everything in this project comes from publicly available data, standards, and information.

| Component | Public source | Link |
|---|---|---|
| Data | CMS 2008–2010 Data Entrepreneurs' Synthetic Public Use File (DE-SynPUF), OMOP version, hosted as a BigQuery public dataset | [CMS DE-SynPUF](https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files/cms-2008-2010-data-entrepreneurs-synthetic-public-use-file-de-synpuf) |
| Data standard | OMOP Common Data Model | [OMOP CDM documentation](https://ohdsi.github.io/CommonDataModel/) |
| Vocabulary standard | OHDSI Standardized Vocabularies (drugs coded in RxNorm) | [The Book of OHDSI: Standardized Vocabularies](https://book.ohdsi.org/StandardizedVocabularies.html) |
| Adherence definition | ISPOR terminology and definitions report (Cramer et al., 2008) | [ISPOR good practices report](https://www.ispor.org/heor-resources/good-practices/article/medication-compliance-and-persistence-terminology-and-definitions) |
| Study design checklist | ISPOR checklist for retrospective database studies (Peterson et al., 2007) | [ISPOR good practices report](https://ispor.org/heor-resources/good-practices/article/checklist-for-medication-compliance-and-persistence-studies-using-retrospective-databases) |
| Adherence measure conventions | Pharmacy Quality Alliance (PQA) public measure summaries | [PQA measures overview](https://www.pqaalliance.org/measures-overview) |
| Drug details | U.S. Food and Drug Administration (FDA) | [Drugs@FDA](https://www.accessdata.fda.gov/scripts/cder/daf/), [Orange Book](https://www.accessdata.fda.gov/scripts/cder/ob/), [DailyMed](https://dailymed.nlm.nih.gov/) |
| Drug labeling terms | FDA labeling regulations | [21 CFR 201.57](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-C/part-201/subpart-B/section-201.57) |
| Diagnosis codes | CDC National Center for Health Statistics (NCHS) | [ICD-9-CM](https://www.cdc.gov/nchs/icd/icd9cm.htm), [ICD-10-CM](https://www.cdc.gov/nchs/icd/icd-10-cm/) |
| Condition background | Centers for Disease Control and Prevention (CDC) | [High Cholesterol Facts](https://www.cdc.gov/cholesterol/data-research/facts-stats/index.html) |

## Data

- **Source:** CMS DE-SynPUF, a public file of synthetic Medicare beneficiaries and their claims from 2008 to 2010, including prescription drug events. No record represents a real person.
- **Why this dataset:** It is public, fully synthetic, and already converted to the OMOP Common Data Model, so OMOP standards apply to it directly. In the OMOP version, prescription drug events are stored as drug exposure records.
- **Location:** `bigquery-public-data.cms_synthetic_patient_data_omop` (Google BigQuery public datasets).
- **Limitation:** CMS describes the file as having "very limited inferential research value" for drawing conclusions about Medicare beneficiaries. Results here demonstrate methods, not real-world findings.
- **Documentation:** [CMS DE-SynPUF overview](https://www.cms.gov/data-research/statistics-trends-and-reports/medicare-claims-synthetic-public-use-files/cms-2008-2010-data-entrepreneurs-synthetic-public-use-file-de-synpuf), [CMS data users guide (PDF)](https://www.cms.gov/Research-Statistics-Data-and-Systems/Downloadable-Public-Use-Files/SynPUFs/Downloads/SynPUF_DUG.pdf)

## OMOP Standards

Sources: [OMOP CDM documentation](https://ohdsi.github.io/CommonDataModel/), [The Book of OHDSI: Standardized Vocabularies](https://book.ohdsi.org/StandardizedVocabularies.html)

| What the OMOP standard specifies | How this project applies it | Status |
|---|---|---|
| Health data is stored in standard tables with standard columns (e.g., PERSON, DRUG_EXPOSURE). | Drug exposure records come from DRUG_EXPOSURE; age and gender come from PERSON. | Applied (omop_query.py) |
| Each record is coded to a standard concept in the Standardized Vocabularies. Drugs use RxNorm (the US standard drug naming system). | Each drug is identified by its standard RxNorm concept of class "Ingredient." | Applied (omop_query.py) |
| CONCEPT_ANCESTOR links each concept to everything beneath it in the hierarchy, so an ingredient links to every product that contains it. | All products for each ingredient (every strength, form, brand, and generic) are found through CONCEPT_ANCESTOR, with no hand-typed product code lists. | Applied (omop_query.py) |
| DRUG_STRENGTH records the amount of each ingredient in each product. | Niacin products are limited to prescription strength (500 mg or more). | Applied (omop_query.py) |

## ISPOR Standards

### Adherence Definition (Cramer et al., 2008)

Source: [ISPOR terminology and definitions report, Value in Health 2008;11(1):44–47](https://www.ispor.org/heor-resources/good-practices/article/medication-compliance-and-persistence-terminology-and-definitions)

| What the ISPOR standard specifies | How this project applies it | Status |
|---|---|---|
| Adherence (synonym: compliance) is the extent to which a patient follows "the prescribed interval, and dose of a dosing regimen." In plain terms: does the patient take the medication on schedule and at the expected dose? | Measured with pharmacy records as a proxy, as proportion of days covered (PDC) in each calendar year: a day counts as covered when the patient has medication on hand. Measure conventions follow PQA public summaries (see below). | Applied (ispor_adherence.py) |

### Study Design Checklist (Peterson et al., 2007)

Source: [ISPOR checklist for retrospective database studies, Value in Health 2007;10(1):3–12](https://ispor.org/heor-resources/good-practices/article/checklist-for-medication-compliance-and-persistence-studies-using-retrospective-databases) (open access)

The checklist is an ISPOR consensus list of items to include or consider when measuring medication adherence in retrospective databases such as claims data. It covers data sources, measurement of adherence, reporting of results, and conflicts of interest. Following it, this project states each design choice and its basis in one place:

| Design choice | Setting | Basis |
|---|---|---|
| Data source | CMS DE-SynPUF in OMOP format | Public synthetic data (see Data) |
| Unit of data | One OMOP drug exposure record, as recorded | OMOP DRUG_EXPOSURE table |
| Adherence measure | Proportion of days covered (PDC) | PQA public measure summaries |
| Measurement period | Each calendar year, from the patient's first statin record in that year | PQA public measure summaries |
| Minimum statin records | At least 2 on different dates in the year | PQA public measure summaries |
| Timing of first statin record | At least 91 days before the end of the year | PQA public measure summaries |
| Minimum age | 18 at the first statin record in the year | PQA public measure summaries |
| Adherence threshold | PDC of 80% or more | PQA public measure summaries |
| Missing, zero, or negative days supply | Reported in data_quality.py; record excluded from PDC | Analyst choice: covered days cannot be determined |
| Long days supply | Reported in data_quality.py; kept as recorded | Analyst choice: PDC counts only days in the measurement period |
| Overlapping supply | Each covered day counted once; not shifted forward | Analyst choice |
| Multiple records for the same patient, product, and date | Reported in data_quality.py; kept as recorded, with each covered day counted once | Analyst choice |
| Combination products containing a statin | Counted as statin | Analyst choice |
| Niacin products | 500 mg or more per product | Analyst choice, to exclude vitamin products |
| Groups with fewer than 30 patients | Not shown in results by group | Analyst choice |

### Related Public Measure Convention (PQA)

The Pharmacy Quality Alliance (PQA) publicly summarizes its adherence measures, including statins: adults 18 and older, at least two statin prescriptions on different dates, a first prescription at least 91 days before the end of the measurement period, and adherence defined as a proportion of days covered (PDC) of 80% or more. This project uses only those public summaries. It is not a certified implementation of any PQA measure, and the full licensed PQA specifications were not used. Sources: [PQA measures overview](https://www.pqaalliance.org/measures-overview), [PQA public FAQ (PDF)](https://www.pqaalliance.org/assets/Measures/QRS%20PDC%20FAQs%20080818.pdf)

## Project Files

| File | Purpose |
|---|---|
| `main.py` | Runs the three modules below in order |
| `modules/config.py` | All settings in one place, each labeled with its basis |
| `modules/omop_query.py` | Pulls drug exposure records from the public BigQuery dataset using OMOP standard vocabularies, without merging or editing records |
| `modules/data_quality.py` | Profiles the records and reports data quality; writes `output/data_quality.md` |
| `modules/ispor_adherence.py` | Measures statin adherence as proportion of days covered (PDC), following ISPOR and PQA public conventions; writes `output/adherence_results.md` |

Run `python main.py` from the repo root to reproduce all outputs.

## Example Use Case: Therapeutic Area

Condition and drug details below come from the public sources listed in each section.

### Condition: Hyperlipidemia

- **What it is:** High cholesterol or other fats (lipids) in the blood, which build up in arteries and raise the risk of heart attack and stroke. It usually has no symptoms until complications occur.
- **How common:** About 86 million US adults age 20 or older have total cholesterol above 200 mg/dL, and about 10% of adults had total cholesterol above 240 mg/dL in 2017–2020. About 7% of US children and adolescents ages 6 to 19 have high total cholesterol.
- **Diagnosis codes:** ICD-9-CM 272.0–272.4 (used in US claims before October 2015, including the 2008–2010 data in this project); ICD-10-CM E78.0–E78.5 (used from October 2015 onward).
- **Sources:** [CDC High Cholesterol Facts](https://www.cdc.gov/cholesterol/data-research/facts-stats/index.html), [CDC NCHS ICD-9-CM](https://www.cdc.gov/nchs/icd/icd9cm.htm), [CDC NCHS ICD-10-CM](https://www.cdc.gov/nchs/icd/icd-10-cm/)

### Sources of Drug Details

- **FDA approval dates, market withdrawal dates, and generic availability:** [Drugs@FDA](https://www.accessdata.fda.gov/scripts/cder/daf/) and the [FDA Orange Book](https://www.accessdata.fda.gov/scripts/cder/ob/)
- **Indications (conditions a drug is approved to treat or prevent), route, and frequency:** FDA-approved prescribing information, available through [Drugs@FDA](https://www.accessdata.fda.gov/scripts/cder/daf/) and [DailyMed](https://dailymed.nlm.nih.gov/). FDA requires an "Indications and Usage" section in every prescription drug label ([21 CFR 201.57](https://www.ecfr.gov/current/title-21/chapter-I/subchapter-C/part-201/subpart-B/section-201.57)).
- **Drug names and ingredients in the data:** RxNorm (the US standard drug naming system), through the OMOP Standardized Vocabularies ([RxNorm at the National Library of Medicine](https://www.nlm.nih.gov/research/umls/rxnorm/index.html))

### Statins (Adherence Analysis)

All statins are taken by mouth, typically once daily (with some exceptions). All are indicated at least for high cholesterol, sometimes for high cholesterol as the sole indication and sometimes for other indications as well.

| Brand | Active Ingredient | Generic Available | Date FDA Approved (YYYY-MM-DD) | Date Withdrawn from Market (YYYY-MM-DD) | Indications | Route and Frequency |
|---|---|---|---|---|---|---|
| Mevacor | Lovastatin | Yes | 1987-08-31 | N/A | Hyperlipidemia, Heart attack, Coronary heart disease | Oral, once or twice daily |
| Pravachol | Pravastatin | Yes | 1991-10-31 | N/A | Hyperlipidemia, Heart attack, Stroke | Oral, once daily |
| Zocor | Simvastatin | Yes | 1991-12-23 | N/A | Hyperlipidemia, Heart attack, Stroke | Oral, once daily |
| Lescol | Fluvastatin | Yes | 1993-12-31 | N/A | Hyperlipidemia, Coronary heart disease | Oral, once or twice daily |
| Lipitor | Atorvastatin | Yes | 1996-12-17 | N/A | Hyperlipidemia, Heart attack, Stroke | Oral, once daily |
| Baycol | Cerivastatin | N/A | 1997-06-26 | 2001-08-08 | Hyperlipidemia | Oral, once daily |
| Crestor | Rosuvastatin | Yes | 2003-08-12 | N/A | Hyperlipidemia, Heart attack, Stroke, Coronary heart disease | Oral, once daily |
| Livalo | Pitavastatin | Yes | 2009-08-03 | N/A | Hyperlipidemia | Oral, once daily |

### Other Lipid-Lowering Drugs (Context on Similar Therapies)

| Brand | Active Ingredient | Generic Available | Date FDA Approved (YYYY-MM-DD) | Date Withdrawn from Market (YYYY-MM-DD) | Indications | Route and Frequency |
|---|---|---|---|---|---|---|
| Lopid | Gemfibrozil | Yes | 1981-12-21 | N/A | Hypertriglyceridemia, Coronary heart disease | Oral, twice daily |
| Tricor | Fenofibrate | Yes | 1993-12-31 | N/A | Hyperlipidemia, Hypertriglyceridemia | Oral, once daily |
| Niaspan | Niacin extended-release | Yes | 1997-07-28 | N/A | Hyperlipidemia, Hypertriglyceridemia, Heart attack, Coronary heart disease | Oral, once daily |
| Welchol | Colesevelam | Yes | 2000-05-26 | N/A | Hyperlipidemia, Type 2 diabetes | Oral, one to two times daily |
| Zetia | Ezetimibe | Yes | 2002-10-25 | N/A | Hyperlipidemia, Sitosterolemia | Oral, once daily |
| Praluent | Alirocumab | No | 2015-07-24 | N/A | Hyperlipidemia, Heart attack, Stroke | Injection, every 2 or 4 weeks |
| Repatha | Evolocumab | No | 2015-08-27 | N/A | Hyperlipidemia, Heart attack, Stroke | Injection, every 2 weeks or monthly |
| Nexletol | Bempedoic acid | No | 2020-02-21 | N/A | Hyperlipidemia, Heart attack | Oral, once daily |
| Leqvio | Inclisiran | No | 2021-12-22 | N/A | Hyperlipidemia | Injection in clinic, every 6 months after first two doses |

The search list in config.py also includes fenofibric acid, cholestyramine, and colestipol, which are not shown in this table.

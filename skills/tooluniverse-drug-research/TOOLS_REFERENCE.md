# Drug Research Tools Reference

Complete reference for 50+ tools used in drug research, organized by use case.

---

## Quick Reference: Tools by Use Case

| Use Case | Primary Tool | Fallback |
|----------|--------------|----------|
| Name → CID | `PubChem_get_CID_by_compound_name` | `ChEMBL_search_compounds` |
| SMILES → CID | `PubChem_get_CID_by_SMILES` | - |
| Properties | `PubChem_get_compound_properties_by_CID` | ADMET-AI |
| 2D Image | `PubChem_get_compound_2D_image_by_CID` | - |
| Drug-likeness | `ADMETAI_predict_physicochemical_properties` | PubChem properties |
| Targets | `ChEMBL_get_target_by_chemblid` | `DGIdb_get_drug_info` |
| Bioactivity | `ChEMBL_get_bioactivity_by_chemblid` | `PubChem_get_bioactivity_summary_by_CID` |
| Absorption | `ADMETAI_predict_bioavailability` | Literature |
| BBB | `ADMETAI_predict_BBB_penetrance` | Literature |
| CYP | `ADMETAI_predict_CYP_interactions` | PharmGKB |
| Toxicity | `ADMETAI_predict_toxicity` | FAERS |
| Trials | `search_clinical_trials` | - |
| Trial outcomes | `extract_clinical_trial_outcomes` | - |
| Trial AEs | `extract_clinical_trial_adverse_events` | - |
| FAERS | `FAERS_count_reactions_by_drug_event` | - |
| Label | `DailyMed_search_spls` | `PubChem_get_drug_label_info_by_CID` |
| PGx Drug | `PharmGKB_search_drugs` | - |
| CPIC | `PharmGKB_get_dosing_guidelines` | - |
| Literature | `PubMed_search_articles` | `EuropePMC_search_articles` |
| Similar compounds | `PubChem_search_compounds_by_similarity` | ChEMBL |
| Patents | `PubChem_get_associated_patents_by_CID` | - |

---

## Compound Identity & Chemistry

### PubChem Tools
| Tool | Purpose | Key Output |
|------|---------|------------|
| `PubChem_get_CID_by_compound_name` | Name → CID | CID, canonical name |
| `PubChem_get_CID_by_SMILES` | Structure → CID | CID |
| `PubChem_get_compound_properties_by_CID` | Molecular properties | MW, formula, XLogP, TPSA, HBD, HBA |
| `PubChem_get_compound_2D_image_by_CID` | Structure image | PNG image |
| `PubChem_get_bioactivity_summary_by_CID` | Activity overview | Active/inactive counts, assay types |
| `PubChem_get_drug_label_info_by_CID` | FDA label info | Indications, warnings, dosing |
| `PubChem_get_associated_patents_by_CID` | Patent data | Patent numbers, titles |
| `PubChem_search_compounds_by_similarity` | Find analogs | Similar CIDs with scores |
| `PubChem_search_compounds_by_substructure` | Substructure search | Matching CIDs |

### ChEMBL Tools
| Tool | Purpose | Key Output |
|------|---------|------------|
| `ChEMBL_search_compounds` | Name/structure search | ChEMBL ID, pref_name |
| `ChEMBL_get_compound_by_chemblid` | Compound details | SMILES, properties, synonyms |
| `ChEMBL_get_bioactivity_by_chemblid` | Activity data | IC50, Ki, EC50 values |
| `ChEMBL_get_target_by_chemblid` | Protein targets | Target ChEMBL IDs, UniProt |
| `ChEMBL_get_assays_by_chemblid` | Assay metadata | Assay types, organisms |
| `ChEMBL_search_targets` | Target search | Target ChEMBL IDs |

---

## ADMET Predictions

All ADMET-AI tools require SMILES input in list format: `smiles=["CC(=O)Oc1ccccc1C(=O)O"]`

### Physicochemical
| Tool | Endpoints |
|------|-----------|
| `ADMETAI_predict_physicochemical_properties` | MW, logP, HBD, HBA, Lipinski, QED, stereo_centers, TPSA |
| `ADMETAI_predict_solubility_lipophilicity_hydration` | Solubility_AqSolDB, Lipophilicity_AstraZeneca, HydrationFreeEnergy |

### Absorption
| Tool | Endpoints |
|------|-----------|
| `ADMETAI_predict_bioavailability` | Bioavailability_Ma, HIA_Hou, PAMPA_NCATS, Caco2_Wang, Pgp_Broccatelli |

### Distribution
| Tool | Endpoints |
|------|-----------|
| `ADMETAI_predict_BBB_penetrance` | BBB_Martins (0-1 probability) |
| `ADMETAI_predict_clearance_distribution` | VDss_Lombardo, PPBR_AZ |

### Metabolism
| Tool | Endpoints |
|------|-----------|
| `ADMETAI_predict_CYP_interactions` | CYP1A2_Veith, CYP2C9_Veith/Substrate, CYP2C19_Veith, CYP2D6_Veith/Substrate, CYP3A4_Veith/Substrate |

### Excretion
| Tool | Endpoints |
|------|-----------|
| `ADMETAI_predict_clearance_distribution` | Clearance_Hepatocyte_AZ, Clearance_Microsome_AZ, Half_Life_Obach |

### Toxicity
| Tool | Endpoints |
|------|-----------|
| `ADMETAI_predict_toxicity` | AMES, Carcinogens_Lagunin, ClinTox, DILI, LD50_Zhu, Skin_Reaction, hERG |
| `ADMETAI_predict_nuclear_receptor_activity` | NR-AR, NR-AR-LBD, NR-AhR, NR-Aromatase, NR-ER, NR-ER-LBD, NR-PPAR-gamma |
| `ADMETAI_predict_stress_response` | SR-ARE, SR-ATAD5, SR-HSE, SR-MMP, SR-p53 |

---

## Drug-Gene Interactions

### DGIdb Tools
| Tool | Purpose | Key Output |
|------|---------|------------|
| `DGIdb_get_drug_gene_interactions` | Drug → gene interactions | Gene names, interaction types, sources |
| `DGIdb_get_gene_druggability` | Gene druggability categories | Kinase, GPCR, ion channel, etc. |
| `DGIdb_get_drug_info` | Drug targets and details | Target genes, interaction types |
| `DGIdb_get_gene_info` | Gene details | Aliases, categories |

---

## Clinical Trials (ClinicalTrials.gov)

### Search & Overview
| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `search_clinical_trials` | Search trials | condition, intervention, query_term, pageSize |
| `get_clinical_trial_descriptions` | Trial titles, summaries | nct_ids, description_type (brief/full) |
| `get_clinical_trial_status_and_dates` | Status, dates | nct_ids |

### Details
| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `get_clinical_trial_conditions_and_interventions` | Conditions, arms | nct_ids |
| `get_clinical_trial_eligibility_criteria` | Inclusion/exclusion | nct_ids |
| `get_clinical_trial_locations` | Trial sites | nct_ids |
| `get_clinical_trial_outcome_measures` | Primary/secondary endpoints | nct_ids, outcome_measures |
| `get_clinical_trial_references` | Related publications | nct_ids |

### Results Extraction
| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `extract_clinical_trial_outcomes` | Efficacy results | nct_ids, outcome_measure |
| `extract_clinical_trial_adverse_events` | Safety data | nct_ids, organ_systems, adverse_event_type |

---

## Adverse Events (FDA FAERS)

### Single Drug Analysis
| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `FAERS_count_reactions_by_drug_event` | AEs by MedDRA term | medicinalproduct, filters |
| `FAERS_count_seriousness_by_drug_event` | Serious vs non-serious | medicinalproduct |
| `FAERS_count_outcomes_by_drug_event` | Recovered, fatal, etc. | medicinalproduct |
| `FAERS_count_death_related_by_drug` | Fatal outcomes | medicinalproduct |
| `FAERS_count_patient_age_distribution` | Age groups | medicinalproduct |
| `FAERS_count_drug_routes_by_event` | Administration routes | medicinalproduct |
| `FAERS_count_country_by_drug_event` | Country distribution | medicinalproduct |

### Multi-Drug Analysis
| Tool | Purpose |
|------|---------|
| `FAERS_count_additive_adverse_reactions` | Combined AEs across drugs |
| `FAERS_count_additive_seriousness_classification` | Combined seriousness |
| `FAERS_count_additive_reaction_outcomes` | Combined outcomes |

### Filter Options (FAERS)
| Filter | Values |
|--------|--------|
| patientsex | "Male", "Female" |
| patientagegroup | "Neonate", "Infant", "Child", "Adolescent", "Adult", "Elderly" |
| occurcountry | ISO2 code (e.g., "US", "GB") |
| serious | "Yes", "No" |
| seriousnessdeath | "Yes", "No" |

---

## Drug Labeling

### DailyMed Tools
| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `DailyMed_search_spls` | Search labels | drug_name, ndc, rxcui, setid |
| `DailyMed_get_spl_by_setid` | Full label content | setid, format |

---

## Pharmacogenomics (PharmGKB)

| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `PharmGKB_search_drugs` | Search drugs | query |
| `PharmGKB_get_drug_details` | Drug cross-references | drug_id (PA...) |
| `PharmGKB_search_genes` | Search pharmacogenes | query |
| `PharmGKB_get_gene_details` | Gene details | gene_id |
| `PharmGKB_get_clinical_annotations` | Gene-drug associations | annotation_id or gene_id |
| `PharmGKB_get_dosing_guidelines` | CPIC/DPWG guidelines | guideline_id or gene |
| `PharmGKB_search_variants` | Search by rsID | query |

---

## Literature

### Search Tools
| Tool | Purpose | Key Parameters |
|------|---------|----------------|
| `PubMed_search_articles` | Primary biomedical | query, limit |
| `PMC_search_papers` | Full-text | query, limit |
| `EuropePMC_search_articles` | European coverage | query, limit |
| `openalex_literature_search` | Broad academic | query, limit |
| `Crossref_search_works` | DOI-based | query, limit |
| `SemanticScholar_search_papers` | AI-ranked | query, limit |
| `BioRxiv_search_preprints` | Biology preprints | query, limit |
| `MedRxiv_search_preprints` | Medical preprints | query, limit |

### Citation Tools
| Tool | Purpose |
|------|---------|
| `PubMed_get_cited_by` | Forward citations |
| `PubMed_get_related` | Related articles |
| `EuropePMC_get_citations` | Citations (fallback) |
| `EuropePMC_get_references` | Reference list |

---

## Tool Chains by Research Path

### PATH 1: Identity Resolution
```
PubChem_get_CID_by_compound_name
  ↓
ChEMBL_search_compounds
  ↓
DailyMed_search_spls
  ↓
PharmGKB_search_drugs
```

### PATH 2: Chemistry & Drug-likeness
```
PubChem_get_compound_properties_by_CID
  ↓
ADMETAI_predict_physicochemical_properties
  ↓
ADMETAI_predict_solubility_lipophilicity_hydration
```

### PATH 3: Targets & Bioactivity
```
ChEMBL_get_bioactivity_by_chemblid
  ↓
ChEMBL_get_target_by_chemblid
  ↓
DGIdb_get_drug_info
  ↓
PubChem_get_bioactivity_summary_by_CID
```

### PATH 4: ADMET Profile
```
ADMETAI_predict_bioavailability
  ↓
ADMETAI_predict_BBB_penetrance
  ↓
ADMETAI_predict_CYP_interactions
  ↓
ADMETAI_predict_clearance_distribution
  ↓
ADMETAI_predict_toxicity
```

### PATH 5: Clinical Trials
```
search_clinical_trials
  ↓
get_clinical_trial_conditions_and_interventions
  ↓
extract_clinical_trial_outcomes
  ↓
extract_clinical_trial_adverse_events
```

### PATH 6: Post-Marketing Safety
```
FAERS_count_reactions_by_drug_event
  ↓
FAERS_count_seriousness_by_drug_event
  ↓
FAERS_count_outcomes_by_drug_event
  ↓
FAERS_count_death_related_by_drug
  ↓
FAERS_count_patient_age_distribution
```

### PATH 7: Pharmacogenomics
```
PharmGKB_search_drugs
  ↓
PharmGKB_get_drug_details
  ↓
PharmGKB_get_clinical_annotations (for each gene)
  ↓
PharmGKB_get_dosing_guidelines
```

### PATH 8: Literature
```
PubMed_search_articles (total count)
  ↓
PubMed_search_articles (recent papers)
  ↓
PubMed_search_articles (drug-focused)
  ↓
PubMed_get_cited_by (for key papers)
```

---

## Fallback Chains

| Primary | Fallback 1 | Fallback 2 |
|---------|------------|------------|
| `PubChem_get_CID_by_compound_name` | `ChEMBL_search_compounds` | Manual SMILES search |
| `ChEMBL_get_bioactivity_by_chemblid` | `PubChem_get_bioactivity_summary_by_CID` | Literature search |
| `DailyMed_search_spls` | `PubChem_get_drug_label_info_by_CID` | FDA Orange Book |
| `PharmGKB_get_dosing_guidelines` | Note "No guideline" | Literature search |
| `FAERS_count_reactions_by_drug_event` | Note "FAERS unavailable" | Trial AE data |
| `ADMETAI_*` | Note "Predictions unavailable" | Literature values |
| `PubMed_search_articles` | `EuropePMC_search_articles` | `openalex_literature_search` |

---

## Rate Limiting & Best Practices

| Database | Notes |
|----------|-------|
| PubChem | Robust, no strict limits; batch when possible |
| ChEMBL | May timeout on large bioactivity queries |
| ClinicalTrials.gov | Paginate for >100 results; use pageToken |
| FAERS | Can be slow; use minimal filters; avoid over-restriction |
| PharmGKB | Generally fast |
| ADMET-AI | Local computation; batch SMILES in single call |
| PubMed | 3 requests/second limit; use limit parameter |

---

## Input Format Requirements

### SMILES
```python
# ADMET-AI tools require list format
smiles = ["CC(=O)Oc1ccccc1C(=O)O"]  # List, not string
```

### Drug Names (FAERS)
```python
# Use uppercase, match FDA labeling
medicinalproduct = "METFORMIN"  # Not "metformin"
```

### NCT IDs
```python
# List format for batch queries
nct_ids = ["NCT01234567", "NCT02345678"]
```

### ChEMBL IDs
```python
# Full ID format
chembl_id = "CHEMBL1431"  # Not "1431"
```

### PharmGKB IDs
```python
# PA prefix for drugs
drug_id = "PA450657"  # Not "450657"
```

---
name: tooluniverse-drug-repurposing
description: Identify drug repurposing candidates using ToolUniverse for target-based, compound-based, and disease-driven strategies. Searches existing drugs for new therapeutic indications by analyzing targets, bioactivity, safety profiles, and literature evidence. Use when exploring drug repurposing opportunities, finding new indications for approved drugs, or when users mention drug repositioning, off-label uses, or therapeutic alternatives.
---

# Drug Repurposing with ToolUniverse

Systematically identify and evaluate drug repurposing candidates using multiple computational strategies.

**IMPORTANT**: Always use English terms in tool calls. Respond in the user's language.

---

## Core Strategies

1. **Target-Based**: Disease targets -> Find drugs that modulate those targets
2. **Compound-Based**: Approved drugs -> Find new disease indications
3. **Disease-Driven**: Disease -> Targets -> Match to existing drugs

---

## Workflow Overview

```
Phase 1: Disease & Target Analysis
  Get disease info (OpenTargets), find associated targets, get target details

Phase 2: Drug Discovery
  Search DrugBank, DGIdb, ChEMBL for drugs targeting disease-associated genes
  Get drug details, indications, pharmacology

Phase 3: Safety & Feasibility Assessment
  FDA warnings, FAERS adverse events, drug interactions, ADMET predictions

Phase 4: Literature Evidence
  PubMed, Europe PMC, clinical trials for existing evidence

Phase 5: Scoring & Ranking
  Composite score: target association + safety + literature + drug properties
```

See: PROCEDURES.md for detailed step-by-step procedures and code patterns.

---

## Quick Start

```python
from tooluniverse import ToolUniverse
tu = ToolUniverse()
tu.load_tools()

# Step 1: Get disease targets
disease_info = tu.tools.OpenTargets_get_disease_id_description_by_name(diseaseName="rheumatoid arthritis")
# Response nests ID at data.search.hits[0].id
disease_id = disease_info['data']['search']['hits'][0]['id']
targets = tu.tools.OpenTargets_get_associated_targets_by_disease_efoId(efoId=disease_id, limit=10)

# Step 2: Find drugs for each target
# Response nests targets at data.disease.associatedTargets.rows
rows = targets['data']['disease']['associatedTargets']['rows']
for target in rows[:5]:
    gene = target['target']['approvedSymbol']
    drugs = tu.tools.DGIdb_get_drug_gene_interactions(genes=[gene])
```

---

## Key ToolUniverse Tools

**Disease & Target**:
- `OpenTargets_get_disease_id_description_by_name` - Disease lookup
- `OpenTargets_get_associated_targets_by_disease_efoId` - Disease targets
- `UniProt_get_entry_by_accession` - Protein details

**Drug Discovery**:
- `drugbank_get_drug_name_and_description_by_target_name` - Drugs by target
- `drugbank_get_drug_name_and_description_by_indication` - Drugs by indication
- `DGIdb_get_drug_gene_interactions` - Drug-gene interactions
- `ChEMBL_search_drugs` / `ChEMBL_get_drug_mechanisms` - Drug search and MOA

**Drug Information**:
- `drugbank_get_drug_basic_info_by_drug_name_or_id` - Basic info
- `drugbank_get_indications_by_drug_name_or_drugbank_id` - Approved indications
- `drugbank_get_pharmacology_by_drug_name_or_drugbank_id` - Pharmacology
- `drugbank_get_targets_by_drug_name_or_drugbank_id` - Drug targets

**Safety**:
- `FDA_get_warnings_and_cautions_by_drug_name` - FDA warnings
- `FAERS_search_reports_by_drug_and_reaction` - Adverse events
- `FAERS_count_death_related_by_drug` - Serious outcomes
- `drugbank_get_drug_interactions_by_drug_name_or_id` - Interactions

**Property Prediction**:
- `ADMETAI_predict_physicochemical_properties` / `ADMETAI_predict_toxicity` - ADMET and toxicity

**Pathway & Network Analysis**:
- `ReactomeAnalysis_pathway_enrichment` - Pathway enrichment for target gene sets
- `STRING_get_network` - Protein interaction networks for target validation
- `CTD_get_gene_diseases` - Curated gene-disease associations

**Literature & Clinical Trials**:
- `PubMed_search_articles` / `EuropePMC_search_articles` - Literature search
- `search_clinical_trials` - ClinicalTrials.gov search. Use `condition` for disease name. The `intervention` filter is strict and may miss trials — use `query_term` for broader drug-name matching as fallback.

> **CNS diseases note**: For neurological indications (ALS, Alzheimer's, Parkinson's), prioritize BBB-penetrant candidates. Use ChEMBL molecular properties (MW < 500, PSA < 90) as BBB proxy since `ADMETAI_predict_BBB_penetrance` may require the `tooluniverse[ml]` extra. Consider route of administration (oral preferred for patients with swallowing difficulty) and sex-specific effects from preclinical models.

---

## Scoring & Decision Framework

### Repurposing Viability Score (0-100)

| Category | Points | How to Score |
|----------|--------|-----------|
| **Target Association** | 0-40 | **40**: Target has genetic evidence in disease (GWAS, rare variants); **25**: Target is in a disease-associated pathway (Reactome, KEGG); **15**: Target is differentially expressed in disease tissue; **5**: Target shares a GO term with disease genes |
| **Safety Profile** | 0-30 | **30**: FDA-approved drug, no black box warning, established safety record; **20**: FDA-approved with manageable warnings; **10**: Phase II+ data, acceptable safety; **0**: Preclinical only or serious safety signals |
| **Literature Evidence** | 0-20 | **20**: Phase II+ trial for the new indication exists; **15**: Case reports or retrospective studies show efficacy; **10**: Preclinical in-vivo evidence (animal models); **5**: In-vitro evidence only; **0**: No prior evidence |
| **Drug Properties** | 0-10 | **10**: Oral, good bioavailability, IP available; **5**: Injectable or narrow therapeutic window; **0**: Poor PK or formulation challenges |

**Classification**:
- **80-100**: Strong candidate — proceed to clinical evaluation
- **60-79**: Promising — worth preclinical validation or retrospective study
- **40-59**: Speculative — needs significant additional evidence
- **<40**: Weak — likely not worth pursuing without new mechanistic insight

### Evidence Grading for Repurposing

| Grade | Definition | Action |
|-------|-----------|--------|
| **E1 (Clinical)** | Existing clinical trial for new indication (any phase) | High priority — check trial results |
| **E2 (Epidemiological)** | Retrospective/observational data showing benefit | Moderate priority — design prospective study |
| **E3 (Preclinical)** | Animal model evidence for new indication | Standard priority — validate mechanism |
| **E4 (Computational)** | Target overlap, network proximity, or molecular similarity only | Low priority — needs experimental validation |

### How to Interpret and Combine Results

After running Phases 1-4, synthesize by answering:

1. **Is the target validated for this disease?** Check OpenTargets association score (>0.5 = strong). Cross-reference with genetic evidence (GWAS hits, rare variant studies). If target association is only pathway-level, the repurposing hypothesis is speculative.

2. **Does the drug actually hit the target at achievable doses?** Check ChEMBL IC50/Ki values. If the drug's affinity for the new target is >10x weaker than for its original target, clinical efficacy is unlikely at safe doses.

3. **What's the safety margin?** Compare the dose needed for the new indication to the approved dose. If higher doses are needed, safety data from the original indication may not apply.

4. **Is there prior clinical evidence?** A Phase II trial for the new indication (even failed) is more informative than 100 computational predictions. Check `search_clinical_trials` first.

5. **What's the competitive landscape?** If better drugs already exist for the disease, repurposing offers little value. Check DrugBank indications for approved therapies.

---

## Best Practices

1. **Check clinical trials FIRST**: `search_clinical_trials(condition="[disease]", intervention="[drug]")` — if a trial already exists, start there
2. **Validate targets with genetics**: Genetic evidence (GWAS, rare variants) is the strongest predictor of successful drug development
3. **Safety first**: Prioritize approved drugs with known safety profiles
4. **Dose matters**: A drug that hits a disease target at 100x its approved dose is not a repurposing candidate
5. **Mechanism over correlation**: Network proximity alone is insufficient — explain WHY the drug should work
6. **Consider IP and formulation**: Generic drugs are easier to repurpose but harder to fund trials for

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Disease not found | Try synonyms or EFO ID lookup |
| No drugs for target | Check HUGO nomenclature, expand to pathway-level, try similar targets |
| Insufficient literature | Search drug class instead, check preclinical/animal studies |
| Safety data unavailable | Drug may not be US-approved, check EMA or clinical trial safety |

---

## Reference Files

- **REFERENCE.md** - Detailed reference documentation
- **EXAMPLES.md** - Sample repurposing analyses
- **PROCEDURES.md** - Step-by-step procedures with code
- **REPORT_TEMPLATE.md** - Output report template
- Related skills: disease-intelligence-gatherer, chemical-compound-retrieval, tooluniverse-sdk

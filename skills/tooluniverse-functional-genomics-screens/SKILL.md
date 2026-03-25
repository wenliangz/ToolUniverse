---
name: tooluniverse-functional-genomics-screens
description: Interpret results from CRISPR/shRNA genetic screens using DepMap essentiality data, constraint scores, pathway enrichment, protein networks, druggability assessment, and clinical evidence. Use for screen hit validation, gene essentiality analysis, DepMap exploration, functional genomics interpretation, and screen-to-target prioritization.
---

# Functional Genomics Screen Interpretation

Pipeline for validating and prioritizing hits from genetic screens (CRISPR knockout, CRISPRi, shRNA) by integrating essentiality data (DepMap), evolutionary constraint (gnomAD), pathway context (Reactome, STRING), druggability (DGIdb), and clinical evidence (CIViC, COSMIC). Transforms a list of screen hits into a ranked, actionable target list.

**Guiding principles**:
1. **Hits are hypotheses** -- screen results contain false positives and context-dependent effects; validation through orthogonal evidence is the goal
2. **Selectivity matters** -- a gene essential in all cell lines is less interesting than one essential only in the disease context
3. **Pathway over gene** -- enriched pathways are more robust than individual gene hits; always look for convergent biology
4. **Druggability is practical** -- prioritize hits that can be chemically or biologically modulated
5. **Clinical anchoring** -- connect screen hits to known disease biology via CIViC, COSMIC, and literature
6. **English-first queries** -- use English gene names in tool calls

---

## When to Use

Typical triggers:
- "Here are my CRISPR screen hits -- which ones are real?"
- "Validate these essential genes from my screen"
- "What pathways are enriched in my screen hits?"
- "Which of these hits are druggable?"
- "Check DepMap essentiality for [gene list]"
- "Prioritize screen hits for [cancer type]"
- "Are these genes selectively essential in [context]?"

**Not this skill**: For differential gene expression analysis, use `tooluniverse-rnaseq-deseq2`. For pathway enrichment of expression data, use `tooluniverse-gene-enrichment`. For single-cell analysis, use `tooluniverse-single-cell`.

---

## Core Databases

| Database | Scope | Best For |
|----------|-------|----------|
| **DepMap** | Cancer cell line essentiality (1000+ lines), drug response | Context-specific essentiality, pan-cancer vs selective dependency |
| **gnomAD** | Population genetic constraint scores | Evolutionary importance; loss-of-function intolerance |
| **STRING** | Protein-protein interaction network | Network context, functional associations |
| **Reactome** | Curated biological pathways | Pathway enrichment of hit lists |
| **DGIdb** | Drug-gene interactions and druggability | Target tractability, existing drugs/compounds |
| **CIViC** | Clinical evidence for variants/genes | Clinical relevance, therapeutic implications |
| **COSMIC** | Cancer mutation catalog | Somatic mutation frequency, oncogene/TSG classification |
| **UniProt** | Protein function annotation | Gene function, domains, subcellular localization |

---

## Workflow Overview

```
Phase 0: Input Processing
  Parse hit list, identify gene names, screen type, context
    |
Phase 1: Hit Validation (Essentiality + Constraint)
  DepMap dependency scores, gnomAD constraint, gene function
    |
Phase 2: Pathway & Network Context
  Reactome enrichment, STRING network, functional clusters
    |
Phase 3: Druggability Assessment
  DGIdb interactions, druggable gene categories
    |
Phase 4: Clinical Evidence
  CIViC variants, COSMIC mutations, disease relevance
    |
Phase 5: Literature Context
  PubMed studies on key hits
    |
Phase 6: Prioritized Report
  Ranked target list with multi-dimensional scoring
```

---

## Phase Details

### Phase 0: Input Processing

Parse the user's input to identify:
- **Gene list**: names or IDs of screen hits
- **Screen type**: CRISPR-KO, CRISPRi, CRISPRa, shRNA (affects interpretation)
- **Cell line or model**: what was screened
- **Control comparison**: positive vs negative selection, what phenotype was scored
- **Disease context**: cancer type, tissue, or condition

If the user provides a ranked list (e.g., by MAGeCK score or BAGEL BF), preserve the ranking. If unranked, all hits are treated equally in Phase 1.

### Phase 1: Hit Validation (Essentiality + Constraint)

**Objective**: Assess whether screen hits are genuine essential genes in the relevant context.

**Tools**:
- `DepMap_get_gene_dependencies` -- get CRISPR dependency scores across cell lines
  - Input: `gene_name` (gene symbol)
  - Output: dependency scores per cell line (lower = more essential; < -0.5 typically essential)
- `DepMap_search_cell_lines` -- find cell lines matching criteria
  - Input: `query` (cell line name, lineage, or disease)
  - Output: cell line metadata, lineage, disease
- `gnomad_get_gene_constraints` -- get loss-of-function constraint
  - Input: `gene_symbol`
  - Output: pLI score, LOEUF, missense constraint (may return "Service overloaded" -- treat as transient)
- `UniProt_get_function_by_accession` -- get protein function summary
  - Input: `accession` (UniProt ID)
  - Output: list of function description strings

**Workflow**:
1. For each hit gene, query DepMap for dependency scores
2. Compare dependency in the screen's cell line/lineage vs pan-cancer
3. Classify each hit:
   - **Pan-essential**: essential in >90% of lines (common essential, less interesting for therapy)
   - **Selectively essential**: essential in specific lineages or contexts (high-value therapeutic targets)
   - **Context-specific**: essential only in the screen's model (needs further validation)
4. Get gnomAD constraint: pLI > 0.9 or LOEUF < 0.35 indicates strong evolutionary constraint
5. Get UniProt function for biological context

**Interpreting DepMap scores**:
- Chronos score < -0.5: likely essential
- Chronos score < -1.0: strongly essential
- Compare to median across all lines to assess selectivity

### Phase 2: Pathway & Network Context

**Objective**: Identify convergent biological themes in the hit list.

**Tools**:
- `ReactomeAnalysis_pathway_enrichment` -- pathway enrichment analysis
  - Input: `identifiers` (space-separated gene list as STRING, not array)
  - Output: enriched pathways with p-values, gene counts
- `STRING_get_network` -- get protein interaction network
  - Input: `protein_ids` (array of gene names), `species` (9606 for human)
  - Output: interaction edges with confidence scores
- `STRING_functional_enrichment` -- GO/KEGG enrichment via STRING
  - Input: `protein_ids` (array), `species` (9606)
  - Output: enriched terms with FDR-corrected p-values

**Workflow**:
1. Run Reactome pathway enrichment on the full hit list
2. Build STRING network for the top hits (limit to 20-50 genes for interpretable networks)
3. Run STRING functional enrichment for GO terms and KEGG pathways
4. Identify pathway clusters -- groups of hits converging on the same biology
5. Highlight hits that are network hubs (high connectivity)

**Important**: For `ReactomeAnalysis_pathway_enrichment`, identifiers are space-separated (e.g., `"TP53 BRCA1 EGFR"`), not a list.

### Phase 3: Druggability Assessment

**Objective**: Determine which hits can be therapeutically targeted.

**Tools**:
- `DGIdb_get_drug_gene_interactions` -- find drugs targeting hit genes
  - Input: `genes` (list of gene names, e.g., `["EGFR", "BRAF"]`)
  - Output: drug-gene interactions with drug names, interaction types, sources
- `DGIdb_get_gene_druggability` -- assess druggable gene categories
  - Input: `genes` (list of gene names)
  - Output: `{data: {genes: {nodes: [{name, geneCategories}]}}}`
- `DepMap_get_drug_response` -- get drug sensitivity data
  - Input: `drug_name` or `gene_name`
  - Output: drug response (IC50, AUC) across cell lines

**Workflow**:
1. Query DGIdb for all hit genes to find existing drug-gene interactions
2. Get druggability categories (kinase, GPCR, ion channel, etc.)
3. For druggable hits, check DepMap drug response data
4. Classify each hit:
   - **Approved drug exists**: direct translational potential
   - **Druggable category, no approved drug**: compounds may exist in development
   - **Not in druggable category**: may need novel modalities (PROTAC, antisense, etc.)

### Phase 4: Clinical Evidence

**Objective**: Connect screen hits to known clinical and cancer biology.

**Tools**:
- `civic_search_evidence_items` -- search CIViC for clinical evidence
  - Input: `query` (gene name or variant)
  - Output: evidence items with clinical significance, disease, drugs
- `COSMIC_get_mutations_by_gene` -- get somatic mutation data
  - Input: `gene_name`
  - Output: mutation types, frequencies, cancer types
- `PubMed_search_articles` -- find relevant publications
  - Input: `query`, optional `limit`
  - Output: list of article dicts

**Workflow**:
1. For top prioritized hits, search CIViC for clinical evidence
2. Query COSMIC for somatic mutation frequency (high frequency = likely driver)
3. Classify genes as: known oncogene, tumor suppressor, or novel
4. Note any existing clinical implications (predictive, prognostic, diagnostic)

### Phase 5: Literature Context

**Objective**: Find published studies on key hits, especially in the disease context.

**Tools**:
- `PubMed_search_articles` -- biomedical literature search
  - Input: `query`, optional `limit`
  - Output: list of article dicts

**Workflow**:
1. For the top 5-10 prioritized hits, search PubMed for "[gene] [disease] essentiality" or "[gene] CRISPR screen"
2. Look for validation studies, mechanism papers, and therapeutic targeting efforts
3. Note any conflicting evidence or context-dependent findings

### Phase 6: Prioritized Report

Generate a ranked target list integrating all dimensions:

**Ranking criteria** (weight as appropriate for the context):
1. **Selective essentiality** (DepMap) -- selectively essential > pan-essential
2. **Pathway convergence** -- hits in enriched pathways rank higher
3. **Druggability** -- existing drugs > druggable category > undruggable
4. **Clinical evidence** -- CIViC/COSMIC evidence boosts ranking
5. **Constraint** -- high gnomAD constraint suggests biological importance
6. **Literature support** -- published functional data validates the hit

**Report structure**:
1. **Screen Summary** -- type, model, phenotype, total hits
2. **Top Targets** (ranked table) -- gene, DepMap score, selectivity, constraint, druggability, clinical evidence
3. **Enriched Pathways** -- convergent biology themes with gene members
4. **Network Analysis** -- interaction hubs, pathway clusters
5. **Druggable Targets** -- compounds, interaction types, development status
6. **Clinical Connections** -- CIViC evidence, COSMIC mutations
7. **Validation Recommendations** -- suggested orthogonal experiments
8. **Data Gaps** -- genes with limited annotation, missing data

---

## Common Analysis Patterns

| Pattern | Description | Key Phases |
|---------|-------------|------------|
| **Full Screen Interpretation** | Comprehensive hit validation and prioritization | All (0-6) |
| **Essentiality Check** | Quick DepMap lookup for a gene list | 0, 1 |
| **Pathway Discovery** | What biology do my hits converge on? | 0, 2 |
| **Druggable Target ID** | Which hits can I target with drugs? | 0, 1, 3 |
| **Clinical Translation** | Connect screen to patient relevance | 0, 1, 4, 5 |

---

## Edge Cases & Fallbacks

- **gnomAD "Service overloaded"**: Transient error. Retry once, then proceed without constraint data and note the gap
- **Gene not in DepMap**: Possible if the gene is not well-annotated. Fall back to gnomAD constraint and UniProt function
- **Large hit lists (>500 genes)**: Focus pathway enrichment on the full list, but do per-gene analysis only on top 50 by screen score
- **Non-cancer screens**: DepMap is cancer-focused. For non-cancer contexts, DepMap selectivity is less informative; weight constraint and pathway evidence more heavily
- **shRNA vs CRISPR**: shRNA screens have more off-target effects. Higher validation bar for shRNA-only hits

---

## Limitations

- **DepMap is cancer-centric**: Essentiality data covers ~1000 cancer cell lines; limited utility for non-cancer biology
- **Screen artifacts**: Seed effects (shRNA), copy number bias (CRISPR), and fitness confounders are not assessed by this skill
- **No raw screen analysis**: This skill interprets hit lists, not raw screen data (read counts, guide-level data). Use MAGeCK/BAGEL/CRISPRcleanR for upstream analysis
- **COSMIC access**: Some COSMIC data requires authentication; results may be limited
- **Interaction directionality**: STRING interactions are associations, not causal relationships

---
name: tooluniverse-metagenomics-analysis
description: Analyze microbiome and metagenomics data using MGnify, GTDB, GMrepo, and ENA. Covers study discovery, taxonomic profiling, genome quality assessment, functional annotation, and clinical phenotype associations. Use for 16S rRNA analysis, shotgun metagenomics, microbiome composition, taxonomic classification, and gut-health research.
---

# Metagenomics & Microbiome Analysis

Integrated pipeline for exploring microbiome studies, classifying taxa, assessing genome quality, and linking microbial composition to clinical phenotypes. Combines curated study databases (MGnify, ENA) with taxonomic references (GTDB) and clinical microbiome data (GMrepo).

**Guiding principles**:
1. **Study context first** -- understand the biome, sequencing method, and sample metadata before diving into taxa
2. **Taxonomic consistency** -- use GTDB taxonomy as the reference standard; reconcile NCBI taxonomy where needed
3. **Genome quality matters** -- CheckM completeness/contamination thresholds determine which MAGs are trustworthy
4. **Clinical grounding** -- connect microbial signatures to human phenotypes via GMrepo
5. **Progressive reporting** -- create the report file early and update it as phases complete
6. **English-first queries** -- use English terms in tool calls; respond in the user's language

---

## When to Use

Typical triggers:
- "What microbiome studies exist for [biome/disease]?"
- "Classify these taxa using GTDB"
- "Find metagenome-assembled genomes for [species]"
- "What gut bacteria are associated with [phenotype]?"
- "Search for 16S rRNA studies on [topic]"
- "Assess genome quality for [accession]"
- "Compare microbiome composition in [condition A] vs [condition B]"

**Not this skill**: For host genomics or variant calling, use `tooluniverse-variant-analysis`. For pathway enrichment of host genes, use `tooluniverse-gene-enrichment`.

---

## Core Databases

| Database | Scope | Best For |
|----------|-------|----------|
| **MGnify** | EBI metagenomics portal; studies, analyses, genomes, biomes | Discovering processed metagenomics studies and their taxonomic/functional results |
| **GTDB** | Genome Taxonomy Database; standardized bacterial/archaeal taxonomy | Consistent taxonomic classification, species-level resolution |
| **GMrepo** | Gut Microbiome Repository; curated phenotype-microbe associations | Linking gut species to human health conditions |
| **ENA** | European Nucleotide Archive; raw sequencing data | Finding raw 16S/shotgun datasets and study metadata |

---

## Workflow Overview

```
Phase 0: Query Parsing & Disambiguation
  Identify organism, biome, phenotype, or study accession
    |
Phase 1: Study Discovery
  Search MGnify studies and ENA for relevant datasets
    |
Phase 2: Taxonomic Classification
  Resolve species via GTDB; get lineage and type material
    |
Phase 3: Genome Quality & MAG Assessment
  Search MGnify genomes; evaluate completeness/contamination
    |
Phase 4: Functional & Ecological Context
  MGnify analyses for functional annotations; biome classification
    |
Phase 5: Clinical Phenotype Associations
  GMrepo phenotype-species links; disease relevance
    |
Phase 6: Report Synthesis
  Integrate findings into structured report
```

---

## Phase Details

### Phase 0: Query Parsing & Disambiguation

Parse the user's request to identify:
- **Organism or taxon** (e.g., "Bacteroides fragilis", "Firmicutes")
- **Biome or environment** (e.g., "human gut", "soil", "marine sediment")
- **Phenotype or disease** (e.g., "IBD", "obesity", "colorectal cancer")
- **Study accession** (e.g., MGYS00005292, PRJEB1234)

If the query is ambiguous, clarify before proceeding. A species name might match multiple GTDB entries; a disease might span several biomes.

### Phase 1: Study Discovery

**Objective**: Find relevant metagenomics studies and datasets.

**Tools**:
- `MGnify_search_studies` -- search by keyword, biome, or lineage
  - Input: `query` (search term), optional `biome`, `lineage`
  - Output: list of studies with accession, name, biome, sample count
- `MGnify_get_study` -- get full details for a known study accession
  - Input: `accession` (MGnify study ID)
  - Output: study metadata, associated analyses, biome hierarchy
- `MGnify_list_biomes` -- browse available biome categories
  - Output: hierarchical biome tree
- `ENAPortal_search_studies` -- search ENA for raw sequencing studies
  - Input: `query` (keyword), optional `result_type`, `limit`
  - Output: study accessions, titles, descriptions

**Workflow**:
1. Search MGnify for processed studies matching the query
2. If few MGnify results, broaden with ENA to find raw datasets
3. For each relevant study, note the biome, sequencing type (amplicon vs shotgun), and sample count
4. Retrieve full details for the top studies

**If no studies found**: Try broader search terms, check alternative biome categories via `MGnify_list_biomes`, or search ENA with simpler keywords.

### Phase 2: Taxonomic Classification

**Objective**: Resolve species/genus names to standardized GTDB taxonomy.

**Tools**:
- `GTDB_search_genomes` -- find reference genomes by species name
  - Input: `query` (species name), optional `limit`
  - Output: genome accessions, GTDB taxonomy, quality metrics
- `GTDB_get_species` -- get species cluster details
  - Input: `species_name` (GTDB species name)
  - Output: type genome, member genomes, taxonomy
- `GTDB_get_taxon_info` -- get taxonomic rank details
  - Input: `taxon` (e.g., "g__Bacteroides")
  - Output: rank, parent lineage, child taxa, genome count
- `GTDB_search_taxon` -- search for taxa by partial name
  - Input: `query` (partial name), optional `rank`
  - Output: matching taxa with lineage

**Workflow**:
1. Search GTDB for the taxon of interest
2. Get full lineage (domain through species)
3. Note any taxonomic reclassifications (GTDB vs NCBI naming differences are common)
4. For species-level queries, identify the type genome and representative genome

**Important**: GTDB uses its own naming conventions (e.g., `s__Bacteroides_A fragilis` may differ from NCBI's `Bacteroides fragilis`). Always note discrepancies.

### Phase 3: Genome Quality & MAG Assessment

**Objective**: Find and evaluate metagenome-assembled genomes (MAGs).

**Tools**:
- `MGnify_search_genomes` -- search the MGnify genome catalog
  - Input: `query` (species/taxon), optional `catalogue`, `limit`
  - Output: genome accessions, completeness, contamination, taxonomy
- `MGnify_get_genome` -- get detailed genome info
  - Input: `accession` (genome ID)
  - Output: full quality metrics (CheckM), gene count, taxonomy, source study

**Workflow**:
1. Search MGnify genomes for the target species
2. Filter by quality: completeness >= 50%, contamination <= 10% (medium quality); completeness >= 90%, contamination <= 5% (high quality)
3. Note the source study and biome for each genome
4. Compare genome statistics (size, GC content, gene count) across entries

**Quality tiers** (MIMAG standard):
- **High quality**: >= 90% complete, <= 5% contamination, 23S/16S/5S rRNA, >= 18 tRNAs
- **Medium quality**: >= 50% complete, <= 10% contamination
- **Low quality**: below medium thresholds -- flag but don't exclude without reason

### Phase 4: Functional & Ecological Context

**Objective**: Extract functional annotations and ecological context from processed analyses.

**Tools**:
- `MGnify_search_analyses` -- find analysis results for studies
  - Input: `study_accession` or `query`, optional `experiment_type`
  - Output: analysis accessions, pipeline version, experiment type
- `MGnify_list_biomes` -- understand the biome classification hierarchy
  - Output: nested biome tree with study counts

**Workflow**:
1. For studies from Phase 1, retrieve their analyses
2. Note the analysis pipeline version (affects available annotations)
3. Classify the ecological niche using the biome hierarchy
4. Summarize functional profile if available (GO terms, InterPro, KEGG)

### Phase 5: Clinical Phenotype Associations

**Objective**: Connect microbial taxa to human health phenotypes.

**Tools**:
- `GMrepo_search_species` -- search for species in the gut microbiome repository
  - Input: `query` (species name or NCBI taxon ID)
  - Output: species prevalence, relative abundance across phenotypes
- `GMrepo_get_phenotypes` -- get phenotypes associated with a species
  - Input: `query` (species name or taxon ID)
  - Output: phenotype list with prevalence and abundance data

**Workflow**:
1. For key taxa identified in earlier phases, query GMrepo
2. Get phenotype associations -- which diseases/conditions show enrichment or depletion
3. Note the sample sizes and prevalence ranges
4. Cross-reference with study findings from Phase 1

**Scope note**: GMrepo focuses on the human gut microbiome. For environmental metagenomics (soil, marine), this phase may be limited or skippable.

### Phase 6: Report Synthesis

Assemble findings into a structured report:

1. **Study Landscape** -- number of studies found, biomes covered, sequencing methods
2. **Taxonomic Profile** -- GTDB-standardized taxonomy, key lineages, naming discrepancies
3. **Genome Catalog** -- available MAGs with quality tiers, representative genomes
4. **Functional Summary** -- ecological context, functional annotations
5. **Clinical Relevance** -- phenotype associations, disease links, prevalence data
6. **Data Gaps** -- missing biomes, low-quality genomes, taxa without clinical data

---

## Common Analysis Patterns

| Pattern | Description | Key Phases |
|---------|-------------|------------|
| **Species Deep-Dive** | Full profile of one species: taxonomy, genomes, clinical links | 0, 2, 3, 5 |
| **Study Exploration** | Discover and summarize studies for a biome or disease | 0, 1, 4 |
| **MAG Quality Audit** | Evaluate genome quality for a set of species | 0, 2, 3 |
| **Disease-Microbiome Link** | Find taxa associated with a clinical condition | 0, 1, 5 |
| **Taxonomic Reconciliation** | Compare GTDB vs NCBI classification for a lineage | 0, 2 |

---

## Edge Cases & Fallbacks

- **Taxon not in GTDB**: May be a recently described species or use outdated naming. Try partial search via `GTDB_search_taxon`, or fall back to MGnify which uses NCBI taxonomy
- **No GMrepo data**: Normal for non-gut organisms. Note the gap and rely on literature
- **MGnify study vs ENA study**: MGnify contains processed results; ENA has raw data. If MGnify lacks a study, ENA may still have the raw reads
- **Large result sets**: MGnify and ENA can return hundreds of studies. Use biome filters and limit parameters to focus results
- **GTDB version differences**: Taxonomy changes between GTDB releases. Note the version when reporting classifications

---

## Limitations

- **GMrepo**: Gut-only; no coverage for skin, oral, vaginal, or environmental microbiomes
- **GTDB**: Bacteria and Archaea only; no eukaryotic microbes or viruses
- **MGnify**: Functional annotations depend on pipeline version; older analyses may lack newer annotations
- **ENA**: Raw data only; no processed taxonomic profiles
- **No direct sequence analysis**: This skill queries databases, not raw FASTQ/FASTA files. For sequence processing, use external pipelines (QIIME2, MetaPhlAn) and bring results here for annotation

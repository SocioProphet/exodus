# SIRE-inspired ingestion, normalization, and enrichment pipeline (2026)

## Position

Exodus should adopt the **shape** of IBM's document ingestion and enrichment pipeline while keeping the implementation fully open.

We do **not** adopt IBM proprietary runtimes. We adopt the architecture pattern.

## IBM patterns worth stealing

### 1. Staged enrichment flow

IBM's current unstructured data enrichment flow is explicitly staged as:
1. data ingestion
2. document curation
   1. document transformation
   2. document enrichment
3. entity curation
   1. entity curation
   2. entity table creation
   3. entity table enrichment.

### 2. End-to-end unstructured ETL

IBM's current unstructured data integration stack frames the problem as extract, transform, load, and scale for unstructured content. It highlights pre-built operations for text extraction, de-duplication, PII/HAP redaction, chunking, embeddings, and continuous updates with ACL-aware processing.

### 3. Layout-aware conversion and scalable microservices

IBM Research's Corpus Conversion Service describes a modular, asynchronous microservice architecture for converting PDFs/bitmaps into structured content representations at scale, with ground-truth collection and very high reported precision/recall for content conversion tasks.

### 4. Document understanding beyond OCR

IBM's document-understanding work emphasizes layout, tables, charts, noisy scans, and downstream graph-building rather than plain text OCR alone.

### 5. SIRE relation and mention extraction lineage

IBM's older SIRE lineage is relevant for the enrichment layer: Watson Explorer / Watson Knowledge Studio used SIRE for machine-learning annotators over mentions, relations, and coreferences, enabling automatic creation of structured exploratory facets from unstructured documents.

## Exodus 2026 pipeline

### Phase 3 and Phase 4 pipeline stages

1. **Acquire**
   - raw source objects
   - source metadata
   - ACLs / sharing context
   - manifests / hashes

2. **Transform**
   - format conversion
   - OCR when needed
   - layout parsing
   - page/block/table/figure extraction
   - language detection
   - de-dup fingerprints

3. **Normalize**
   - canonical document IR
   - canonical section/block/table representations
   - stable identifiers for spans and objects
   - provenance links to source pages/objects

4. **Enrich**
   - mention/entity extraction
   - relation extraction
   - coreference
   - document classification
   - sensitivity / secrecy / policy tags
   - business vocabulary / ontology mapping

5. **Curate entities**
   - entity tables
   - entity linking
   - confidence tracking
   - source evidence mapping

6. **Adaptive chunking and retrieval overlays**
   - deterministic chunks first
   - optional H-net dynamic chunking second
   - vector and lexical index overlays

7. **Serve evidence and analytics**
   - Drill over JSONL / Parquet / Iceberg
   - score explanations
   - review exports
   - dashboards

## Open implementation mapping

| IBM-style stage | Exodus open implementation |
|---|---|
| ingestion | object lake + manifests + Kafka registration |
| document transformation | Beam processors + OCR/layout parsers |
| document enrichment | NER/relation/coref/classification/tagging jobs |
| entity curation | entity tables in Parquet/Iceberg + Drill views |
| monitoring/rerun | Kafka events + run manifests + replayable Beam jobs |

## Core rule

The canonical preservation and normalization outputs must remain deterministic.
Model-driven enrichment is layered on top, versioned, and attributable.

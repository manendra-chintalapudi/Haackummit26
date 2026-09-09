# Project structure

The repository keeps one folder per responsibility. Runtime code is separated from data, the web client, and evaluation tools.

```text
synapse/
├── api/          FastAPI routes, auth, RCA, compliance, knowledge transfer
├── router/       Entity matching and retrieval-plan selection
├── retrieval/    DuckDB and Neo4j access
├── embeddings/   Chroma ingestion and document search
├── synthesizer/  Evidence-based answer generation and confidence scoring
├── ontology/     Graph schema, nodes, relationships, and loaders
├── data/         Local DuckDB files and source data
├── frontend/     Static client and React/Vite source
├── evaluation/   Benchmarks and regression checks
├── scripts/      Data preparation utilities
├── supabase/     Authentication schema
└── docs/         Project documentation and architecture assets
```

The current names are intentionally short and match the imports and deployment layout. Renaming them would add path and import churn without improving navigation.

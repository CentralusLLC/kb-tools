---
type: Architecture
title: Research data
description: Conventions for structured research data in the repository's data/ folder - dataset layout, formats, Frictionless datapackage.json descriptors, provenance, and the path to the application database.
tags: [architecture, data, research, datasets]
status: draft
generated:
  by: claude-code/opus-5.5
  at: 2026-11-05T06:34:50Z
---

# Research data

The repository's `data/` folder (next to `docs/`) holds structured data from
research: tables of products, prices, locations, reference values, and
anything else that may later be loaded into the application database. Knowledge
*about* the data, such as what it means and how it is used, lives in this
knowledge base. The data itself lives in `data/`.

## Layout

One folder per dataset:

```
data/
  README.md                 # points here
  <dataset>/
    datapackage.json        # descriptor: files, schema, sources (required)
    README.md               # optional notes for people
    <table>.csv             # one file per table
```

Name datasets for what they hold (`products`, `price-list`, `site-locations`),
not for where they came from.

## Formats

- **Tables:** CSV in UTF-8, one header row, one table per file. Use snake_case
  column names. Each table needs a primary key column (`id`), which keeps rows
  stable through migration.
- **Nested or graph data:** JSON (or JSON Lines for large record sets).
- Never commit spreadsheets with formulas (`.xlsx`). Export them to CSV and keep the
  original in `docs/sources/` if it matters.

## Descriptor (`datapackage.json`)

Each dataset carries a [Frictionless Data Package](https://datapackage.org)
descriptor. It is a widely used, tool-supported standard: you can validate it
with `frictionless validate`, and it maps onto database tables cleanly.

```json
{
  "name": "products",
  "title": "Product catalog",
  "description": "Products with base attributes, from early market research.",
  "sources": [
    {"title": "Product research notes", "path": "../../docs/sources/2026-01-10-product-notes.md"}
  ],
  "resources": [
    {
      "name": "products",
      "path": "products.csv",
      "schema": {
        "fields": [
          {"name": "id", "type": "string", "constraints": {"required": true, "unique": true}},
          {"name": "name", "type": "string"},
          {"name": "category", "type": "string", "constraints": {"enum": ["hardware", "software", "service"]}},
          {"name": "unit_price", "type": "number"}
        ],
        "primaryKey": "id"
      }
    }
  ]
}
```

- Field names and enum values use the [glossary](../domains/glossary.md) terms.
- `sources` links back to the files in `docs/sources/` that the data came from. The
  [ingest log](../process/ingestion.md) links forward to the dataset.
- Link each dataset from the domain page that describes it.

## Path to the application database

> Open question: The database technology and the migration mechanism (seed scripts,
> migrations, an import tool) depend on the [system architecture](overview.md).

Until those are decided:

- Treat `data/` as the source of truth for reference and seed data.
- Change a schema by editing `datapackage.json` in the same pull request as the CSV
  change.
- When data is migrated into the database, record it in the dataset's `README.md`
  (what, when, target) so `data/` and the database don't drift silently.

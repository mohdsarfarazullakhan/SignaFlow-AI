# Data boundaries

- `seed/` contains clearly labelled demonstration inputs.
- `cache/` is created by the respectful catalogue ingestion adapter and is ignored by Git.
- `vector_db/` is the optional persistent Chroma location and is ignored by Git.
- No bundled seed product is represented as real supplier inventory.

CSV and JSON product exports can be imported with `scripts/ingest_products.py`. Use `--demo` for illustrative records. Only reviewed public-source or manually approved imports should omit that flag.

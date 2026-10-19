from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.database.session import Base, SessionLocal, engine  # noqa: E402
from app.integrations.catalog_ingestion import CatalogueIngestionService  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Respectfully ingest explicitly allowed public product pages, a capped sitemap, or a local CSV/JSON export.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", action="append", help="Explicit public product URL (repeatable)")
    group.add_argument("--sitemap", help="Public sitemap URL; processing is capped")
    group.add_argument("--file", type=Path, help="Local .csv or .json catalogue export")
    parser.add_argument("--limit", type=int, default=25, help="Maximum sitemap product pages (max 50)")
    parser.add_argument("--demo", action="store_true", help="Mark a local import as demo data")
    args = parser.parse_args()
    service = CatalogueIngestionService(ROOT / "data" / "cache")
    Base.metadata.create_all(engine)
    if args.file:
        candidates = service.import_file(args.file)
        source, is_demo = ("demo-import", True) if args.demo else ("approved-manual-import", False)
    else:
        urls = args.url or service.product_urls_from_sitemap(args.sitemap, limit=args.limit)
        candidates = []
        for url in urls:
            try:
                candidates.extend(service.parse_product_page(service.fetch(url), url))
            except Exception as exc:
                print(f"Skipped {url}: {exc}")
        source, is_demo = "approved-public-web", False
    with SessionLocal() as db:
        created, updated = service.upsert(db, candidates, source=source, is_demo=is_demo)
    print(f"Ingestion complete: {created} created, {updated} updated, {len(candidates)} normalized records.")


if __name__ == "__main__":
    main()


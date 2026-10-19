from __future__ import annotations

import csv
import hashlib
import html
import json
import logging
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import httpx
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import Product

logger = logging.getLogger(__name__)


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:250]


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    without_tags = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(without_tags)).strip()


class JsonLdParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.inside_json_ld = False
        self.buffer: list[str] = []
        self.blocks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = dict(attrs)
        if tag.lower() == "script" and attr_map.get("type", "").lower() == "application/ld+json":
            self.inside_json_ld = True
            self.buffer = []

    def handle_data(self, data: str) -> None:
        if self.inside_json_ld:
            self.buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self.inside_json_ld:
            self.blocks.append("".join(self.buffer))
            self.buffer = []
            self.inside_json_ld = False


@dataclass
class ProductCandidate:
    name: str
    category: str = "Uncategorized"
    subcategory: str | None = None
    description: str = "Specification not available."
    use_cases: list[str] = field(default_factory=list)
    industries: list[str] = field(default_factory=list)
    environment: str | None = None
    dimensions: str | None = None
    material: str | None = None
    brand: str | None = None
    specifications_json: dict[str, Any] = field(default_factory=dict)
    price: str | None = None
    currency: str = "AED"
    availability: str | None = None
    source_url: str | None = None
    image_url: str | None = None


class CatalogueIngestionService:
    """Rate-limited, robots-aware importer for explicit pages, sitemaps, CSV, and JSON."""

    def __init__(self, cache_dir: Path, *, allowed_hosts: set[str] | None = None, delay_seconds: float = 1.25, retry_limit: int = 2) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.allowed_hosts = {host.lower() for host in (allowed_hosts if allowed_hosts is not None else settings.catalog_allowed_hosts)}
        self.delay_seconds = max(1.0, delay_seconds)
        self.retry_limit = min(max(0, retry_limit), 3)
        self.client = httpx.Client(timeout=15, follow_redirects=True, headers={"User-Agent": "SignaFlowAIPrototype/0.1 (+respectful catalogue ingestion)"})
        self._robots: dict[str, RobotFileParser] = {}
        self._last_request_at = 0.0

    def _validate_url(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or parsed.hostname not in self.allowed_hosts:
            raise ValueError("URL host is not present in CATALOG_ALLOWED_HOSTS")

    def _cache_path(self, url: str) -> Path:
        return self.cache_dir / f"{hashlib.sha256(url.encode()).hexdigest()}.cache"

    def _wait(self) -> None:
        remaining = self.delay_seconds - (time.monotonic() - self._last_request_at)
        if remaining > 0:
            time.sleep(remaining)

    def _robots_allowed(self, url: str) -> bool:
        parsed = urlparse(url)
        origin = f"{parsed.scheme}://{parsed.netloc}"
        if origin not in self._robots:
            parser = RobotFileParser(f"{origin}/robots.txt")
            try:
                self._wait()
                response = self.client.get(parser.url)
                self._last_request_at = time.monotonic()
                if response.status_code < 400:
                    parser.parse(response.text.splitlines())
                else:
                    parser.parse([])
            except httpx.HTTPError as exc:
                logger.warning("robots unavailable host=%s error=%s; skipping live fetch", parsed.netloc, type(exc).__name__)
                parser.parse(["User-agent: *", "Disallow: /"])
            self._robots[origin] = parser
        return self._robots[origin].can_fetch(self.client.headers["User-Agent"], url)

    def fetch(self, url: str, *, use_cache: bool = True) -> str:
        self._validate_url(url)
        cache_path = self._cache_path(url)
        if use_cache and cache_path.exists():
            return cache_path.read_text(encoding="utf-8")
        if not self._robots_allowed(url):
            raise PermissionError(f"robots.txt does not allow this URL: {url}")
        last_error: Exception | None = None
        for attempt in range(self.retry_limit + 1):
            try:
                self._wait()
                response = self.client.get(url)
                self._last_request_at = time.monotonic()
                response.raise_for_status()
                cache_path.write_text(response.text, encoding="utf-8")
                return response.text
            except httpx.HTTPError as exc:
                last_error = exc
                logger.warning("catalogue fetch failed attempt=%d url=%s error=%s", attempt + 1, url, type(exc).__name__)
        raise RuntimeError(f"Could not fetch public catalogue page after {self.retry_limit + 1} attempts") from last_error

    def parse_product_page(self, page_html: str, source_url: str) -> list[ProductCandidate]:
        parser = JsonLdParser()
        parser.feed(page_html)
        products: list[dict[str, Any]] = []

        def walk(value: Any) -> None:
            if isinstance(value, dict):
                item_type = value.get("@type")
                if item_type == "Product" or isinstance(item_type, list) and "Product" in item_type:
                    products.append(value)
                for child in value.values():
                    walk(child)
            elif isinstance(value, list):
                for child in value:
                    walk(child)

        for block in parser.blocks:
            try:
                walk(json.loads(block))
            except json.JSONDecodeError:
                logger.info("Ignoring invalid JSON-LD block url=%s", source_url)
        candidates: list[ProductCandidate] = []
        for item in products:
            offers = item.get("offers") or {}
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            brand = item.get("brand") or {}
            image = item.get("image")
            if isinstance(image, list):
                image = image[0] if image else None
            name = clean_text(str(item.get("name") or ""))
            if not name:
                continue
            candidates.append(ProductCandidate(name=name, category=clean_text(str(item.get("category") or "Uncategorized")), description=clean_text(str(item.get("description") or "")) or "Specification not available.", brand=clean_text(str(brand.get("name") if isinstance(brand, dict) else brand)) or None, specifications_json={"sku": item.get("sku")} if item.get("sku") else {}, price=str(offers.get("price")) if offers.get("price") is not None else None, currency=str(offers.get("priceCurrency") or "AED"), availability=str(offers.get("availability", "")).rsplit("/", 1)[-1] or None, source_url=source_url, image_url=str(image) if image else None))
        return candidates

    def product_urls_from_sitemap(self, sitemap_url: str, *, limit: int = 25) -> list[str]:
        xml = self.fetch(sitemap_url)
        root = ET.fromstring(xml)
        urls = [element.text.strip() for element in root.iter() if element.tag.endswith("loc") and element.text]
        return [url for url in urls if "/product/" in url and urlparse(url).hostname in self.allowed_hosts][: min(limit, 50)]

    @staticmethod
    def import_file(path: Path) -> list[ProductCandidate]:
        suffix = path.suffix.lower()
        if suffix == ".json":
            payload = json.loads(path.read_text(encoding="utf-8"))
            rows = payload if isinstance(payload, list) else payload.get("products", [])
        elif suffix == ".csv":
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
        else:
            raise ValueError("Only .json and .csv imports are supported")
        candidates = []
        for row in rows:
            normalized = dict(row)
            for key in ("use_cases", "industries"):
                value = normalized.get(key, [])
                normalized[key] = value if isinstance(value, list) else [item.strip() for item in str(value).split("|") if item.strip()]
            specs = normalized.get("specifications_json", {})
            normalized["specifications_json"] = specs if isinstance(specs, dict) else json.loads(specs or "{}")
            candidates.append(ProductCandidate(**{key: value for key, value in normalized.items() if key in ProductCandidate.__dataclass_fields__}))
        return candidates

    @staticmethod
    def upsert(db: Session, candidates: Iterable[ProductCandidate], *, source: str, is_demo: bool) -> tuple[int, int]:
        created = updated = 0
        for candidate in candidates:
            slug = slugify(candidate.name)
            query = db.query(Product).filter(Product.slug == slug)
            if candidate.source_url:
                query = db.query(Product).filter(or_(Product.source_url == candidate.source_url, Product.slug == slug))
            product = query.first()
            values = candidate.__dict__ | {"slug": slug, "source": source, "is_demo": is_demo}
            if product:
                for key, value in values.items():
                    setattr(product, key, value)
                updated += 1
            else:
                db.add(Product(**values))
                created += 1
        db.commit()
        return created, updated


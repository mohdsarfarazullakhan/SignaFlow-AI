import json

from app.integrations.catalog_ingestion import CatalogueIngestionService


def test_json_file_import_normalizes_list_fields(tmp_path):
    path = tmp_path / "products.json"
    path.write_text(json.dumps([{"name": "Approved Sample", "category": "Accessories", "description": "A reviewed import.", "use_cases": "mounting|installation", "industries": ["retail"]}]), encoding="utf-8")
    candidates = CatalogueIngestionService.import_file(path)
    assert candidates[0].use_cases == ["mounting", "installation"]
    assert candidates[0].industries == ["retail"]


def test_public_page_parser_reads_product_json_ld(tmp_path):
    service = CatalogueIngestionService(tmp_path / "cache", allowed_hosts={"catalog.example.com"})
    page = '<html><script type="application/ld+json">{"@type":"Product","name":"Public Product","description":"Verified description","category":"Digital Signage","offers":{"price":"99.50","priceCurrency":"AED","availability":"https://schema.org/InStock"}}</script></html>'
    candidates = service.parse_product_page(page, "https://catalog.example.com/product/public-product")
    assert len(candidates) == 1
    assert candidates[0].name == "Public Product"
    assert candidates[0].price == "99.50"
    assert candidates[0].availability == "InStock"

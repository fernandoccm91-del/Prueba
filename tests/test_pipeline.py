import unittest
from datetime import date, timedelta

from productscout.config import Settings
from productscout.models import AmazonProduct, PriceTier, SupplierQuote
from productscout.pipeline import Pipeline, ScanRequest
from productscout.sources.base import get_amazon_source, get_ml_source, get_supplier_source


def make_settings(**overrides) -> Settings:
    settings = Settings()
    for key, value in overrides.items():
        setattr(settings, key, value)
    return settings


class MockSourceTests(unittest.TestCase):
    def setUp(self):
        self.settings = make_settings()

    def test_amazon_mock_search_by_keyword(self):
        source = get_amazon_source(self.settings)
        results = source.search("cable organizer")
        self.assertTrue(results)
        self.assertTrue(any("Cable" in p.title for p in results))

    def test_amazon_mock_search_by_spanish_keyword(self):
        results = get_amazon_source(self.settings).search("pastillero")
        self.assertEqual([p.asin for p in results], ["B0DRT6VQ4H"])

    def test_amazon_mock_empty_keyword_returns_catalog(self):
        self.assertGreater(len(get_amazon_source(self.settings).search("")), 10)

    def test_ml_mock_is_deterministic(self):
        source = get_ml_source(self.settings)
        first, second = source.market("vaso plegable"), source.market("vaso plegable")
        self.assertEqual(first.total_listings, second.total_listings)
        self.assertEqual(first.sold_total, second.sold_total)
        self.assertGreater(first.total_listings, 0)

    def test_supplier_mock_prices_anchor_to_retail(self):
        quotes = get_supplier_source(self.settings).quotes("travel cup", reference_price_usd=20.0)
        self.assertTrue(quotes)
        for quote in quotes:
            self.assertLess(quote.unit_price_usd, 20.0 * 0.35)
            self.assertGreater(quote.moq, 0)

    def test_supplier_quotes_sorted_by_price(self):
        quotes = get_supplier_source(self.settings).quotes("phone stand", reference_price_usd=22.0)
        self.assertEqual([q.unit_price_usd for q in quotes], sorted(q.unit_price_usd for q in quotes))


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.pipeline = Pipeline(make_settings())

    def test_scan_produces_ranked_scored_opportunities(self):
        result = self.pipeline.scan(ScanRequest(keywords=[""], limit_per_keyword=50))
        self.assertTrue(result.opportunities)
        scores = [o.total_score for o in result.opportunities]
        self.assertEqual(scores, sorted(scores, reverse=True))
        for opp in result.opportunities:
            self.assertGreater(opp.amazon_monthly_units, 0)
            self.assertIsNotNone(opp.economics)
            self.assertIsNotNone(opp.ml_market)
            self.assertIn(opp.verdict, {"perseguir", "investigar", "dudoso", "descartar"})

    def test_min_score_filters_results(self):
        everything = self.pipeline.scan(ScanRequest(keywords=[""], limit_per_keyword=50))
        filtered = self.pipeline.scan(ScanRequest(keywords=[""], limit_per_keyword=50, min_score=70))
        self.assertLessEqual(len(filtered.opportunities), len(everything.opportunities))
        self.assertTrue(all(o.total_score >= 70 for o in filtered.opportunities))

    def test_small_only_drops_oversize_and_heavy(self):
        result = self.pipeline.scan(ScanRequest(keywords=[""], limit_per_keyword=50, small_only=True))
        for opp in result.opportunities:
            self.assertLessEqual(opp.product.weight_g, 900)

    def test_flags_can_skip_ml_and_suppliers(self):
        result = self.pipeline.scan(
            ScanRequest(keywords=[""], check_mercadolibre=False, check_suppliers=False)
        )
        opp = result.opportunities[0]
        self.assertIsNone(opp.ml_market)
        self.assertEqual(opp.quotes, [])
        self.assertIsNone(opp.economics)

    def test_a_new_low_review_product_outranks_a_saturated_one(self):
        result = self.pipeline.scan(ScanRequest(keywords=[""], limit_per_keyword=50))
        by_asin = {o.product.asin: o for o in result.opportunities}
        fresh = by_asin["B0D3F8W7RK"]      # 34 reseñas, publicado en 2026
        crowded = by_asin["B0CT4LZ8YQ"]    # 4200 reseñas, 11 vendedores, de 2023
        self.assertGreater(fresh.scores["competition"], crowded.scores["competition"])
        self.assertGreater(fresh.scores["novelty"], crowded.scores["novelty"])
        self.assertGreater(fresh.total_score, crowded.total_score)

    def test_scan_survives_a_failing_source(self):
        class Boom:
            name = "boom"

            def market(self, query, limit=50):
                raise RuntimeError("API caída")

        self.pipeline.ml = Boom()
        result = self.pipeline.scan(ScanRequest(keywords=["travel cup"]))
        self.assertTrue(result.opportunities)
        self.assertTrue(result.errors)
        self.assertIsNone(result.opportunities[0].ml_market)

    def test_supplier_search_url_is_brand_free(self):
        product = AmazonProduct(
            asin="X", title="Nordika Silicone Collapsible Travel Cup with Lid",
            category="Home & Kitchen", price=18.99, brand="Nordika",
        )
        url = self.pipeline.supplier_search_url(product)
        self.assertIn("alibaba.com", url)
        self.assertNotIn("Nordika", url)


class QuoteTests(unittest.TestCase):
    def test_price_at_uses_the_highest_matching_tier(self):
        quote = SupplierQuote(
            supplier_name="X", product_title="Y", unit_price_usd=2.0, moq=100,
            price_tiers=[
                PriceTier(min_qty=100, unit_price_usd=2.0),
                PriceTier(min_qty=500, unit_price_usd=1.7),
                PriceTier(min_qty=2000, unit_price_usd=1.4),
            ],
        )
        self.assertEqual(quote.price_at(100), 2.0)
        self.assertEqual(quote.price_at(499), 2.0)
        self.assertEqual(quote.price_at(500), 1.7)
        self.assertEqual(quote.price_at(5000), 1.4)


class ProductTests(unittest.TestCase):
    def test_age_days_and_dimensions(self):
        product = AmazonProduct(
            asin="X", title="Y", category="Z", price=10.0,
            first_available=date.today() - timedelta(days=45),
            length_mm=100, width_mm=50, height_mm=20,
        )
        self.assertEqual(product.age_days, 45)
        self.assertEqual(product.longest_side_mm, 100)
        self.assertAlmostEqual(product.volume_cm3, 10 * 5 * 2)


if __name__ == "__main__":
    unittest.main()

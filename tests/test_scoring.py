import unittest
from datetime import date, timedelta

from productscout.config import CostAssumptions, Settings
from productscout.estimators import bsr_to_daily_units, bsr_to_monthly_units, ml_monthly_units
from productscout.fees import compute_economics, fba_fee, size_tier
from productscout.models import AmazonProduct, MLMarket, PriceTier, SupplierQuote
from productscout.scoring import (
    competition_score,
    demand_score,
    margin_score,
    ml_score,
    novelty_score,
    size_score,
    verdict_for,
)


def product(**kwargs) -> AmazonProduct:
    base = dict(asin="B0TEST", title="Test", category="Home & Kitchen", price=19.99)
    base.update(kwargs)
    return AmazonProduct(**base)


class EstimatorTests(unittest.TestCase):
    def test_better_rank_means_more_units(self):
        self.assertGreater(bsr_to_daily_units(100, "Home & Kitchen"),
                           bsr_to_daily_units(10_000, "Home & Kitchen"))
        self.assertGreater(bsr_to_daily_units(10_000, "Home & Kitchen"),
                           bsr_to_daily_units(200_000, "Home & Kitchen"))

    def test_missing_or_invalid_rank_is_zero(self):
        self.assertEqual(bsr_to_daily_units(None), 0.0)
        self.assertEqual(bsr_to_daily_units(0), 0.0)
        self.assertEqual(bsr_to_daily_units(-5), 0.0)

    def test_monthly_is_thirty_days(self):
        self.assertAlmostEqual(bsr_to_monthly_units(5000), bsr_to_daily_units(5000) * 30)

    def test_curve_lands_in_a_believable_range(self):
        # A top-100 product in a big category should be in the hundreds/day,
        # and a rank-100k product should be a couple of units/day.
        self.assertTrue(100 < bsr_to_daily_units(100, "Home & Kitchen") < 1500)
        self.assertTrue(0.5 < bsr_to_daily_units(100_000, "Home & Kitchen") < 5)

    def test_unknown_category_uses_the_default_curve(self):
        self.assertEqual(bsr_to_daily_units(5000, "Categoría Inventada"),
                         bsr_to_daily_units(5000, "default"))

    def test_ml_monthly_units_amortises_lifetime_sales(self):
        self.assertAlmostEqual(ml_monthly_units(1200, window_months=12), 100.0)
        self.assertEqual(ml_monthly_units(0), 0.0)


class FeeTests(unittest.TestCase):
    def test_size_tiers(self):
        small = product(weight_g=145, length_mm=95, width_mm=95, height_mm=15)
        large = product(weight_g=900, length_mm=400, width_mm=300, height_mm=150)
        huge = product(weight_g=12000, length_mm=800, width_mm=500, height_mm=400)
        self.assertEqual(size_tier(small), "small_standard")
        self.assertEqual(size_tier(large), "large_standard")
        self.assertEqual(size_tier(huge), "oversize")
        self.assertEqual(size_tier(product()), "unknown")

    def test_fee_grows_with_weight(self):
        light = product(weight_g=50, length_mm=95, width_mm=95, height_mm=15)
        heavy = product(weight_g=400, length_mm=95, width_mm=95, height_mm=15)
        self.assertLess(fba_fee(light), fba_fee(heavy))

    def test_economics_add_up(self):
        item = product(price=24.99, weight_g=200, length_mm=150, width_mm=100, height_mm=18)
        quote = SupplierQuote(
            supplier_name="S", product_title="P", unit_price_usd=3.0, moq=500,
            price_tiers=[PriceTier(min_qty=500, unit_price_usd=3.0)],
        )
        econ = compute_economics(item, quote, CostAssumptions(), order_qty=500)
        self.assertAlmostEqual(
            econ.landed_cost_usd,
            econ.unit_cost_usd + econ.freight_usd + econ.duty_usd + econ.prep_usd,
            places=2,
        )
        self.assertAlmostEqual(
            econ.profit_per_unit_usd,
            econ.sale_price_usd - econ.landed_cost_usd - econ.platform_fee_usd - econ.fulfilment_fee_usd,
            places=2,
        )
        self.assertAlmostEqual(econ.upfront_investment_usd, econ.landed_cost_usd * 500, places=1)
        self.assertGreater(econ.roi, 0)

    def test_sea_freight_is_cheaper_than_air(self):
        item = product(weight_g=600, length_mm=200, width_mm=150, height_mm=100)
        quote = SupplierQuote(supplier_name="S", product_title="P", unit_price_usd=4.0, moq=100)
        air = compute_economics(item, quote, CostAssumptions(freight_mode="air"))
        sea = compute_economics(item, quote, CostAssumptions(freight_mode="sea"))
        self.assertGreater(air.freight_usd, sea.freight_usd)

    def test_a_bad_deal_shows_negative_profit(self):
        item = product(price=12.0, weight_g=800, length_mm=300, width_mm=200, height_mm=100)
        quote = SupplierQuote(supplier_name="S", product_title="P", unit_price_usd=9.0, moq=100)
        econ = compute_economics(item, quote, CostAssumptions())
        self.assertLess(econ.profit_per_unit_usd, 0)


class ScoreTests(unittest.TestCase):
    def setUp(self):
        self.settings = Settings()

    def test_demand_score_is_monotonic(self):
        self.assertGreater(demand_score(3000, 60000), demand_score(300, 6000))
        self.assertGreater(demand_score(300, 6000), demand_score(10, 200))

    def test_few_reviews_beats_many(self):
        quiet, _ = competition_score(product(reviews_count=20, offers_count=1))
        loud, _ = competition_score(product(reviews_count=6000, offers_count=1))
        self.assertGreater(quiet, loud)

    def test_amazon_as_a_seller_is_penalised(self):
        without, _ = competition_score(product(reviews_count=50, offers_count=1))
        with_amazon, notes = competition_score(
            product(reviews_count=50, offers_count=1, amazon_sells_it=True)
        )
        self.assertLess(with_amazon, without)
        self.assertTrue(any("Amazon" in note for note in notes))

    def test_many_sellers_on_the_listing_is_penalised(self):
        few, _ = competition_score(product(reviews_count=50, offers_count=1))
        many, _ = competition_score(product(reviews_count=50, offers_count=15))
        self.assertLess(many, few)

    def test_peer_reviews_shift_the_score(self):
        easy, _ = competition_score(product(reviews_count=50), peer_reviews=[10, 20, 30])
        hard, _ = competition_score(product(reviews_count=50), peer_reviews=[5000, 8000, 12000])
        self.assertGreater(easy, hard)

    def test_novelty_prefers_recent_listings(self):
        new, _ = novelty_score(product(first_available=date.today() - timedelta(days=30)))
        old, _ = novelty_score(product(first_available=date.today() - timedelta(days=1500)))
        unknown, notes = novelty_score(product())
        self.assertGreater(new, old)
        self.assertEqual(unknown, 50.0)
        self.assertTrue(notes)

    def test_small_products_score_higher(self):
        small, _ = size_score(
            product(weight_g=120, length_mm=95, width_mm=95, height_mm=15), self.settings
        )
        big, _ = size_score(
            product(weight_g=9000, length_mm=700, width_mm=400, height_mm=300), self.settings
        )
        self.assertEqual(small, 100.0)
        self.assertLess(big, 30.0)

    def test_over_weight_limit_is_penalised(self):
        settings = Settings()
        settings.max_weight_g = 300
        light, _ = size_score(product(weight_g=200, length_mm=95, width_mm=95, height_mm=15), settings)
        heavy, _ = size_score(product(weight_g=500, length_mm=95, width_mm=95, height_mm=15), settings)
        self.assertLess(heavy, light)

    def test_margin_score_without_quote_is_zero(self):
        score, notes = margin_score(None)
        self.assertEqual(score, 0.0)
        self.assertTrue(notes)

    def test_ml_score_rewards_demand_with_little_competition(self):
        thin = MLMarket(query="q", site="MLM", total_listings=60, monthly_units_est=400)
        crowded = MLMarket(query="q", site="MLM", total_listings=4000, monthly_units_est=400)
        self.assertGreater(ml_score(thin)[0], ml_score(crowded)[0])

    def test_official_stores_hurt_the_ml_score(self):
        open_market = MLMarket(query="q", site="MLM", total_listings=200, monthly_units_est=300)
        locked = MLMarket(query="q", site="MLM", total_listings=200,
                          monthly_units_est=300, official_store_share=0.8)
        self.assertGreater(ml_score(open_market)[0], ml_score(locked)[0])

    def test_verdict_thresholds(self):
        self.assertEqual(verdict_for(80), "perseguir")
        self.assertEqual(verdict_for(65), "investigar")
        self.assertEqual(verdict_for(50), "dudoso")
        self.assertEqual(verdict_for(20), "descartar")


if __name__ == "__main__":
    unittest.main()

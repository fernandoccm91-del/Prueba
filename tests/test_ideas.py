import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from productscout.cli import main
from productscout.config import CostAssumptions, MarketAssumptions, Settings
from productscout.db import connect, get_idea, latest_run_id, list_ideas, save_niche_run
from productscout.fees import compute_ml_economics, shipping_cost_local
from productscout.ideas import NicheScanner, NicheScanRequest
from productscout.keywords import to_english
from productscout.models import MLMarket, PriceTier, SupplierQuote
from productscout.niches import get_niche, load_niches, niche_names
from productscout.scoring import competencia_ml_score, demanda_ml_score, ganancia_score


def quote(price=3.0, moq=200, weight=250.0) -> SupplierQuote:
    return SupplierQuote(
        supplier_name="Yiwu Test Co.", product_title="test", unit_price_usd=price, moq=moq,
        unit_weight_g=weight, price_tiers=[PriceTier(min_qty=moq, unit_price_usd=price)],
    )


class NicheTests(unittest.TestCase):
    def test_bathroom_niche_exists_and_has_terms(self):
        niche = get_niche("bano")
        self.assertIsNotNone(niche)
        self.assertGreater(len(niche.terminos), 20)
        self.assertIn("organizador de ducha", niche.terminos)

    def test_lookup_ignores_accents_and_case(self):
        self.assertIsNotNone(get_niche("baño"))
        self.assertIsNotNone(get_niche("BAÑO"))
        self.assertIsNotNone(get_niche("Baño"))

    def test_unknown_niche_returns_none(self):
        self.assertIsNone(get_niche("submarinismo"))

    def test_niche_names_are_listed(self):
        self.assertIn("bano", niche_names())
        self.assertEqual(set(niche_names()), set(load_niches().keys()))


class TranslationTests(unittest.TestCase):
    def test_known_phrases_use_the_dictionary(self):
        self.assertEqual(to_english("organizador de ducha"), "shower caddy organizer")
        self.assertEqual(to_english("atrapa pelos ducha"), "shower drain hair catcher")

    def test_case_and_spacing_do_not_matter(self):
        self.assertEqual(to_english("  Organizador De Ducha "), "shower caddy organizer")

    def test_unknown_phrase_falls_back_to_word_by_word(self):
        result = to_english("cepillo de dientes electrico")
        self.assertNotIn(" de ", f" {result} ")   # se eliminan las preposiciones
        self.assertIn("brush", result)            # traduce lo que conoce
        self.assertIn("dientes", result)          # y deja igual lo que no

    def test_translation_never_returns_empty_for_real_terms(self):
        for term in get_niche("bano").terminos:
            self.assertTrue(to_english(term).strip(), term)


class MLEconomicsTests(unittest.TestCase):
    def setUp(self):
        self.market = MarketAssumptions()   # Chile por defecto
        self.costs = CostAssumptions()

    def test_the_numbers_add_up(self):
        econ = compute_ml_economics(24990, quote(), self.market, self.costs, weight_g=250)
        expected = (
            econ.net_revenue_local - econ.commission_local - econ.fixed_fee_local
            - econ.shipping_local - econ.landed_cost_local
        )
        self.assertAlmostEqual(econ.profit_local, expected, delta=1)
        self.assertEqual(econ.currency, "CLP")

    def test_vat_is_discounted_from_revenue_when_recoverable(self):
        econ = compute_ml_economics(11900, quote(), self.market, self.costs)
        self.assertAlmostEqual(econ.net_revenue_local, 10000, delta=1)

    def test_vat_becomes_a_cost_when_not_recoverable(self):
        recoverable = compute_ml_economics(24990, quote(), self.market, self.costs)
        market = MarketAssumptions(vat_recoverable=False)
        not_recoverable = compute_ml_economics(24990, quote(), market, self.costs)
        # Con empresa: el IVA de importación se recupera, pero el precio de ML
        # lleva IVA incluido y hay que descontarlo del ingreso.
        self.assertGreater(not_recoverable.landed_cost_local, recoverable.landed_cost_local)
        self.assertEqual(not_recoverable.net_revenue_local, not_recoverable.sale_price_local)
        self.assertLess(recoverable.net_revenue_local, recoverable.sale_price_local)

    def test_cheap_products_pay_the_fixed_fee_and_no_shipping(self):
        econ = compute_ml_economics(6990, quote(), self.market, self.costs)
        self.assertEqual(econ.fixed_fee_local, self.market.fixed_fee_local)
        self.assertEqual(econ.shipping_local, 0)

    def test_expensive_products_pay_shipping_and_no_fixed_fee(self):
        econ = compute_ml_economics(29990, quote(), self.market, self.costs)
        self.assertEqual(econ.fixed_fee_local, 0)
        self.assertGreater(econ.shipping_local, 0)

    def test_shipping_grows_with_weight(self):
        light = shipping_cost_local(300, self.market)
        heavy = shipping_cost_local(3000, self.market)
        self.assertLess(light, heavy)
        self.assertEqual(shipping_cost_local(50000, self.market), 7500.0)

    def test_a_bad_deal_shows_a_loss(self):
        econ = compute_ml_economics(8990, quote(price=9.0), self.market, self.costs)
        self.assertLess(econ.profit_local, 0)

    def test_upfront_investment_matches_the_order(self):
        econ = compute_ml_economics(24990, quote(moq=500), self.market, self.costs)
        self.assertEqual(econ.order_qty, 500)
        self.assertAlmostEqual(econ.upfront_investment_local, econ.landed_cost_local * 500, delta=500)


class IdeaScoreTests(unittest.TestCase):
    def market(self, listings, units, **kwargs):
        return MLMarket(query="q", site="MLC", total_listings=listings, currency="CLP",
                        monthly_units_est=units, median_price=15000, **kwargs)

    def test_more_sales_scores_higher(self):
        high, _, _ = demanda_ml_score(self.market(200, 500))
        low, _, _ = demanda_ml_score(self.market(200, 5))
        self.assertGreater(high, low)

    def test_more_listings_scores_lower(self):
        few, _, _ = competencia_ml_score(self.market(80, 200))
        many, _, _ = competencia_ml_score(self.market(4000, 200))
        self.assertGreater(few, many)

    def test_official_stores_and_concentration_hurt(self):
        base, _, _ = competencia_ml_score(self.market(300, 200))
        official, _, warnings = competencia_ml_score(
            self.market(300, 200, official_store_share=0.7, top_seller_share=0.6)
        )
        self.assertLess(official, base)
        self.assertEqual(len(warnings), 2)

    def test_without_a_quote_there_is_no_profit_score(self):
        score, reasons, warnings = ganancia_score(None)
        self.assertEqual(score, 0.0)
        self.assertEqual(reasons, [])
        self.assertTrue(warnings)

    def test_a_loss_is_flagged(self):
        econ = compute_ml_economics(8990, quote(price=9.0), MarketAssumptions(), CostAssumptions())
        _, reasons, warnings = ganancia_score(econ)
        self.assertEqual(reasons, [])
        self.assertTrue(any("no queda ganancia" in w for w in warnings))


class ScannerTests(unittest.TestCase):
    def setUp(self):
        self.scanner = NicheScanner(Settings())

    def test_scan_returns_ranked_ideas_with_every_stage_filled(self):
        result = self.scanner.scan(NicheScanRequest(niche="bano", max_terms=6))
        self.assertEqual(result.terms_scanned, 6)
        self.assertTrue(result.ideas)
        scores = [idea.total_score for idea in result.ideas]
        self.assertEqual(scores, sorted(scores, reverse=True))

        for idea in result.ideas:
            self.assertGreater(idea.ml_market.total_listings, 0)
            self.assertEqual(idea.ml_market.currency, "CLP")
            self.assertTrue(idea.quotes)
            self.assertIsNotNone(idea.economics)
            self.assertIn("alibaba.com", idea.alibaba_url)
            self.assertEqual(set(idea.scores), {"demanda", "competencia", "ganancia", "amazon"})
            self.assertTrue(idea.reasons or idea.warnings)

    def test_the_cheapest_supplier_is_not_always_the_chosen_one(self):
        # el elegido es el de mayor ganancia, y siempre queda primero en la lista
        idea = self.scanner.scan_term("organizador de ducha", [])
        self.assertEqual(idea.quotes[0].unit_price_usd, idea.economics.unit_cost_usd)

    def test_amazon_validation_finds_the_equivalent_product(self):
        idea = self.scanner.scan_term("organizador de ducha", [])
        self.assertTrue(idea.amazon_products)
        self.assertGreater(idea.amazon_monthly_units, 0)
        self.assertIn("Shower Caddy", idea.amazon_products[0].title)

    def test_custom_terms_skip_the_niche(self):
        result = self.scanner.scan(NicheScanRequest(terms=["filtro de ducha"]))
        self.assertEqual(len(result.ideas), 1)
        self.assertEqual(result.ideas[0].term, "filtro de ducha")
        self.assertEqual(result.niche_name, "búsqueda personalizada")

    def test_min_score_filters(self):
        everything = self.scanner.scan(NicheScanRequest(niche="bano", max_terms=8))
        filtered = self.scanner.scan(NicheScanRequest(niche="bano", max_terms=8, min_score=60))
        self.assertLessEqual(len(filtered.ideas), len(everything.ideas))
        self.assertTrue(all(i.total_score >= 60 for i in filtered.ideas))

    def test_unknown_niche_is_a_clear_error(self):
        with self.assertRaises(ValueError) as ctx:
            self.scanner.scan(NicheScanRequest(niche="submarinismo"))
        self.assertIn("submarinismo", str(ctx.exception))

    def test_a_broken_ml_source_does_not_kill_the_scan(self):
        class Boom:
            name = "boom"

            def market(self, query, limit=50):
                raise RuntimeError("ML caído")

        self.scanner.ml = Boom()
        result = self.scanner.scan(NicheScanRequest(niche="bano", max_terms=3))
        self.assertEqual(result.ideas, [])
        self.assertEqual(len(result.errors), 3)

    def test_results_are_deterministic(self):
        first = self.scanner.scan(NicheScanRequest(niche="bano", max_terms=5))
        second = self.scanner.scan(NicheScanRequest(niche="bano", max_terms=5))
        self.assertEqual(
            [(i.term, i.total_score) for i in first.ideas],
            [(i.term, i.total_score) for i in second.ideas],
        )


class IdeaStorageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.tmp.name) / "ideas.db")

    def tearDown(self):
        self.tmp.cleanup()

    def test_save_and_read_back(self):
        result = NicheScanner(Settings()).scan(NicheScanRequest(niche="bano", max_terms=5))
        conn = connect(self.db_path)
        run_id = save_niche_run(conn, result)

        self.assertEqual(latest_run_id(conn), run_id)
        rows = list_ideas(conn, run_id=run_id, limit=50)
        self.assertEqual(len(rows), len(result.ideas))
        self.assertEqual(rows[0]["currency"], "CLP")
        self.assertIn("alibaba.com", rows[0]["alibaba_url"])

        one = get_idea(conn, rows[0]["term"])
        self.assertEqual(one["term"], rows[0]["term"])
        conn.close()


class BuscarCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["DB_PATH"] = str(Path(self.tmp.name) / "cli.db")

    def tearDown(self):
        os.environ.pop("DB_PATH", None)
        self.tmp.cleanup()

    def _run(self, argv, expected_code=0):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(argv)
        self.assertEqual(code, expected_code)
        return buffer.getvalue()

    def test_buscar_prints_a_report(self):
        output = self._run(["buscar", "--max-terminos", "5", "--top", "3"])
        self.assertIn("Mercado Libre Chile (MLC)", output)
        self.assertIn("PUNTAJE", output)
        self.assertIn("DETALLE", output)
        self.assertIn("QUÉ HACER AHORA", output)
        self.assertIn("datos de EJEMPLO", output)   # avisa que no son datos reales

    def test_buscar_a_single_term(self):
        output = self._run(["buscar", "--termino", "filtro de ducha"])
        self.assertIn("filtro de ducha", output)
        self.assertIn("alibaba.com", output)

    def test_buscar_unknown_niche_fails_clearly(self):
        self._run(["buscar", "submarinismo"], expected_code=1)

    def test_nichos_lists_the_packs(self):
        output = self._run(["nichos"])
        self.assertIn("bano", output)
        self.assertIn("por defecto", output)


if __name__ == "__main__":
    unittest.main()

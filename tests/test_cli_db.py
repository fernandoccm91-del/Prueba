import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from productscout.cli import main
from productscout.config import Settings
from productscout.db import connect, get_opportunity, latest_run_id, list_opportunities, save_run
from productscout.keywords import alibaba_query, core_words, ml_query
from productscout.pipeline import Pipeline, ScanRequest


class KeywordTests(unittest.TestCase):
    def test_core_words_drop_brand_and_filler(self):
        words = core_words("Nordika Silicone Collapsible Travel Cup with Lid, 12 oz", "Nordika")
        self.assertNotIn("nordika", words)
        self.assertNotIn("with", words)
        self.assertIn("silicone", words)

    def test_ml_query_is_translated(self):
        self.assertEqual(ml_query("Magnetic Cable Organizer Clips, 6-Pack", "Kabelo"),
                         "magnetico cable organizador")

    def test_alibaba_query_is_generic(self):
        query = alibaba_query("Furly Pet Hair Remover Roller, Reusable, No Refills", "Furly")
        self.assertNotIn("furly", query.lower())
        self.assertTrue(query)


class DbTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.tmp.name) / "test.db")
        self.settings = Settings(db_path=self.db_path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_save_and_read_back_a_run(self):
        result = Pipeline(self.settings).scan(ScanRequest(keywords=[""], limit_per_keyword=50))
        conn = connect(self.db_path)
        run_id = save_run(conn, result)

        self.assertEqual(latest_run_id(conn), run_id)
        rows = list_opportunities(conn, run_id=run_id, limit=100)
        self.assertEqual(len(rows), len(result.opportunities))

        payload = json.loads(rows[0]["payload"])
        self.assertIn("product", payload)
        self.assertIn("scores", payload)

        one = get_opportunity(conn, rows[0]["asin"])
        self.assertEqual(one["asin"], rows[0]["asin"])
        conn.close()

    def test_filters_apply_on_read(self):
        result = Pipeline(self.settings).scan(ScanRequest(keywords=[""], limit_per_keyword=50))
        conn = connect(self.db_path)
        save_run(conn, result)
        high = list_opportunities(conn, min_score=60, limit=100)
        self.assertTrue(all(row["total_score"] >= 60 for row in high))
        conn.close()


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.tmp.name) / "cli.db")
        import os

        os.environ["DB_PATH"] = self.db_path

    def tearDown(self):
        import os

        os.environ.pop("DB_PATH", None)
        self.tmp.cleanup()

    def _run(self, argv: list[str]) -> str:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(argv)
        self.assertEqual(code, 0)
        return buffer.getvalue()

    def test_scan_then_list_then_show_then_export(self):
        output = self._run(["scan", "--top", "5", "--small-only"])
        self.assertIn("oportunidades", output)
        self.assertIn("SCORE", output)

        listed = self._run(["list", "--limit", "5"])
        self.assertIn("SCORE", listed)

        asin = None
        for line in listed.splitlines():
            for token in line.split():
                if token.startswith("B0") and len(token) == 10:
                    asin = token
                    break
            if asin:
                break
        self.assertIsNotNone(asin)

        detail = self._run(["show", asin])
        self.assertIn("ECONOMÍA UNITARIA", detail)
        self.assertIn("DEMANDA AMAZON", detail)

        out_file = str(Path(self.tmp.name) / "export.csv")
        self._run(["export", "--format", "csv", "--out", out_file])
        content = Path(out_file).read_text(encoding="utf-8")
        self.assertIn("asin,title", content)
        self.assertIn("alibaba.com", content)

    def test_show_unknown_asin_returns_error_code(self):
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["show", "B0NOEXISTE"])
        self.assertEqual(code, 1)

    def test_scan_json_output_is_valid(self):
        output = self._run(["scan", "--json", "--top", "3", "--keyword", "travel cup"])
        payload = json.loads(output[output.index("["):])
        self.assertTrue(payload)
        self.assertIn("total_score", payload[0])


if __name__ == "__main__":
    unittest.main()

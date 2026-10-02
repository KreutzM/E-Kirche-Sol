"""Regression checks for evidence integrity; no network or reconstruction geometry."""
from pathlib import Path
import contextlib
import csv
import importlib.util
import io
import json
import shutil
import tempfile
import unittest
from unittest.mock import patch
import yaml

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


validator = module("validate_dataset")
fetcher = module("fetch_assets")


class DatasetTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for folder in ("data", "sources", "validation"):
            shutil.copytree(ROOT / folder, self.root / folder)

    def change(self, path, edit):
        target = self.root / path
        value = yaml.safe_load(target.read_text(encoding="utf-8"))
        edit(value)
        target.write_text(yaml.safe_dump(value), encoding="utf-8")

    def errors(self):
        return "\n".join(validator.validate(self.root)[0])

    def test_baseline(self):
        self.assertEqual(validator.validate(self.root), ([], 32, 6, 0))

    def test_axes_and_origin(self):
        self.change("data/coordinate_system.yaml", lambda d: d["axes"].update(x_positive="west"))
        self.assertIn("coordinate axes", self.errors())
        self.change("data/coordinate_system.yaml", lambda d: d["origin"].update(definition="west portal"))
        self.assertIn("coordinate origin", self.errors())

    def test_dimension_source_and_nonfinite_value(self):
        self.change("data/dimensions.yaml", lambda d: d["tower_height"].update(source_id="missing", value=float("nan")))
        self.assertIn("unknown source_id", self.errors())
        self.assertIn("finite and positive", self.errors())

    def test_assumption_contract(self):
        assumption = dict(value=0.0, unit="m", reason="test only", confidence="low", evidence=["M01"], iteration="TEST")
        self.change("data/assumptions.yaml", lambda d: d["assumptions"].update(test=assumption))
        self.assertEqual(self.errors(), "")
        self.change("data/assumptions.yaml", lambda d: d["assumptions"]["test"].update(evidence=["UNKNOWN"], iteration=""))
        self.assertIn("unknown evidence ID", self.errors())
        self.assertIn("iteration must be nonempty", self.errors())

    def test_view_evidence(self):
        self.change("validation/reference_views.yaml", lambda d: d["views"]["W"].update(evidence=["UNKNOWN"]))
        self.assertIn("unknown evidence ID", self.errors())

    def test_malformed_files_report_errors(self):
        (self.root / "data/manifest.json").write_text("{broken", encoding="utf-8")
        (self.root / "data/dimensions.yaml").write_text("- not a mapping", encoding="utf-8")
        (self.root / "data/assumptions.yaml").write_text("assumptions:\n  bad: null", encoding="utf-8")
        self.assertIn("data/manifest.json", self.errors())
        self.assertIn("expected dict", self.errors())
        self.assertIn("assumption bad: expected mapping", self.errors())


class DownloadTests(unittest.TestCase):
    def test_license_policy(self):
        for name in ("CC BY-SA 4.0", "CC-BY 3.0", "CC0", "Public domain", "PDM", "GFDL 1.2"):
            self.assertTrue(fetcher.allowed(name), name)
        for name in ("", "CC BY-NC 4.0", "CC BY-ND 4.0", "CC BY-SA-NC", "not public domain", "unknown"):
            self.assertFalse(fetcher.allowed(name), name)

    def test_preservation_failure_status_and_csv(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "sources").mkdir()
            rec = dict(id="M01", title="reference.jpg", group="modern", priority=1, commons_page="test")
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps([rec]), encoding="utf-8")
            meta = root / "sources/meta.jsonl"
            meta.write_text('{"previous": true}\n', encoding="utf-8")
            report = root / "sources/report.csv"
            with patch.multiple(fetcher, ROOT=root, MANIFEST=manifest, META=meta, REPORT=report), patch.object(fetcher.time, "sleep"), contextlib.redirect_stdout(io.StringIO()):
                with patch.object(fetcher, "info", side_effect=RuntimeError('failure, "quoted"')):
                    self.assertEqual(fetcher.main([]), 1)
                with report.open(encoding="utf-8", newline="") as f:
                    self.assertEqual(list(csv.DictReader(f))[0]["error"], 'failure, "quoted"')
                dest = fetcher.destination(rec)
                dest.parent.mkdir(parents=True)
                dest.write_bytes(b"existing reference")
                with patch.object(fetcher, "info") as info:
                    self.assertEqual(fetcher.main([]), 0)
                    info.assert_not_called()
                self.assertEqual(dest.read_bytes(), b"existing reference")
                self.assertEqual(meta.read_text(encoding="utf-8"), '{"previous": true}\n')

    def test_success_records_local_provenance(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            rec = dict(id="M01", title="reference.jpg", group="modern", priority=1, commons_page="test")
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps([rec]), encoding="utf-8")
            meta = root / "sources/meta.jsonl"
            def download(url, dest):
                dest.parent.mkdir(parents=True)
                dest.write_bytes(b"downloaded")
            with patch.multiple(fetcher, ROOT=root, MANIFEST=manifest, META=meta, REPORT=root / "sources/report.csv"), patch.object(fetcher.time, "sleep"), patch.object(fetcher, "info", return_value=dict(license_short_name="CC BY 4.0", original_url="original", thumb_url="thumbnail")), patch.object(fetcher, "download", side_effect=download), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(fetcher.main([]), 0)
            record = json.loads(meta.read_text(encoding="utf-8"))
            self.assertEqual(record["download_url"], "thumbnail")
            self.assertEqual(len(record["local_sha256"]), 64)
            self.assertIn("downloaded_at_utc", record)


if __name__ == "__main__":
    unittest.main()

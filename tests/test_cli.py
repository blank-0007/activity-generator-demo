"""Tests for command-line behavior."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from activity_planner.cli import main


class CliTests(unittest.TestCase):
    def write_temp(self, suffix: str, content: str) -> Path:
        temporary = tempfile.NamedTemporaryFile(
            mode="w", suffix=suffix, encoding="utf-8", delete=False
        )
        temporary.write(content)
        temporary.close()
        path = Path(temporary.name)
        self.addCleanup(path.unlink, missing_ok=True)
        return path

    def run_cli(self, *arguments: str) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = main(list(arguments))
        return result, stdout.getvalue(), stderr.getvalue()

    def test_filters_json_with_inclusive_boundaries(self):
        path = self.write_temp(
            ".json",
            json.dumps([
                {"date": "2026-10-14", "repository": "api", "type": "commit", "count": 1},
                {"date": "2026-10-20", "repository": "web", "type": "issue", "count": 2},
                {"date": "2026-10-21", "repository": "web", "type": "commit", "count": 3},
            ]),
        )

        code, output, error = self.run_cli(
            "--input", str(path), "--from", "2026-10-14", "--to", "2026-10-20"
        )

        self.assertEqual(code, 0)
        self.assertEqual(error, "")
        self.assertIn("Records: 2", output)
        self.assertIn("Activity units: 3", output)
        self.assertNotIn("2026-10-21", output)

    def test_filters_csv_with_a_single_boundary(self):
        path = self.write_temp(
            ".csv",
            "date,repository,type,count\n2026-10-14,api,commit,1\n2026-10-20,web,issue,2\n",
        )

        code, output, error = self.run_cli("--input", str(path), "--from", "2026-10-20")

        self.assertEqual(code, 0)
        self.assertEqual(error, "")
        self.assertIn("Records: 1", output)
        self.assertIn("Activity units: 2", output)

    def test_returns_empty_summary_when_no_records_match(self):
        path = self.write_temp(
            ".json",
            json.dumps([{"date": "2026-10-14", "repository": "api", "type": "commit", "count": 1}]),
        )

        code, output, error = self.run_cli("--input", str(path), "--from", "2026-10-20")

        self.assertEqual(code, 0)
        self.assertEqual(error, "")
        self.assertIn("Records: 0", output)
        self.assertIn("Activity units: 0", output)

    def test_rejects_invalid_filter_dates(self):
        code, _, error = self.run_cli(
            "--input", "unused.json", "--from", "2026-02-30"
        )

        self.assertEqual(code, 2)
        self.assertIn("Invalid --from date '2026-02-30'; expected YYYY-MM-DD", error)

    def test_rejects_reversed_filter_dates(self):
        code, _, error = self.run_cli(
            "--input", "unused.json", "--from", "2026-10-21", "--to", "2026-10-20"
        )

        self.assertEqual(code, 2)
        self.assertIn("--from date cannot be after --to date", error)


if __name__ == "__main__":
    unittest.main()

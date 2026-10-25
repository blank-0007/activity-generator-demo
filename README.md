# GitHub Activity Planner

A small Python CLI that turns GitHub contribution data into readable activity summaries and practical next-step suggestions. Built as an approachable open-source project for developers who want to inspect their own public contribution history and plan consistent, meaningful work.

> **Project goal:** useful engineering practice, not artificially inflating contribution graphs. The tool never creates commits or edits repositories.

## Features

- Import contribution snapshots from JSON or CSV.
- Validate and normalize records before analysis.
- Summarize activity by day, repository, and event type.
- Identify quiet days and the most active repositories.
- Generate a Markdown report for a portfolio.
- Works offline with Python's standard library; no token or third-party package required.
- Unit tests for parsing, validation, aggregation, and report output.

## Quick start

Requires Python 3.10 or newer.

~~~bash
git clone https://github.com/Hariharans1971/activity-generator-demo.git
cd activity-generator-demo
python -m activity_planner --input examples/activity.json --format markdown --output activity-report.md
~~~

On Windows, use py instead of python if needed.

## Input format

JSON can be either a list of records or an object with an events list:

~~~json
{
  "events": [
    {"date": "2026-10-20", "repository": "demo-api", "type": "commit", "count": 2},
    {"date": "2026-10-20", "repository": "portfolio", "type": "pull_request", "count": 1}
  ]
}
~~~

CSV uses the same fields as a header row: date, repository, type, count. Dates must use YYYY-MM-DD. Counts must be non-negative integers. Duplicate records are aggregated in the summary.

## Commands

~~~bash
# Print a text summary to the terminal
python -m activity_planner --input examples/activity.json

# Write a Markdown report
python -m activity_planner --input examples/activity.json --format markdown --output report.md

# Read CSV input
python -m activity_planner --input examples/activity.csv --format markdown

# Summarize an inclusive date range (either --from or --to may be used alone)
python -m activity_planner --input examples/activity.json --from 2026-10-14 --to 2026-10-20
~~~

## Run tests

~~~bash
python -m unittest discover -s tests -v
~~~

## Project structure

~~~text
activity_planner/
  __init__.py
  __main__.py
  cli.py
  loader.py
  analysis.py
  report.py
examples/
  activity.json
  activity.csv
tests/
  test_loader.py
  test_analysis.py
  test_report.py
CONTRIBUTING.md
LICENSE
~~~

## Contributing

Issues and pull requests are welcome. Start with CONTRIBUTING.md, choose a focused improvement, add a test, and explain how you verified it.

Good first contributions include date-range filtering, additional report formats, better validation, and more edge-case tests. Please do not add fake activity records or automated commits just to increase contribution counts.

## Roadmap

- [x] JSON and CSV import
- [x] Local activity aggregation
- [x] Text and Markdown reports
- [x] Unit test suite
- [ ] Optional GitHub API import with explicit token handling
- [ ] Date range filters
- [ ] Optional charts

## License

MIT — see LICENSE.

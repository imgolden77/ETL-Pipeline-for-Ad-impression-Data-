
# ETL Pipeline for Twitter Ad Impression Data

A ETL utility that parses Twitter's ad-impressions.js JSON and loads ad impression records into a SQLite database using Python.

Important functions
- [`load_ad_json.load_json_from_js`](load_ad_json.py) — read and extract JSON payload from an ad-impressions.js file.
- [`load_ad_json.populate_db`](load_ad_json.py) — open SQLite DB and drive insertion.
- [`load_ad_json.json2db`](load_ad_json.py) — map JSON fields to the database tables.

Database Schema
- deviceInfo
- promotedTweetInfo
- advertiserInfo
- TargetingCriteria
- matchedTargetingCriteria
- impressions

Requirements
- Python 3 (uses standard library: json, sqlite3, argparse, pathlib)

Usage
```sh
python [load_ad_json.py](http://_vscodecontentref_/0) --source ./ad-impressions.js --output ./twitterads.db

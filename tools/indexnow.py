#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""IndexNow submitter (no login required).

Usage:
  python3 tools/indexnow.py https://insights.technologynova.org/p/0001/

Requires:
  - data/site.json contains base_url
  - an IndexNow key file exists at repo root named <key>.txt containing the key
"""

import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "site.json"

SITE = json.loads(DATA.read_text(encoding="utf-8"))
BASE = SITE["base_url"].rstrip("/")

# find key file
key_files = list(ROOT.glob("*.txt"))
key = None
for p in key_files:
  txt = p.read_text(encoding="utf-8").strip()
  if len(txt) >= 16 and txt == p.stem:
    key = txt
    break

if not key:
  raise SystemExit("IndexNow key file not found. Expected <key>.txt with matching content.")

urls = [u for u in sys.argv[1:] if u.startswith("http")]
if not urls:
  raise SystemExit("No URLs provided")

payload = {
  "host": "insights.technologynova.org",
  "key": key,
  "keyLocation": f"{BASE}/{key}.txt",
  "urlList": urls,
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(
  "https://api.indexnow.org/indexnow",
  data=data,
  headers={"Content-Type": "application/json; charset=utf-8"},
  method="POST",
)

try:
  with urllib.request.urlopen(req, timeout=20) as resp:
    print("IndexNow status:", resp.status)
except Exception as e:
  print("IndexNow error:", e)
  # don't hard-fail the whole pipeline
  sys.exit(0)

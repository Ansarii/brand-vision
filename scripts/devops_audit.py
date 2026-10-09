#!/usr/bin/env python3
"""
Brand Vision — Automated DevOps Quality & Invariant Audit Suite (October 2026)
Validates frontend integrity, assets, business invariants, SEO, and performance standards.
"""

import sys
import os
import re
import json
import subprocess
from bs4 import BeautifulSoup

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(WORKSPACE_ROOT)

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

failures = 0
warnings = 0

def pass_check(name):
    print(f"[{GREEN}PASS{RESET}] {name}")

def fail_check(name, reason):
    global failures
    failures += 1
    print(f"[{RED}FAIL{RESET}] {name}: {reason}")

def warn_check(name, reason):
    global warnings
    warnings += 1
    print(f"[{YELLOW}WARN{RESET}] {name}: {reason}")

print(f"\n{BLUE}=== Starting Brand Vision DevOps Quality Audit (Oct 2026 Standards) ==={RESET}\n")

# 1. HTML File Existence & Core Tags
if not os.path.exists("index.html"):
    fail_check("HTML Existence", "index.html not found!")
    sys.exit(1)

with open("index.html", "r", encoding="utf-8") as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, "html.parser")

# Check viewport & charset
meta_charset = soup.find("meta", charset=True)
meta_viewport = soup.find("meta", attrs={"name": "viewport"})
if meta_charset and meta_charset.get("charset", "").lower() == "utf-8":
    pass_check("HTML Meta: charset UTF-8")
else:
    fail_check("HTML Meta: charset", "Missing or invalid charset meta tag")

if meta_viewport and "width=device-width" in meta_viewport.get("content", ""):
    pass_check("HTML Meta: responsive viewport")
else:
    fail_check("HTML Meta: viewport", "Missing responsive viewport tag")

# Check GEO tags
geo_region = soup.find("meta", attrs={"name": "geo.region"})
if geo_region and "IN-TG" in geo_region.get("content", ""):
    pass_check("GEO SEO: meta geo.region (Hyderabad / Telangana)")
else:
    fail_check("GEO SEO", "Missing or invalid geo.region meta tag")

# 2. Asset Integrity (Zero Broken Local References)
local_assets = []
# Images
for img in soup.find_all("img"):
    src = img.get("src")
    if src and not src.startswith("http") and not src.startswith("data:"):
        local_assets.append(("img", src.split("?")[0]))

# Videos and sources
for vid in soup.find_all("video"):
    poster = vid.get("poster")
    if poster and not poster.startswith("http"):
        local_assets.append(("video poster", poster.split("?")[0]))
    for source in vid.find_all("source"):
        src = source.get("src")
        if src and not src.startswith("http"):
            local_assets.append(("video source", src.split("?")[0]))

# Stylesheets
for link in soup.find_all("link", rel="stylesheet"):
    href = link.get("href")
    if href and not href.startswith("http"):
        local_assets.append(("stylesheet", href.split("?")[0]))

# Scripts
for script in soup.find_all("script", src=True):
    src = script.get("src")
    if src and not src.startswith("http"):
        local_assets.append(("script", src.split("?")[0]))

broken_assets = []
for asset_type, path in local_assets:
    # strip leading slash if any
    clean_path = path.lstrip("/")
    if not os.path.exists(clean_path):
        broken_assets.append((asset_type, clean_path))

if not broken_assets:
    pass_check(f"Asset Integrity: All {len(local_assets)} local media and script references exist on disk")
else:
    fail_check("Asset Integrity", f"Found broken assets: {broken_assets}")

# 3. Business Invariant: Zero Emojis
emoji_pattern = re.compile(r'[\U00010000-\U0010ffff]', flags=re.UNICODE)
emoji_files = ["index.html", "assets/css/style.css", "assets/js/main.js", "llms.txt", "llms-full.txt"]
emojis_found = False
for fname in emoji_files:
    if os.path.exists(fname):
        with open(fname, "r", encoding="utf-8") as f:
            c = f.read()
        matches = emoji_pattern.findall(c)
        if matches:
            emojis_found = True
            fail_check(f"Zero Emojis Invariant: {fname}", f"Found prohibited emoji characters: {matches[:5]}")

if not emojis_found:
    pass_check("Zero Emojis Invariant: 100% clean across all HTML, CSS, JS, and LLM text files")

# 4. Business Invariant: Sole Partner Compliance
purged_names = ["Radhika", "Vamsi Krishna", "Vamsi"]
partner_violations = []
for p in purged_names:
    if re.search(r'\b' + re.escape(p) + r'\b', html_content):
        partner_violations.append(p)

if not partner_violations and "Sreedhar" in html_content:
    pass_check("Partner Compliance: Sole contact K. Sreedhar (+91 98853 35559) strictly maintained")
else:
    fail_check("Partner Compliance", f"Detected purged partner names in index.html: {partner_violations}")

# 5. CSS Syntax & Brace Balance
if os.path.exists("assets/css/style.css"):
    with open("assets/css/style.css", "r", encoding="utf-8") as f:
        css_text = f.read()
    open_b = css_text.count("{")
    close_b = css_text.count("}")
    if open_b == close_b:
        pass_check(f"CSS Syntax Integrity: Balanced braces ({open_b} open / {close_b} closed)")
    else:
        fail_check("CSS Syntax Integrity", f"Mismatched braces ({open_b} open vs {close_b} closed)")
else:
    fail_check("CSS Existence", "assets/css/style.css missing")

# 6. JavaScript Syntax Validation via Node.js
if os.path.exists("assets/js/main.js"):
    try:
        res = subprocess.run(["node", "-c", "assets/js/main.js"], capture_output=True, text=True)
        if res.returncode == 0:
            pass_check("JavaScript Syntax: Node.js AST compilation passed with 0 errors")
        else:
            fail_check("JavaScript Syntax", res.stderr.strip())
    except FileNotFoundError:
        warn_check("JavaScript Syntax", "Node.js not installed in environment, skipped syntax compilation")
else:
    fail_check("JS Existence", "assets/js/main.js missing")

# 7. Structured Data (JSON-LD) Validation
ld_scripts = soup.find_all("script", type="application/ld+json")
if ld_scripts:
    for i, s in enumerate(ld_scripts):
        try:
            data = json.loads(s.string)
            pass_check(f"JSON-LD Schema #{i+1}: Valid syntax")
            if "@graph" in data:
                types = [x.get("@type") for x in data["@graph"]]
                flattened = []
                for t in types:
                    if isinstance(t, list):
                        flattened.extend(t)
                    else:
                        flattened.append(t)
                has_business = any(b in flattened for b in ["AdvertisingAgency", "LocalBusiness"])
                has_video = "VideoObject" in flattened
                has_faq = "FAQPage" in flattened
                if has_business and has_video and has_faq:
                    pass_check("SEO & AI Knowledge Graph: Contains LocalBusiness, VideoObject, and FAQPage")
                else:
                    fail_check("SEO & AI Knowledge Graph", f"Missing key entities. Present: {flattened}")
        except Exception as e:
            fail_check(f"JSON-LD Schema #{i+1}", f"JSON parse error: {e}")
else:
    fail_check("JSON-LD Schema", "No application/ld+json script tag found")

# 8. LLM & Search Discovery Manifests
for manifest in ["robots.txt", "sitemap.xml", "llms.txt", "llms-full.txt"]:
    if os.path.exists(manifest) and os.path.getsize(manifest) > 50:
        pass_check(f"Search & AI Discovery: {manifest} present ({os.path.getsize(manifest)} bytes)")
    else:
        fail_check("Discovery Manifest", f"{manifest} missing or empty")

# Summary
print(f"\n{BLUE}=== Audit Completed ==={RESET}")
print(f"Total Failures: {failures}")
print(f"Total Warnings: {warnings}\n")

if failures > 0:
    print(f"{RED}Result: FAILED{RESET}")
    sys.exit(1)
else:
    print(f"{GREEN}Result: 100% PASSED (Production Ready){RESET}")
    sys.exit(0)

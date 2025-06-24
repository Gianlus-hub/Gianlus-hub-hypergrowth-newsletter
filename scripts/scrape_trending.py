#!/usr/bin/env python3
# scripts/scrape_trending.py

import requests, datetime, json
from bs4 import BeautifulSoup
import pandas as pd

# Config
LANGUAGE  = ""
SINCE     = "daily"
TOP_N     = 50
DELTA_N   = 20
PREV_FILE = "trending_prev.json"

def fetch_trending():
    url = f"https://github.com/trending/{LANGUAGE}?since={SINCE}"
    resp = requests.get(url); resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    out = []
    for art in soup.select("article.Box-row")[:TOP_N]:
        repo = art.h2.a.get_text(strip=True).replace(" / ", "/")
        url  = f"https://github.com/{repo}"
        # stars
        star_tag = art.find("a", href=lambda h: h and h.endswith("/stargazers"))
        stars    = int(star_tag.get_text(strip=True).replace(",", "")) if star_tag else 0
        # description
        desc_tag    = art.find("p", class_="col-9 color-fg-muted my-1 pr-4")
        description = desc_tag.get_text(strip=True) if desc_tag else ""
        # language
        lang_tag = art.find("span", itemprop="programmingLanguage")
        language = lang_tag.get_text(strip=True) if lang_tag else ""
        out.append({
            "repo":        repo,
            "url":         url,
            "description": description,
            "language":    language,
            "stars":       stars
        })
    return out

def main():
    today = datetime.date.today().isoformat()
    try:
        prev = json.load(open(PREV_FILE))
    except FileNotFoundError:
        prev = []
    prev_map = {r["repo"]: r["stars"] for r in prev}

    current = fetch_trending()
    for r in current:
        r["prev_stars"] = prev_map.get(r["repo"], 0)
        r["delta"]      = r["stars"] - r["prev_stars"]

    hot = sorted(current, key=lambda x: -x["delta"])[:DELTA_N]
    df = pd.DataFrame(hot)[[
        "repo","url","description","language","prev_stars","stars","delta"
    ]]
    out = f"hot_repos_{today}.csv"
    df.to_csv(out, index=False)
    print(f"✅ Saved top {DELTA_N} repos to {out}")

    json.dump(current, open(PREV_FILE,"w"), indent=2)

if __name__=="__main__":
    main()

import requests
from bs4 import BeautifulSoup
import json

BASE_URL = "https://www.shl.com/products/product-catalog/"

def scrape_shl_catalog():
    resp = requests.get(BASE_URL)
    soup = BeautifulSoup(resp.text, 'html.parser')

    assessments = []
    cards = soup.select('a.c-product-card')

    for card in cards:
        name = card.text.strip()
        url = card['href']
        if "pre-packaged" in url.lower():
            continue

        try:
            page = requests.get(url)
            inner = BeautifulSoup(page.text, 'html.parser')
            desc = inner.select_one('div.c-product-hero__summary')
            desc_text = desc.text.strip() if desc else ""
        except:
            desc_text = ""

        assessments.append({
            "name": name,
            "url": url,
            "description": desc_text
        })

    with open("data/assessments.json", "w", encoding="utf-8") as f:
        json.dump(assessments, f, indent=2, ensure_ascii=False)

    print(f"Extracted {len(assessments)} assessments")

if __name__ == "__main__":
    scrape_shl_catalog()
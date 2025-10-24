# app/parsing/anaf_loader.py
import re, hashlib, datetime as dt
import requests
from bs4 import BeautifulSoup

HEADINGS = {"h1","h2","h3","h4"}
ART_PAT = re.compile(r"\b(Art\.?|ART\.?)\s*\d+[A-Za-z]?(?:\s*\([\d\w]+\))*")

def fetch_html(url: str) -> tuple[str, str]:
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    html = r.text
    return html, hashlib.sha256(html.encode("utf-8")).hexdigest()

def extract_updated_on(soup: BeautifulSoup) -> str | None:
    # many ANAF pages show “actualizat în data de DD.MM.YYYY”
    txt = soup.get_text(" ", strip=True)
    m = re.search(r"actualizat(?:[^\d]{1,10})?(\d{2}\.\d{2}\.\d{4})", txt)
    return m.group(1) if m else None

def normalize_whitespace(t: str) -> str:
    return re.sub(r"\s+\n", "\n", re.sub(r"[ \t]+", " ", t)).strip()

def html_to_blocks(html: str):
    soup = BeautifulSoup(html, "lxml")
    updated_on = extract_updated_on(soup)

    # keep order; walk DOM and collect logical blocks by headings / article markers
    blocks = []
    buf, meta = [], {"heading": None, "article": None}
    def flush():
        if buf:
            raw = normalize_whitespace("\n".join(buf))
            if raw:
                blocks.append({"text": raw, "heading": meta["heading"], "article": meta["article"]})
            buf.clear()

    for el in soup.find_all(["h1","h2","h3","h4","p","li","table"]):
        tag = el.name.lower()
        text = normalize_whitespace(el.get_text(" ", strip=True))
        if not text:
            continue
        if tag in HEADINGS:
            flush()
            meta = {"heading": text, "article": None}
        else:
            # detect article marker inside text
            art = ART_PAT.search(text)
            if art:
                flush()
                meta["article"] = art.group(0)
            buf.append(text)
    flush()
    return blocks, updated_on

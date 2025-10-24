# scripts/ingest_anaf.py
import json, numpy as np, time
from app.parsing.anaf_loader import fetch_html, html_to_blocks
from app.parsing.chunking import chunk_blocks
from app.indexing.store import FaissStore
from app.indexing.embed import embed_texts  # your wrapper around Ollama embeddings

def ingest_source(url, version_year, store, source_id):
    html, sha = fetch_html(url)
    blocks, updated_on = html_to_blocks(html)
    chunks = chunk_blocks(blocks)

    texts = [c["text"] for c in chunks]
    vecs = embed_texts(texts)                     # -> np.ndarray [n, dim]
    metas = [{
        "source_url": url,
        "source_id": source_id,
        "version_year": version_year,
        "updated_on": updated_on,
        "heading": c["heading"],
        "article": c["article"],
        "hash": sha
    } for c in chunks]

    store.add(vecs, metas, texts)
    return {"n_chunks": len(chunks), "updated_on": updated_on, "hash": sha}

if __name__ == "__main__":
    store = FaissStore(dim=768)  # set to your embed dim
    sources = [
        ("anaf_cod_fiscal_2023", "https://static.anaf.ro/static/10/Anaf/legislatie/Cod_fiscal_norme_2023.htm", 2023),
        ("anaf_cod_fiscal_latest", "https://static.anaf.ro/static/10/Anaf/Legislatie_R/Codfiscal.htm", "latest")
    ]
    report = {sid: ingest_source(url, year, store, sid) for sid, url, year in sources}
    print(json.dumps(report, ensure_ascii=False, indent=2))

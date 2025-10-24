# app/indexing/store.py
import faiss, numpy as np
from dataclasses import dataclass

@dataclass
class KBItem:
    text: str
    meta: dict

class FaissStore:
    def __init__(self, dim: int):
        self.index = faiss.IndexFlatIP(dim)  # inner product -> cosine if vectors L2-normalized
        self.items: list[KBItem] = []

    def add(self, vectors: np.ndarray, metas: list[dict], texts: list[str]):
        # ensure L2 norm
        faiss.normalize_L2(vectors)
        self.index.add(vectors.astype(np.float32))
        for t, m in zip(texts, metas):
            self.items.append(KBItem(t, m))

    def search(self, qvec: np.ndarray, k=8):
        faiss.normalize_L2(qvec)
        D, I = self.index.search(qvec.astype(np.float32), k)
        return [(self.items[i], float(D[0, j])) for j, i in enumerate(I[0]) if i != -1]

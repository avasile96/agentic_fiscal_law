# app/parsing/chunking.py
def chunk_blocks(blocks, max_tokens=350, overlap=50, tkn=lambda s: len(s.split())):
    chunks = []
    cur, cur_len, cur_head, cur_art = [], 0, None, None
    for b in blocks:
        txt = b["text"]; h = b["heading"]; a = b["article"]
        if h is not None and h != cur_head:
            # close section before new heading
            if cur:
                chunks.append({"text":"\n".join(cur), "heading":cur_head, "article":cur_art})
                cur, cur_len = [], 0
            cur_head = h
        if a is not None and a != cur_art:
            if cur:
                chunks.append({"text":"\n".join(cur), "heading":cur_head, "article":cur_art})
                cur, cur_len = [], 0
            cur_art = a
        for para in txt.split("\n"):
            n = tkn(para)
            if cur_len + n > max_tokens and cur:
                chunks.append({"text":"\n".join(cur), "heading":cur_head, "article":cur_art})
                # soft overlap
                back = " ".join(" ".join(cur).split()[-overlap:]) if overlap else ""
                cur, cur_len = ([back] if back else []), tkn(back)
            cur.append(para); cur_len += n
    if cur:
        chunks.append({"text":"\n".join(cur), "heading":cur_head, "article":cur_art})
    return chunks

"""Классификация материала по осям тегов. Если задан ANTHROPIC_API_KEY —
через Claude; иначе эвристика по ключевым словам (демо-режим)."""
import os
import json
from . import config

TOPIC_IDS = [t["id"] for t in config.TOPICS]

# Эвристические маркеры для демо-режима
HEURISTICS = {
    "kya":    ["kya", "know your agent", "верификац", "audit", "мандат", "identity"],
    "agcom":  ["agentic commerce", "agent payments", "x402", "ap2", "acp", "stablecoin", "платеж"],
    "token":  ["token", "токен", "цфа", "rwa", "buidl", "стейблкоин", "актив"],
    "agmgmt": ["principal-agent", "governance", "mcp", "a2a", "агент", "manage"],
    "reg":    ["регулир", "цб", "закон", "aml", "regulation", "compliance"],
}
SRC_BY_DOMAIN = {
    "arxiv.org": "academic", "ssrn.com": "academic",
    "cbr.ru": "reg",
}


def _src_type(domain):
    if domain in SRC_BY_DOMAIN:
        return SRC_BY_DOMAIN[domain]
    if any(x in domain for x in ["rbc", "vedomosti", "news", "coindesk", "theblock", "habr", "digitalcommerce"]):
        return "news"
    return "industry"


GLOSSARY_TOKENS = {term.split(" (")[0].split(" ")[0].lower(): term.split(" (")[0]
                   for term, _, _ in config.GLOSSARY_SEED}


def _heuristic(text, domain):
    t = text.lower()
    scores = {tid: sum(t.count(m) for m in ms) for tid, ms in HEURISTICS.items()}
    topic = max(scores, key=scores.get) if any(scores.values()) else "agmgmt"
    tags = [label for tok, label in GLOSSARY_TOKENS.items() if tok in t]
    return {"topic": topic, "source_type": _src_type(domain), "tags": tags}


def classify(material):
    """material: {title, snippet, domain, region, ...} -> {topic, source_type, tags}"""
    text = f"{material.get('title','')} {material.get('snippet','')}"
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return _heuristic(text, material.get("domain", ""))
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key)
        prompt = (
            "Классифицируй материал по теме мониторинга (агентный менеджмент, токены, ИИ-агенты).\n"
            f"Заголовок: {material.get('title','')}\nФрагмент: {material.get('snippet','')}\n\n"
            f"Верни СТРОГО JSON: {{\"topic\": один из {TOPIC_IDS}, "
            "\"source_type\": один из [industry,news,academic,reg], "
            "\"tags\": [короткие теги-термины]}."
        )
        msg = client.messages.create(model=config.MODEL, max_tokens=300,
                                     messages=[{"role": "user", "content": prompt}])
        raw = msg.content[0].text
        raw = raw[raw.find("{"): raw.rfind("}") + 1]
        data = json.loads(raw)
        if data.get("topic") not in TOPIC_IDS:
            data["topic"] = "agmgmt"
        data.setdefault("source_type", _src_type(material.get("domain", "")))
        data.setdefault("tags", [])
        return data
    except Exception as e:
        print("classify fallback:", e)
        return _heuristic(text, material.get("domain", ""))

"""Оркестратор: поиск -> дедупликация -> классификация -> сборка data.json.
Запуск: python -m agent.build  (демо-режим работает без ключей)."""
import json
import hashlib
import datetime as dt
from collections import Counter, defaultdict

from . import config, search, classify, store


def _id(url):
    return "m" + hashlib.sha1(url.encode()).hexdigest()[:8]


def _token(term):
    """Ключевой токен термина для подсчёта упоминаний."""
    return term.split(" (")[0].split(" ")[0].lower()


def gather():
    """Собрать сырые материалы по всем регионам и ключевым словам, без дублей."""
    seen_urls, raw, in_run = store.load_seen(), [], set()
    for region, queries in config.KEYWORDS.items():
        for q in queries:
            for it in search.search(q, region):
                u = it.get("url")
                if not u or u in in_run:
                    continue
                in_run.add(u)
                raw.append(it)
    return raw, seen_urls


def to_materials(raw):
    out = []
    for it in raw:
        c = classify.classify(it)
        out.append({
            "id": _id(it["url"]),
            "date": it.get("published") or dt.date.today().isoformat(),
            "title": it.get("title", ""),
            "summary": it.get("snippet", ""),
            "url": it["url"],
            "topic": c["topic"],
            "region": it.get("region", "g"),
            "source_type": c.get("source_type", "industry"),
            "entity_type": "материал",
            "tags": c.get("tags", []),
            "saved": False,
        })
    return out


def momentum(materials):
    today = dt.date.today()
    weeks = config.WEEKS
    labels = [f"н-{weeks-1-i}" for i in range(weeks - 1)] + ["эта"]
    series = {t["id"]: [0] * weeks for t in config.TOPICS}
    for m in materials:
        try:
            d = dt.date.fromisoformat(m["date"])
        except Exception:
            continue
        wa = (today - d).days // 7
        idx = weeks - 1 - wa
        if 0 <= idx < weeks and m["topic"] in series:
            series[m["topic"]][idx] += 1
    return {"weeks": labels, "series": series}


def source_types(materials):
    cnt = Counter(m["source_type"] for m in materials)
    total = sum(cnt.values()) or 1
    out = []
    for s in config.SOURCE_TYPES:
        pct = round(100 * cnt.get(s["id"], 0) / total)
        out.append({**s, "value": pct})
    return out


def glossary(materials):
    blob = " ".join((m["title"] + " " + m["summary"]).lower() for m in materials)
    out = []
    for i, (term, topic, definition) in enumerate(config.GLOSSARY_SEED):
        occ = blob.count(_token(term))
        base = len(config.GLOSSARY_SEED) - i          # позиция даёт базовый вес
        out.append({"term": term, "topic": topic, "def": definition,
                    "mentions": base * 2 + occ})
    out.sort(key=lambda g: -g["mentions"])
    return out


def emerging_and_newtags(materials):
    canonical = {t.split(" (")[0].lower() for t, _, _ in config.GLOSSARY_SEED}
    tag_cnt = Counter()
    for m in materials:
        for t in m.get("tags", []):
            tag_cnt[t.lower()] += 1
    emerging = [{"term": t, "note": f"{c} упоминаний", "status": "up"}
                for t, c in tag_cnt.most_common(4)]
    new_tags = [{"tag": t, "facet": "Тема", "note": "новый термин, требует утверждения"}
                for t in tag_cnt if t not in canonical][:3]
    return emerging, new_tags


def watchlist():
    wl = [dict(w, date=dt.date.today().isoformat()) for w in config.WATCHLIST_SEED]
    for c in store.load_companies(config.COMPANIES_FILE):
        wl.insert(0, {"name": c.get("name"), "region": c.get("region", "ru"),
                      "focus": c.get("focus", []), "status": "на анализ",
                      "signal": "агент подбирает ключевые слова",
                      "site": c.get("site", ""), "user": True,
                      "date": dt.date.today().isoformat()})
    return wl


def radar(new_tags, companies):
    out = []
    for c in companies:
        out.append({"title": f"Новый игрок: {c.get('name')}",
                    "note": "добавлен на анализ · подбор ключевых слов",
                    "region": c.get("region", "ru"), "level": "наблюдать"})
    for t in new_tags:
        out.append({"title": f"Новое направление: {t['tag']}",
                    "note": t["note"], "region": "g", "level": "наблюдать"})
    return out


def build():
    raw, seen = gather()
    materials = to_materials(raw)
    materials.sort(key=lambda m: m["date"], reverse=True)

    today = dt.date.today()
    within = [m for m in materials
              if (today - dt.date.fromisoformat(m["date"])).days <= 7]
    emerging, new_tags = emerging_and_newtags(materials)
    companies = store.load_companies(config.COMPANIES_FILE)

    data = {
        "meta": {"updated": dt.datetime.utcnow().isoformat() + "Z",
                 "range_label": f"{config.WEEKS} недель"},
        "kpi": {"new_week": len(within), "new_week_delta_pct": 0,
                "total": len(seen) + len(materials),
                "academic": sum(1 for m in materials if m["source_type"] == "academic"),
                "new_terms": len(new_tags)},
        "topics": config.TOPICS,
        "regions": config.REGIONS,
        "source_types": source_types(materials),
        "momentum": momentum(materials),
        "emerging": emerging,
        "new_tags": new_tags,
        "glossary": glossary(materials),
        "materials": [{k: v for k, v in m.items() if k != "tags"} for m in materials],
        "watchlist": watchlist(),
        "radar": radar(new_tags, companies),
    }

    with open(config.OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    store.save_seen(seen | {m["url"] for m in materials})
    print(f"OK: {config.OUTPUT} · материалов {len(materials)} · "
          f"терминов {len(data['glossary'])} · watchlist {len(data['watchlist'])}")


if __name__ == "__main__":
    build()

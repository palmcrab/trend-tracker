"""Хранилище состояния: реестр «виденного» (дедупликация) и очередь компаний,
добавленных на дашборде. В облачной версии это заменяется на Airtable/Supabase."""
import json
import os

SEEN_FILE = "seen.json"


def _load(path, default):
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def load_seen():
    """Множество ключей (url), которые уже обрабатывались."""
    return set(_load(SEEN_FILE, {"urls": []}).get("urls", []))


def save_seen(urls):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump({"urls": sorted(urls)}, f, ensure_ascii=False, indent=2)


def load_companies(path):
    """Компании, добавленные пользователем на дашборде (очередь на анализ)."""
    data = _load(path, [])
    return data if isinstance(data, list) else data.get("queue", [])


def _issn_key(s):
    import re
    return re.sub(r"[^0-9Xx]", "", s or "").upper()


def load_scimago(path):
    """Опциональная таблица SCImago (ISSN → квартиль Q1–Q4), скачивается бесплатно
    с scimagojr.com. Возвращает {нормализованный_ISSN: 'Q1'|...}. Если файла нет — {}."""
    import csv
    out = {}
    if not os.path.exists(path):
        return out
    try:
        with open(path, encoding="utf-8", errors="ignore") as f:
            rd = csv.DictReader(f, delimiter=";")
            for row in rd:
                q = (row.get("SJR Best Quartile") or "").strip()
                if not q or q == "-":
                    continue
                for issn in (row.get("Issn") or "").split(","):
                    k = _issn_key(issn)
                    if k:
                        out[k] = q
    except Exception:
        pass
    return out

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

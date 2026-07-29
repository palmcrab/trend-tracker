"""Слой поиска. Если задан TAVILY_API_KEY — реальный веб-поиск через Tavily.
Иначе демо-режим: возвращает встроенный список материалов, чтобы конвейер
работал end-to-end без ключей."""
import os
import datetime as dt
import requests

TAVILY_URL = "https://api.tavily.com/search"


def _days_ago(n):
    return (dt.date.today() - dt.timedelta(days=n)).isoformat()


# Демо-набор «найденного» (используется без ключей).
DEMO = [
    {"title": "McKinsey: agentic commerce до $5 трлн к 2030", "url": "https://www.digitalcommerce360.com/2025/10/20/mckinsey-forecast-5-trillion-agentic-commerce-sales-2030/", "snippet": "ИИ-агенты сами ищут, торгуются и покупают; лояльность переосмысливается первой.", "published": _days_ago(0),  "domain": "digitalcommerce360.com", "region": "g"},
    {"title": "Skyfire привлекла $8,5 млн на инфраструктуру KYA", "url": "https://firecode.ru/blog/skyfire-8-5m", "snippet": "Основатели — экс-Google и Ripple. Верификация и платежи агентов, Know Your Agent.", "published": _days_ago(1), "domain": "firecode.ru", "region": "g"},
    {"title": "x402 передан под Linux Foundation; Google, Visa, Mastercard", "url": "https://www.datawallet.com/crypto/x402-protocol-explained", "snippet": "Открытый протокол платежей агентов; стандарт формализуется, стейблкоин USDC.", "published": _days_ago(2), "domain": "datawallet.com", "region": "g"},
    {"title": "Ларри Финк: токенизация как «интернет 1996»", "url": "https://www.blackrock.com/corporate/investor-relations/larry-fink-annual-chairmans-letter", "snippet": "Единый регулируемый кошелёк держит платежи и токенизированные активы, RWA.", "published": _days_ago(4), "domain": "blackrock.com", "region": "g"},
    {"title": "Ripple × BlackRock: RWA свыше $23 млрд on-chain", "url": "https://www.okx.com/en-gb/learn/ripple-blackrock-tokenized-finance", "snippet": "Обзор рынка токенизации реальных активов, BUIDL, роль ключевых игроков.", "published": _days_ago(5), "domain": "okx.com", "region": "g"},
    {"title": "arXiv: principal-agent theory для автономных ИИ-агентов", "url": "https://arxiv.org/abs/xxxx.xxxxx", "snippet": "Перенос агентской проблемы на ИИ; контроль через мандат и audit-log, agent governance.", "published": _days_ago(7), "domain": "arxiv.org", "region": "g"},
    {"title": "Visa и Mastercard запустили агентные платёжные инструменты", "url": "https://www.digitalcommerce360.com/2025/10/16/visa-mastercard-agentic/", "snippet": "Крупные платёжные сети выходят в agentic payments, AP2.", "published": _days_ago(9), "domain": "digitalcommerce360.com", "region": "g"},
    {"title": "Разбор письма Финка: токенизация как демократизация доступа", "url": "https://habr.com/ru/companies/finam_broker/articles/1017000/", "snippet": "Русскоязычный обзор: токенизация, ЦФА, прецеденты Индии и Японии.", "published": _days_ago(11), "domain": "habr.com", "region": "ru"},
    {"title": "ЦБ РФ: обновление регулирования ЦФА и цифровых прав", "url": "https://www.cbr.ru/press/", "snippet": "Правовая форма токена (ЦФА/УЦП), AML, защита клиента, регулирование.", "published": _days_ago(14), "domain": "cbr.ru", "region": "ru"},
]


def search(query, region, max_results=6):
    """Вернуть список результатов вида {title,url,snippet,published,domain,region}."""
    key = os.getenv("TAVILY_API_KEY")
    if not key:
        # демо-режим: отдаём релевантные региону материалы
        return [d for d in DEMO if d["region"] == region]
    try:
        r = requests.post(TAVILY_URL, json={
            "api_key": key, "query": query, "max_results": max_results,
            "search_depth": "basic", "include_answer": False,
        }, timeout=30)
        r.raise_for_status()
        out = []
        for it in r.json().get("results", []):
            dom = it.get("url", "").split("/")[2] if "://" in it.get("url", "") else ""
            out.append({"title": it.get("title", ""), "url": it.get("url", ""),
                        "snippet": it.get("content", "")[:280],
                        "published": it.get("published_date", "")[:10] or _days_ago(0),
                        "domain": dom, "region": region})
        return out
    except Exception as e:
        print("search error:", e)
        return []

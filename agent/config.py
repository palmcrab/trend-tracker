"""Конфигурация трекера трендов. Правьте здесь темы, регионы, источники,
ключевые слова поиска, канонические теги и стартовый watchlist."""

MODEL = "claude-sonnet-4-5"          # модель для классификации (если задан ANTHROPIC_API_KEY)
WEEKS = 8                            # окно динамики (недель)
OUTPUT = "data.json"                 # куда писать результат (рядом кладётся dashboard.html)
COMPANIES_FILE = "companies.json"    # очередь компаний, добавленных на дашборде

TOPICS = [
    {"id": "agmgmt", "label": "Агентный менеджмент", "color": "#2a78d6"},
    {"id": "kya",    "label": "KYA / доверие",       "color": "#eb6834"},
    {"id": "token",  "label": "Токенизация",         "color": "#1baf7a"},
    {"id": "agcom",  "label": "Агентная коммерция",  "color": "#eda100"},
    {"id": "reg",    "label": "Регулирование",       "color": "#e87ba4"},
]

REGIONS = [
    {"id": "g",  "label": "Глобальные лидеры", "desc": "США/ЕС — где задаётся тренд и формируются стандарты"},
    {"id": "w",  "label": "Остальной мир",     "desc": "прочие рынки, где идёт адаптация (MENA, Азия, Латам)"},
    {"id": "ru", "label": "РФ",                "desc": "российский рынок — целевой"},
]

SOURCE_TYPES = [
    {"id": "industry", "label": "Индустрия",     "color": "#2a78d6"},
    {"id": "news",     "label": "Новости",       "color": "#eb6834"},
    {"id": "academic", "label": "Академические", "color": "#1baf7a"},
    {"id": "reg",      "label": "Регулирование", "color": "#eda100"},
]

# Ключевые слова поиска по регионам (агент ищет отдельно по каждому)
KEYWORDS = {
    "g":  ["agentic commerce", "tokenization RWA", "know your agent KYA",
           "agent payments protocol", "AI agent governance"],
    "w":  ["tokenized loyalty MENA", "digital assets Asia regulation",
           "agentic payments emerging markets"],
    "ru": ["ЦФА платформа лояльность", "ИИ-агент финтех РФ",
           "токенизация цифровые права"],
}

# Белые списки авторитетных источников (домены) по регионам
SOURCE_WHITELIST = {
    "g":  ["mckinsey.com", "a16z.com", "blackrock.com", "coinbase.com",
           "theblock.co", "coindesk.com", "arxiv.org", "ssrn.com"],
    "w":  ["gulfnews.com", "channelnewsasia.com", "techinasia.com"],
    "ru": ["cbr.ru", "rbc.ru", "frankmedia.ru", "vedomosti.ru", "habr.com"],
}

# Стартовый watchlist (обязательный список игроков)
WATCHLIST_SEED = [
    {"name": "BlackRock",         "region": "g",  "focus": ["token"],          "status": "растёт",    "signal": "BUIDL: +фонды"},
    {"name": "Ripple",            "region": "g",  "focus": ["token", "agent"], "status": "растёт",    "signal": "RWA на XRPL"},
    {"name": "Coinbase",          "region": "g",  "focus": ["agent"],          "status": "растёт",    "signal": "x402 → Linux Foundation"},
    {"name": "Skyfire",           "region": "g",  "focus": ["agent"],          "status": "новое",     "signal": "раунд $8,5M · KYA"},
    {"name": "Visa / Mastercard", "region": "g",  "focus": ["agent"],          "status": "активен",   "signal": "агентные платежи"},
    {"name": "Google (AP2)",      "region": "g",  "focus": ["agent"],          "status": "активен",   "signal": "x402 как рельс"},
    {"name": "Сбер",              "region": "ru", "focus": ["token", "agent"], "status": "стабильно", "signal": "ЦФА + ИИ-ассистент"},
    {"name": "Т-Банк",            "region": "ru", "focus": ["token", "agent"], "status": "активен",   "signal": "лояльность + ИИ"},
    {"name": "Атомайз",           "region": "ru", "focus": ["token"],          "status": "растёт",    "signal": "ЦФА-платформа"},
    {"name": "Яндекс",            "region": "ru", "focus": ["agent"],          "status": "активен",   "signal": "ИИ-агенты"},
    {"name": "МТС Финтех",        "region": "ru", "focus": ["token", "agent"], "status": "наш",       "signal": "токен-лояльность + агент"},
]

# Канонический глоссарий (термин, тема, определение). Агент считает упоминания сам.
GLOSSARY_SEED = [
    ("Токенизация", "token", "Перенос права на актив в цифровую запись в реестре, которой можно управлять программно."),
    ("Agentic commerce (агентная коммерция)", "agcom", "Модель, где ИИ-агенты сами ищут, сравнивают, торгуются и покупают за человека."),
    ("KYA (Know Your Agent)", "kya", "Верификация ИИ-агента перед доступом и оплатой: идентичность, мандат, лимиты, аудит."),
    ("RWA (real-world assets)", "token", "Токенизированные реальные активы — облигации, фонды, недвижимость, private credit."),
    ("ЦФА (цифровые финансовые активы)", "token", "Правовая форма токена в РФ (259-ФЗ): денежные и эмиссионные права."),
    ("Principal-agent theory", "agmgmt", "Классическая агентская проблема управления; переносится на ИИ-агентов."),
    ("KYC (Know Your Customer)", "kya", "Установление и проверка личности клиента; основа доверия, KYA — надстройка."),
    ("x402", "agcom", "Открытый протокол Coinbase: агент мгновенно платит стейблкоином за один HTTP-запрос."),
    ("AP2 (Agent Payments Protocol)", "agcom", "Протокол Google для авторизации платежей агентов; использует x402."),
    ("Agent governance", "agmgmt", "Правила, мандаты и контроль автономных агентов, подотчётность."),
    ("Stablecoin (стейблкоин)", "agcom", "Криптомонета, привязанная к валюте (USDC); расчётный актив агентных платежей."),
    ("УЦП (утилитарные цифровые права)", "token", "«Полезное» цифровое право (товар/услуга/доступ) через инвестплатформы."),
    ("Scoped mandate", "kya", "Ограниченный мандат агента: что он вправе оплачивать, лимиты, срок."),
    ("MCP (Model Context Protocol)", "agmgmt", "Стандарт подключения инструментов и контекста к ИИ-моделям."),
    ("A2A (Agent-to-Agent)", "agmgmt", "Протокол взаимодействия агентов между собой."),
    ("Audit-log", "kya", "Неизменяемый журнал действий агента для подотчётности."),
    ("BUIDL", "token", "Токенизированный фонд денежного рынка BlackRock."),
    ("ACP (Agentic Commerce Protocol)", "agcom", "Формирующийся протокол агентной коммерции."),
    ("Breakage", "token", "Несписанные баллы/токены лояльности как источник экономики."),
    ("Loyalty OS", "agcom", "Открытая нейтральная платформа лояльности поверх платежей."),
]

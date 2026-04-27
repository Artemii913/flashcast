#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlashCast - RSS Parser v4.0
Изменения: расширен список источников, добавлена генерация podcasts.json с полем sources
"""

import feedparser
import json
import os
from datetime import datetime
from html import unescape
import re

CATEGORIES = {
    "news": {
        "name": "Новости",
        "sources": [
            {"name": "Коммерсантъ", "url": "https://www.kommersant.ru/RSS/news.xml",            "count": 2},
            {"name": "Медуза",      "url": "https://meduza.io/rss/all",                          "count": 2},
            {"name": "Интерфакс",   "url": "https://www.interfax.ru/rss.asp",                    "count": 2},
            {"name": "ТАСС",        "url": "https://tass.ru/rss/v2.xml",                         "count": 2},
        ]
    },
    "tech": {
        "name": "Технологии",
        "sources": [
            {"name": "Habr",   "url": "https://habr.com/ru/rss/best/daily/",    "count": 2},
            {"name": "3DNews", "url": "https://3dnews.ru/news/rss/",             "count": 2},
            {"name": "iXBT",   "url": "https://www.ixbt.com/export/news.rss",   "count": 2},
            {"name": "VC.ru",  "url": "https://vc.ru/rss",                       "count": 2},
        ]
    },
    "economy": {
        "name": "Экономика",
        "sources": [
            {"name": "РБК",          "url": "https://rssexport.rbc.ru/rbcnews/news/30/full.rss", "count": 2},
            {"name": "Ведомости",    "url": "https://www.vedomosti.ru/rss/rubric/economics",     "count": 2},
            {"name": "Forbes Russia","url": "https://www.forbes.ru/newrss.xml",                  "count": 2},
            {"name": "The Bell",     "url": "https://thebell.io/feed/",                          "count": 2},
        ]
    },
    "politics": {
        "name": "Политика",
        "sources": [
            {"name": "Коммерсантъ", "url": "https://www.kommersant.ru/RSS/section-politics.xml", "count": 3},
            {"name": "Интерфакс",   "url": "https://www.interfax.ru/rss.asp",                    "count": 3},
            {"name": "ТАСС",        "url": "https://tass.ru/rss/v2.xml",                         "count": 3},
        ]
    },
    "science": {
        "name": "Наука",
        "sources": [
            {"name": "N+1",          "url": "https://nplus1.ru/rss",              "count": 3},
            {"name": "Naked Science","url": "https://naked-science.ru/feed",      "count": 3},
            {"name": "Postnauka",    "url": "https://postnauka.org/feed",         "count": 3},
        ]
    },
    "culture": {
        "name": "Культура",
        "sources": [
            {"name": "Lenta Культура",         "url": "https://lenta.ru/rss/news/culture/",            "count": 2},
            {"name": "The Art Newspaper Russia","url": "https://www.theartnewspaper.ru/rss/",           "count": 2},
            {"name": "Афиша Daily",            "url": "https://daily.afisha.ru/rss/",                  "count": 2},
            {"name": "Colta.ru",               "url": "https://www.colta.ru/rss",                      "count": 2},
            {"name": "Газета.ру Культура",     "url": "https://www.gazeta.ru/export/rss/culture.xml",  "count": 2},
        ]
    },
    "sport": {
        "name": "Спорт",
        "sources": [
            {"name": "Sports.ru",  "url": "https://www.sports.ru/rss/main.xml",   "count": 4},
            {"name": "Lenta Спорт","url": "https://lenta.ru/rss/news/sport/",     "count": 4},
            {"name": "Soccer.ru",  "url": "https://www.soccer.ru/rss/",           "count": 4},
        ]
    },
}

# Метаданные карточек для фронтенда (статические поля, не меняются при парсинге)
PODCAST_CARDS = [
    {
        "id": 0,
        "title": "Все новости дня — полный дайджест",
        "category": "Все новости",
        "date": "Сегодня",
        "duration": "25:00",
        "image": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=400&h=300&fit=crop",
        "audio": "data/podcast_all.mp3",
        "featured": True,
        "keywords": ["новости","дайджест","все","главное","сегодня","день","обзор"],
        "cat_id": "all",
    },
    {
        "id": 1,
        "title": "Технологии: AI, гаджеты и IT",
        "category": "Технологии",
        "date": "Сегодня",
        "duration": "10:00",
        "image": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=400&h=300&fit=crop",
        "audio": "data/podcast_tech.mp3",
        "featured": False,
        "keywords": ["технологии","tech","it","гаджеты","apple","google","ai","искусственный интеллект","программирование","код","смартфон","компьютер","робот"],
        "cat_id": "tech",
    },
    {
        "id": 2,
        "title": "Экономика: курсы, биржи, финансы",
        "category": "Экономика",
        "date": "Сегодня",
        "duration": "8:00",
        "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=400&h=300&fit=crop",
        "audio": "data/podcast_economy.mp3",
        "featured": False,
        "keywords": ["экономика","финансы","деньги","курс","валюта","доллар","евро","рубль","биржа","акции","инвестиции","бизнес","банк","кризис"],
        "cat_id": "economy",
    },
    {
        "id": 3,
        "title": "Спорт: матчи, результаты, трансферы",
        "category": "Спорт",
        "date": "Сегодня",
        "duration": "12:00",
        "image": "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=400&h=300&fit=crop",
        "audio": "data/podcast_sport.mp3",
        "featured": False,
        "keywords": ["спорт","футбол","хоккей","баскетбол","теннис","матч","чемпионат","олимпиада","гол","команда","игрок","трансфер","лига"],
        "cat_id": "sport",
    },
    {
        "id": 4,
        "title": "Политика: события и заявления",
        "category": "Политика",
        "date": "Сегодня",
        "duration": "9:00",
        "image": "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=400&h=300&fit=crop",
        "audio": "data/podcast_politics.mp3",
        "featured": False,
        "keywords": ["политика","выборы","президент","правительство","закон","реформа","депутат","министр","санкции","мир","война"],
        "cat_id": "politics",
    },
    {
        "id": 5,
        "title": "Наука: открытия и исследования",
        "category": "Наука",
        "date": "Сегодня",
        "duration": "11:00",
        "image": "https://images.unsplash.com/photo-1507413245164-6160d8298b31?w=400&h=300&fit=crop",
        "audio": "data/podcast_science.mp3",
        "featured": False,
        "keywords": ["наука","космос","физика","биология","открытие","исследование","ученые","nasa","марс","ракета","медицина","днк","атом"],
        "cat_id": "science",
    },
    {
        "id": 6,
        "title": "Культура: кино, музыка, искусство",
        "category": "Культура",
        "date": "Сегодня",
        "duration": "10:00",
        "image": "https://images.unsplash.com/photo-1499364615650-ec38552f4f34?w=400&h=300&fit=crop",
        "audio": "data/podcast_culture.mp3",
        "featured": False,
        "keywords": ["культура","кино","фильм","музыка","театр","выставка","искусство","концерт","премьера","актер","режиссер","оскар","книга"],
        "cat_id": "culture",
    },
]


def clean_html(text):
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = unescape(clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean


def truncate_text(text, max_length=300):
    if len(text) <= max_length:
        return text
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    if last_space > 0:
        truncated = truncated[:last_space]
    return truncated + "..."


def fetch_news(sources):
    """
    Загружает новости из списка источников без дубликатов.
    Возвращает (news_list, used_sources) — новости и имена источников,
    реально отдавших хотя бы одну запись.
    """
    news_list = []
    seen_titles = set()
    used_sources = []

    for source in sources:
        try:
            print(f"  Загружаю: {source['name']}")
            feed = feedparser.parse(source['url'])
            if not feed.entries:
                print(f"    [!] Нет записей")
                continue

            source_contributed = False
            count = 0
            for entry in feed.entries:
                if count >= source['count']:
                    break

                title = clean_html(entry.get('title', ''))
                title_lower = title.lower().strip()
                if title_lower in seen_titles:
                    print(f"    [dup] {title[:40]}...")
                    continue

                seen_titles.add(title_lower)
                description = clean_html(entry.get('summary', '') or entry.get('description', ''))
                description = truncate_text(description)

                news_list.append({
                    "title": title,
                    "description": description,
                    "source": source['name'],
                })
                print(f"    + {title[:50]}...")
                count += 1
                source_contributed = True

            if source_contributed:
                used_sources.append(source['name'])

        except Exception as e:
            print(f"  ❌ Ошибка {source['name']}: {e}")

    return news_list, used_sources


def fetch_all_news():
    """Загружает все новости из всех категорий без дубликатов."""
    all_news = []
    seen_titles = set()

    for cat_id, cat_info in CATEGORIES.items():
        print(f"\n[{cat_info['name']}]")
        news, _ = fetch_news(cat_info['sources'])

        for item in news:
            title_lower = item['title'].lower().strip()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                item['category'] = cat_info['name']
                all_news.append(item)

    return all_news


def generate_script(category_name, news_list):
    today = datetime.now().strftime("%d.%m.%Y")
    script = f"Привет! Это FlashCast — {category_name}. Сегодня {today}.\n\n"
    for item in news_list:
        script += f"{item['title']}.\n"
        if item['description']:
            script += f"{item['description']}\n"
        script += "\n"
    script += f"Это были новости — {category_name}. Спасибо что слушаете FlashCast!\n"
    return script


def generate_podcast_script(news_list):
    today = datetime.now().strftime("%d.%m.%Y")
    script = f"Привет! Это FlashCast — ваш ежедневный дайджест. Сегодня {today}.\n\n"
    categories_news = {}
    for item in news_list:
        cat = item.get('category', 'Разное')
        if cat not in categories_news:
            categories_news[cat] = []
        categories_news[cat].append(item)
    for category, news in categories_news.items():
        script += f"--- {category} ---\n\n"
        for item in news:
            script += f"{item['title']}.\n"
            if item['description']:
                script += f"{item['description']}\n"
            script += "\n"
    script += "Это был FlashCast. Спасибо что слушаете! До завтра!\n"
    return script


def main():
    print("=" * 50)
    print("FlashCast RSS Parser v4.0")
    print("=" * 50)
    os.makedirs("data", exist_ok=True)

    all_data = {}
    all_news_combined = []
    all_used_sources = []   # все источники, отдавшие хоть что-то за этот прогон
    global_seen = set()

    # cat_id → список реально использованных источников
    used_sources_by_cat = {}

    for cat_id, cat_info in CATEGORIES.items():
        print(f"\n[{cat_info['name']}]")
        news, used = fetch_news(cat_info['sources'])

        unique_news = []
        for item in news:
            title_lower = item['title'].lower().strip()
            if title_lower not in global_seen:
                global_seen.add(title_lower)
                item['category'] = cat_info['name']
                unique_news.append(item)

        used_sources_by_cat[cat_id] = used

        if unique_news:
            script = generate_script(cat_info['name'], unique_news)
            script_file = f"data/script_{cat_id}.txt"
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script)
            print(f"  OK {script_file} ({len(unique_news)} новостей, источники: {', '.join(used)})")
            all_data[cat_id] = {"name": cat_info['name'], "news_count": len(unique_news)}
            all_news_combined.extend(unique_news)
            for s in used:
                if s not in all_used_sources:
                    all_used_sources.append(s)

    # Скрипт «все новости»
    print(f"\n[Все новости]")
    if all_news_combined:
        script = generate_podcast_script(all_news_combined)
        with open("data/script.txt", 'w', encoding='utf-8') as f:
            f.write(script)
        print(f"  OK data/script.txt ({len(all_news_combined)} новостей)")

    # categories.json
    with open("data/categories.json", 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    # podcasts.json — обновляем поле sources для каждой карточки
    today_str = datetime.now().strftime("%d.%m.%Y")
    podcasts = []
    for card in PODCAST_CARDS:
        cat_id = card["cat_id"]
        if cat_id == "all":
            sources_used = all_used_sources
        else:
            sources_used = used_sources_by_cat.get(cat_id, [])

        entry = {k: v for k, v in card.items() if k != "cat_id"}
        entry["date"] = today_str
        entry["sources"] = sources_used
        podcasts.append(entry)

    with open("data/podcasts.json", 'w', encoding='utf-8') as f:
        json.dump(podcasts, f, ensure_ascii=False, indent=2)
    print(f"\n  OK data/podcasts.json (sources для {len(podcasts)} карточек)")

    print("\n" + "=" * 50)
    print(f"DONE! Всего: {len(all_news_combined)} уникальных новостей")
    print(f"   Источники: {', '.join(all_used_sources)}")


if __name__ == "__main__":
    main()

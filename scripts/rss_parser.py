#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlashCast - RSS Parser v3.0
Добавлены: Экономика, Политика
"""

import feedparser
import json
import os
from datetime import datetime
from html import unescape
import re

# ============================================
# КАТЕГОРИИ И ИСТОЧНИКИ
# ============================================
CATEGORIES = {
    "news": {
        "name": "Новости",
        "sources": [
            {"name": "Коммерсантъ", "url": "https://www.kommersant.ru/RSS/news.xml", "count": 3},
            {"name": "Медуза", "url": "https://meduza.io/rss/all", "count": 3},
        ]
    },
    "tech": {
        "name": "Технологии",
        "sources": [
            {"name": "Habr", "url": "https://habr.com/ru/rss/best/daily/", "count": 2},
            {"name": "3DNews", "url": "https://3dnews.ru/news/rss/", "count": 2},
        ]
    },
    "economy": {
        "name": "Экономика",
        "sources": [
            {"name": "РБК Экономика", "url": "https://rssexport.rbc.ru/rbcnews/news/30/full.rss", "count": 2},
            {"name": "Ведомости Экономика", "url": "https://www.vedomosti.ru/rss/rubric/economics", "count": 2},
        ]
    },
    "politics": {
        "name": "Политика",
        "sources": [
            {"name": "РИА Политика", "url": "https://ria.ru/export/rss2/politics/index.xml", "count": 2},
            {"name": "Lenta Политика", "url": "https://lenta.ru/rss/news/russia/politics", "count": 2},
        ]
    },
    "science": {
        "name": "Наука", 
        "sources": [
            {"name": "N+1", "url": "https://nplus1.ru/rss", "count": 4},
        ]
    },
    "culture": {
        "name": "Культура",
        "sources": [
            {"name": "Lenta Культура", "url": "https://lenta.ru/rss/news/culture", "count": 2},
            {"name": "РИА Культура", "url": "https://ria.ru/export/rss2/culture/index.xml", "count": 2},
        ]
    },
    "sport": {
        "name": "Спорт",
        "sources": [
            {"name": "Sports.ru", "url": "https://www.sports.ru/rss/main.xml", "count": 4},
        ]
    }
}

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
    news_list = []
    for source in sources:
        try:
            print(f"  Загружаю: {source['name']}")
            feed = feedparser.parse(source['url'])
            if not feed.entries:
                print(f"    ⚠️ Нет записей")
                continue
            for entry in feed.entries[:source['count']]:
                title = clean_html(entry.get('title', ''))
                description = clean_html(entry.get('summary', '') or entry.get('description', ''))
                description = truncate_text(description)
                news_list.append({
                    "title": title,
                    "description": description,
                    "source": source['name']
                })
                print(f"    + {title[:50]}...")
        except Exception as e:
            print(f"  ❌ Ошибка {source['name']}: {e}")
    return news_list

def fetch_all_news():
    all_news = []
    for cat_id, cat_info in CATEGORIES.items():
        print(f"\n📁 {cat_info['name']}")
        news = fetch_news(cat_info['sources'])
        for item in news:
            item['category'] = cat_info['name']
        all_news.extend(news)
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
    print("FlashCast RSS Parser v3.0")
    print("=" * 50)
    os.makedirs("data", exist_ok=True)
    all_data = {}
    all_news_combined = []
    
    for cat_id, cat_info in CATEGORIES.items():
        print(f"\n📁 {cat_info['name']}")
        news = fetch_news(cat_info['sources'])
        if news:
            for item in news:
                item['category'] = cat_info['name']
            script = generate_script(cat_info['name'], news)
            script_file = f"data/script_{cat_id}.txt"
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script)
            print(f"  ✓ {script_file}")
            all_data[cat_id] = {"name": cat_info['name'], "news_count": len(news)}
            all_news_combined.extend(news)
    
    print(f"\n📁 Все новости")
    if all_news_combined:
        script = generate_podcast_script(all_news_combined)
        with open("data/script.txt", 'w', encoding='utf-8') as f:
            f.write(script)
        print(f"  ✓ data/script.txt")
    
    with open("data/categories.json", 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 50)
    print(f"✅ Готово! Новостей: {len(all_news_combined)}")

if __name__ == "__main__":
    main()

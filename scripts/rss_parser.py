#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FlashCast - RSS Parser с разделением по категориям
"""

import feedparser
import json
import os
from datetime import datetime
from html import unescape
import re

# Категории и их источники
CATEGORIES = {
    "news": {
        "name": "Новости",
        "sources": [
            {"name": "Коммерсантъ", "url": "https://www.kommersant.ru/RSS/news.xml", "count": 3},
            {"name": "Медуза", "url": "https://meduza.io/rss/all", "count": 3},
        ]
    },
    "science": {
        "name": "Наука", 
        "sources": [
            {"name": "N+1", "url": "https://nplus1.ru/rss", "count": 4},
        ]
    },
    "tech": {
        "name": "Технологии",
        "sources": [
            {"name": "Habr", "url": "https://habr.com/ru/rss/best/daily/", "count": 2},
            {"name": "3DNews", "url": "https://3dnews.ru/news/rss/", "count": 2},
        ]
    },
    "culture": {
        "name": "Культура",
        "sources": [
            {"name": "Афиша Daily", "url": "https://daily.afisha.ru/feed/", "count": 4},
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
            print(f"  Ошибка {source['name']}: {e}")
    return news_list

def generate_script(category_name, news_list):
    today = datetime.now().strftime("%d.%m.%Y")
    script = f"Привет! Это FlashCast — {category_name}. Сегодня {today}.\n\n"
    for item in news_list:
        script += f"{item['title']}.\n"
        if item['description']:
            script += f"{item['description']}\n"
        script += "\n"
    script += f"Это были новости в категории {category_name}. Спасибо что слушаете FlashCast!\n"
    return script

def main():
    print("=" * 50)
    print("FlashCast - Генерация подкастов по категориям")
    print("=" * 50)
    
    os.makedirs("data", exist_ok=True)
    
    all_data = {}
    
    for cat_id, cat_info in CATEGORIES.items():
        print(f"\n📁 Категория: {cat_info['name']}")
        
        # Собираем новости
        news = fetch_news(cat_info['sources'])
        
        if news:
            # Генерируем текст
            script = generate_script(cat_info['name'], news)
            
            # Сохраняем текст
            script_file = f"data/script_{cat_id}.txt"
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(script)
            print(f"  ✓ Сохранено: {script_file}")
            
            all_data[cat_id] = {
                "name": cat_info['name'],
                "news_count": len(news),
                "script_file": script_file
            }
    
    # Также создаём общий скрипт (все новости)
    print(f"\n📁 Категория: Все новости")
    all_news = []
    for cat_id, cat_info in CATEGORIES.items():
        all_news.extend(fetch_news(cat_info['sources'][:1]))  # По 1 источнику
    
    if all_news:
        script = generate_script("Все новости", all_news)
        with open("data/script.txt", 'w', encoding='utf-8') as f:
            f.write(script)
        print(f"  ✓ Сохранено: data/script.txt")
    
    # Сохраняем метаданные
    with open("data/categories.json", 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 50)
    print("✅ Готово!")
    print("=" * 50)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================
FlashCast - RSS Parser с разделением по категориям
============================================
Версия: 2.0
Изменения:
- Обновлены источники для культуры (Lenta + РИА)
- Добавлены функции для main.py
============================================
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
            # Lenta — мировые новости культуры (Голливуд, фестивали, искусство)
            {"name": "Lenta Культура", "url": "https://lenta.ru/rss/news/culture", "count": 2},
            # РИА — официальные новости культуры России и мира
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


# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def clean_html(text):
    """Очищает текст от HTML-тегов."""
    if not text:
        return ""
    clean = re.sub(r'<[^>]+>', '', text)
    clean = unescape(clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean


def truncate_text(text, max_length=300):
    """Обрезает текст до указанной длины."""
    if len(text) <= max_length:
        return text
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    if last_space > 0:
        truncated = truncated[:last_space]
    return truncated + "..."


# ============================================
# ОСНОВНЫЕ ФУНКЦИИ ПАРСИНГА
# ============================================

def fetch_news(sources):
    """
    Загружает новости из списка источников.
    
    Args:
        sources: Список источников с url и count
        
    Returns:
        Список новостей
    """
    news_list = []
    
    for source in sources:
        try:
            print(f"  Загружаю: {source['name']}")
            feed = feedparser.parse(source['url'])
            
            if not feed.entries:
                print(f"    ⚠️ Нет записей в {source['name']}")
                continue
                
            for entry in feed.entries[:source['count']]:
                title = clean_html(entry.get('title', ''))
                description = clean_html(
                    entry.get('summary', '') or entry.get('description', '')
                )
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


def fetch_category_news(category_id):
    """
    Загружает новости для одной категории.
    
    Args:
        category_id: ID категории (news, tech, culture и т.д.)
        
    Returns:
        Список новостей с полем category
    """
    if category_id not in CATEGORIES:
        print(f"❌ Категория {category_id} не найдена")
        return []
    
    cat_info = CATEGORIES[category_id]
    news = fetch_news(cat_info['sources'])
    
    # Добавляем категорию к каждой новости
    for item in news:
        item['category'] = cat_info['name']
    
    return news


def fetch_all_news():
    """
    Загружает новости из ВСЕХ категорий.
    Используется в main.py для генерации общего подкаста.
    
    Returns:
        Список всех новостей со всеми полями
    """
    all_news = []
    
    for cat_id, cat_info in CATEGORIES.items():
        print(f"\n📁 Категория: {cat_info['name']}")
        news = fetch_news(cat_info['sources'])
        
        # Добавляем категорию к каждой новости
        for item in news:
            item['category'] = cat_info['name']
        
        all_news.extend(news)
    
    return all_news


# ============================================
# ГЕНЕРАЦИЯ ТЕКСТА ПОДКАСТА
# ============================================

def generate_script(category_name, news_list):
    """
    Генерирует текст подкаста для одной категории.
    """
    today = datetime.now().strftime("%d.%m.%Y")
    
    script = f"Привет! Это FlashCast — {category_name}. Сегодня {today}.\n\n"
    
    for item in news_list:
        script += f"{item['title']}.\n"
        if item['description']:
            script += f"{item['description']}\n"
        script += "\n"
    
    script += f"Это были новости в категории {category_name}. "
    script += "Спасибо что слушаете FlashCast!\n"
    
    return script


def generate_podcast_script(news_list):
    """
    Генерирует текст общего подкаста (все новости).
    Используется в main.py.
    
    Args:
        news_list: Список новостей из fetch_all_news()
        
    Returns:
        Текст подкаста
    """
    today = datetime.now().strftime("%d.%m.%Y")
    
    script = f"Привет! Это FlashCast — ваш ежедневный новостной подкаст. "
    script += f"Сегодня {today}.\n\n"
    
    # Группируем по категориям
    categories_news = {}
    for item in news_list:
        cat = item.get('category', 'Разное')
        if cat not in categories_news:
            categories_news[cat] = []
        categories_news[cat].append(item)
    
    # Генерируем текст по категориям
    for category, news in categories_news.items():
        script += f"--- {category} ---\n\n"
        for item in news:
            script += f"{item['title']}.\n"
            if item['description']:
                script += f"{item['description']}\n"
            script += "\n"
    
    script += "Это был FlashCast. Спасибо что слушаете! "
    script += "Увидимся завтра!\n"
    
    return script


# ============================================
# ГЛАВНАЯ ФУНКЦИЯ (для запуска напрямую)
# ============================================

def main():
    """
    Основная функция — парсит все категории и сохраняет скрипты.
    Запускается из workflow: python scripts/rss_parser.py
    """
    print("=" * 50)
    print("FlashCast - Генерация подкастов по категориям")
    print("=" * 50)
    
    # Создаём папку data
    os.makedirs("data", exist_ok=True)
    
    all_data = {}
    all_news_combined = []
    
    # Парсим каждую категорию
    for cat_id, cat_info in CATEGORIES.items():
        print(f"\n📁 Категория: {cat_info['name']}")
        
        # Собираем новости
        news = fetch_news(cat_info['sources'])
        
        if news:
            # Добавляем категорию
            for item in news:
                item['category'] = cat_info['name']
            
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
            
            # Добавляем в общий список
            all_news_combined.extend(news)
        else:
            print(f"  ⚠️ Нет новостей для {cat_info['name']}")
    
    # Создаём общий скрипт (все новости)
    print(f"\n📁 Категория: Все новости")
    if all_news_combined:
        script = generate_podcast_script(all_news_combined)
        with open("data/script.txt", 'w', encoding='utf-8') as f:
            f.write(script)
        print(f"  ✓ Сохранено: data/script.txt")
    
    # Сохраняем метаданные
    with open("data/categories.json", 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 50)
    print("✅ Готово!")
    print(f"   Всего новостей: {len(all_news_combined)}")
    print("=" * 50)


if __name__ == "__main__":
    main()

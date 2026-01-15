#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================
FlashCast — RSS Parser (Парсер новостей)
============================================
Описание:
    Скрипт собирает новости с RSS-лент различных источников.
    Берёт по 2 свежих новости с каждого сайта.

Источники:
    - Коммерсантъ (новости)
    - Медуза (новости)
    - N+1 (наука)
    - Habr (технологии)
    - 3DNews (технологии)
    - Афиша Daily (культура)
    - Sports.ru (спорт)

Использование:
    python rss_parser.py

Зависимости:
    pip install feedparser requests
============================================
"""

import feedparser
import requests
from datetime import datetime
from typing import List, Dict, Optional
import json
import logging
import re
from html import unescape

# ============================================
# НАСТРОЙКА ЛОГИРОВАНИЯ
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('FlashCast')


# ============================================
# КОНФИГУРАЦИЯ RSS-ИСТОЧНИКОВ
# ============================================
RSS_SOURCES = [
    {
        "name": "Коммерсантъ",
        "url": "https://www.kommersant.ru/RSS/news.xml",
        "category": "Новости",
        "count": 2  # Сколько новостей брать
    },
    {
        "name": "Медуза",
        "url": "https://meduza.io/rss/all",
        "category": "Новости",
        "count": 2
    },
    {
        "name": "N+1",
        "url": "https://nplus1.ru/rss",
        "category": "Наука",
        "count": 2
    },
    {
        "name": "Habr",
        "url": "https://habr.com/ru/rss/best/daily/",
        "category": "Технологии",
        "count": 2
    },
    {
        "name": "3DNews",
        "url": "https://3dnews.ru/news/rss/",
        "category": "Технологии",
        "count": 2
    },
    {
        "name": "Афиша Daily",
        "url": "https://daily.afisha.ru/feed/",
        "category": "Культура",
        "count": 2
    },
    {
        "name": "Sports.ru",
        "url": "https://www.sports.ru/rss/main.xml",
        "category": "Спорт",
        "count": 2
    }
]


# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def clean_html(text: str) -> str:
    """
    Очищает текст от HTML-тегов и лишних пробелов.
    
    Args:
        text: Исходный текст с HTML
        
    Returns:
        Очищенный текст
    """
    if not text:
        return ""
    
    # Убираем HTML-теги
    clean = re.sub(r'<[^>]+>', '', text)
    
    # Декодируем HTML-сущности (&amp; → &, &quot; → " и т.д.)
    clean = unescape(clean)
    
    # Убираем лишние пробелы и переносы строк
    clean = re.sub(r'\s+', ' ', clean).strip()
    
    return clean


def truncate_text(text: str, max_length: int = 300) -> str:
    """
    Обрезает текст до указанной длины, не разрывая слова.
    
    Args:
        text: Исходный текст
        max_length: Максимальная длина
        
    Returns:
        Обрезанный текст с "..." в конце
    """
    if len(text) <= max_length:
        return text
    
    # Обрезаем и ищем последний пробел
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > 0:
        truncated = truncated[:last_space]
    
    return truncated + "..."


def parse_date(entry) -> Optional[datetime]:
    """
    Извлекает дату публикации из RSS-записи.
    
    Args:
        entry: Объект записи из feedparser
        
    Returns:
        datetime объект или None
    """
    # feedparser парсит дату в published_parsed или updated_parsed
    date_tuple = entry.get('published_parsed') or entry.get('updated_parsed')
    
    if date_tuple:
        try:
            return datetime(*date_tuple[:6])
        except Exception:
            pass
    
    return None


# ============================================
# ОСНОВНАЯ ФУНКЦИЯ ПАРСИНГА
# ============================================

def fetch_news_from_source(source: Dict) -> List[Dict]:
    """
    Загружает новости из одного RSS-источника.
    
    Args:
        source: Словарь с настройками источника
                {name, url, category, count}
    
    Returns:
        Список словарей с новостями
    """
    logger.info(f"📡 Загружаю: {source['name']} ({source['url']})")
    
    news_list = []
    
    try:
        # Парсим RSS-ленту
        feed = feedparser.parse(source['url'])
        
        # Проверяем на ошибки
        if feed.bozo and feed.bozo_exception:
            logger.warning(f"⚠️  Ошибка парсинга {source['name']}: {feed.bozo_exception}")
        
        # Берём нужное количество записей
        entries = feed.entries[:source['count']]
        
        for entry in entries:
            # Извлекаем данные
            title = clean_html(entry.get('title', 'Без заголовка'))
            
            # Описание может быть в разных полях
            description = (
                entry.get('summary') or 
                entry.get('description') or 
                entry.get('content', [{}])[0].get('value', '')
            )
            description = clean_html(description)
            description = truncate_text(description, 300)
            
            link = entry.get('link', '')
            pub_date = parse_date(entry)
            
            # Формируем объект новости
            news_item = {
                "title": title,
                "description": description,
                "link": link,
                "source": source['name'],
                "category": source['category'],
                "published": pub_date.isoformat() if pub_date else None,
                "published_formatted": pub_date.strftime("%d.%m.%Y %H:%M") if pub_date else "—"
            }
            
            news_list.append(news_item)
            logger.info(f"   ✓ {title[:50]}...")
        
        logger.info(f"✅ {source['name']}: загружено {len(news_list)} новостей")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Ошибка сети для {source['name']}: {e}")
    except Exception as e:
        logger.error(f"❌ Ошибка при парсинге {source['name']}: {e}")
    
    return news_list


def fetch_all_news() -> List[Dict]:
    """
    Загружает новости со всех источников.
    
    Returns:
        Список всех новостей, отсортированный по дате (свежие первые)
    """
    logger.info("=" * 50)
    logger.info("🚀 FlashCast RSS Parser — Запуск")
    logger.info("=" * 50)
    
    all_news = []
    
    for source in RSS_SOURCES:
        news = fetch_news_from_source(source)
        all_news.extend(news)
    
    # Сортируем по дате (свежие первые)
    all_news.sort(
        key=lambda x: x['published'] or '1970-01-01',
        reverse=True
    )
    
    logger.info("=" * 50)
    logger.info(f"📊 Итого загружено: {len(all_news)} новостей")
    logger.info("=" * 50)
    
    return all_news


# ============================================
# ГЕНЕРАЦИЯ ТЕКСТА ДЛЯ ПОДКАСТА
# ============================================

def generate_podcast_script(news_list: List[Dict]) -> str:
    """
    Генерирует текст для озвучки подкаста.
    
    Args:
        news_list: Список новостей
        
    Returns:
        Готовый текст для TTS
    """
    today = datetime.now().strftime("%d %B %Y")
    
    # Месяцы на русском
    months_ru = {
        'January': 'января', 'February': 'февраля', 'March': 'марта',
        'April': 'апреля', 'May': 'мая', 'June': 'июня',
        'July': 'июля', 'August': 'августа', 'September': 'сентября',
        'October': 'октября', 'November': 'ноября', 'December': 'декабря'
    }
    
    for eng, rus in months_ru.items():
        today = today.replace(eng, rus)
    
    # Вступление
    script = f"""Привет! Это FlashCast — твой ежедневный новостной подкаст.
Сегодня {today}. Вот главные новости дня.

"""
    
    # Группируем по категориям
    categories = {}
    for news in news_list:
        cat = news['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(news)
    
    # Генерируем текст по категориям
    for category, items in categories.items():
        script += f"\n{category}.\n\n"
        
        for item in items:
            script += f"{item['title']}.\n"
            if item['description']:
                script += f"{item['description']}\n"
            script += "\n"
    
    # Заключение
    script += """Это были главные новости на сегодня.
Спасибо, что слушаете FlashCast! До завтра!
"""
    
    return script


# ============================================
# СОХРАНЕНИЕ РЕЗУЛЬТАТОВ
# ============================================

def save_results(news_list: List[Dict], script: str):
    """
    Сохраняет результаты в файлы.
    
    Args:
        news_list: Список новостей (сохраняется в JSON)
        script: Текст подкаста (сохраняется в TXT)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d")
    
    # Сохраняем JSON с новостями
    json_filename = f"news_{timestamp}.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(news_list, f, ensure_ascii=False, indent=2)
    logger.info(f"💾 Сохранено: {json_filename}")
    
    # Сохраняем текст для озвучки
    txt_filename = f"podcast_script_{timestamp}.txt"
    with open(txt_filename, 'w', encoding='utf-8') as f:
        f.write(script)
    logger.info(f"💾 Сохранено: {txt_filename}")
    
    return json_filename, txt_filename


# ============================================
# ТОЧКА ВХОДА
# ============================================

if __name__ == "__main__":
    # 1. Собираем новости
    news = fetch_all_news()
    
    # 2. Генерируем текст подкаста
    script = generate_podcast_script(news)
    
    # 3. Выводим превью
    print("\n" + "=" * 50)
    print("📝 ПРЕВЬЮ ТЕКСТА ПОДКАСТА:")
    print("=" * 50)
    print(script[:1000] + "..." if len(script) > 1000 else script)
    
    # 4. Сохраняем результаты
    json_file, txt_file = save_results(news, script)
    
    print("\n" + "=" * 50)
    print("✅ ГОТОВО!")
    print(f"   Новости: {json_file}")
    print(f"   Скрипт:  {txt_file}")
    print("=" * 50)

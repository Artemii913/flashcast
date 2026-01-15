#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================
FlashCast — Main Pipeline (Главный скрипт)
============================================
Описание:
    Полный пайплайн генерации подкаста:
    1. Собирает новости с RSS
    2. Формирует текст подкаста
    3. Озвучивает через Edge TTS
    4. Обновляет данные для сайта

Использование:
    python main.py

Для GitHub Actions:
    python main.py --ci

============================================
"""

import asyncio
import json
import os
import sys
from datetime import datetime
import logging
import shutil

# Импортируем наши модули
from rss_parser import fetch_all_news, generate_podcast_script
from tts_generator import text_to_speech

# ============================================
# НАСТРОЙКА ЛОГИРОВАНИЯ
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('FlashCast-Main')


# ============================================
# КОНФИГУРАЦИЯ
# ============================================

# Папка для выходных файлов (будет на сайте)
OUTPUT_DIR = "../data"

# Голос для озвучки
VOICE = "dmitry"  # или "svetlana"


# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def ensure_output_dir():
    """Создаёт папку для выходных файлов, если её нет."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    logger.info(f"📁 Папка данных: {OUTPUT_DIR}")


def clean_old_files():
    """Удаляет старые файлы подкастов (старше 1 дня)."""
    logger.info("🧹 Очистка старых файлов...")
    
    today = datetime.now().strftime("%Y-%m-%d")
    
    if not os.path.exists(OUTPUT_DIR):
        return
    
    for filename in os.listdir(OUTPUT_DIR):
        # Пропускаем файлы без даты в имени
        if today not in filename and filename.endswith(('.mp3', '.json')):
            filepath = os.path.join(OUTPUT_DIR, filename)
            try:
                os.remove(filepath)
                logger.info(f"   🗑️  Удалён: {filename}")
            except Exception as e:
                logger.warning(f"   ⚠️  Не удалось удалить {filename}: {e}")


def save_podcast_metadata(news_list: list, audio_file: str):
    """
    Сохраняет метаданные подкаста для сайта.
    
    Args:
        news_list: Список новостей
        audio_file: Путь к MP3 файлу
    """
    today = datetime.now()
    
    # Формируем данные для сайта
    metadata = {
        "id": today.strftime("%Y%m%d"),
        "title": f"Новости за {today.strftime('%d.%m.%Y')}",
        "date": today.isoformat(),
        "date_formatted": today.strftime("%d %B %Y"),
        "audio_file": os.path.basename(audio_file),
        "news_count": len(news_list),
        "categories": list(set(n['category'] for n in news_list)),
        "sources": list(set(n['source'] for n in news_list)),
        "news": news_list,
        "generated_at": datetime.now().isoformat()
    }
    
    # Русские месяцы
    months_ru = {
        'January': 'января', 'February': 'февраля', 'March': 'марта',
        'April': 'апреля', 'May': 'мая', 'June': 'июня',
        'July': 'июля', 'August': 'августа', 'September': 'сентября',
        'October': 'октября', 'November': 'ноября', 'December': 'декабря'
    }
    for eng, rus in months_ru.items():
        metadata['date_formatted'] = metadata['date_formatted'].replace(eng, rus)
    
    # Сохраняем
    metadata_file = os.path.join(OUTPUT_DIR, "podcast.json")
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    logger.info(f"💾 Метаданные: {metadata_file}")
    
    return metadata


# ============================================
# ГЛАВНЫЙ ПАЙПЛАЙН
# ============================================

async def run_pipeline():
    """
    Запускает полный пайплайн генерации подкаста.
    
    Шаги:
    1. Создание/очистка папок
    2. Парсинг RSS
    3. Генерация текста
    4. Озвучка TTS
    5. Сохранение метаданных
    """
    
    print("=" * 60)
    print("🎙️  FlashCast — Генерация подкаста")
    print("=" * 60)
    
    start_time = datetime.now()
    
    # 1. Подготовка
    logger.info("📋 Шаг 1/5: Подготовка...")
    ensure_output_dir()
    clean_old_files()
    
    # 2. Парсинг новостей
    logger.info("📰 Шаг 2/5: Сбор новостей...")
    news_list = fetch_all_news()
    
    if not news_list:
        logger.error("❌ Не удалось загрузить новости!")
        return False
    
    logger.info(f"   ✓ Загружено {len(news_list)} новостей")
    
    # 3. Генерация текста
    logger.info("📝 Шаг 3/5: Генерация текста...")
    script = generate_podcast_script(news_list)
    
    # Сохраняем текст (для отладки)
    script_file = os.path.join(OUTPUT_DIR, "script.txt")
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script)
    logger.info(f"   ✓ Текст: {len(script)} символов")
    
    # 4. Озвучка
    logger.info("🔊 Шаг 4/5: Озвучка...")
    today = datetime.now().strftime("%Y-%m-%d")
    audio_file = os.path.join(OUTPUT_DIR, f"podcast_{today}.mp3")
    
    success = await text_to_speech(
        text=script,
        output_file=audio_file,
        voice=VOICE
    )
    
    if not success:
        logger.error("❌ Ошибка озвучки!")
        return False
    
    # 5. Сохранение метаданных
    logger.info("💾 Шаг 5/5: Сохранение метаданных...")
    metadata = save_podcast_metadata(news_list, audio_file)
    
    # Итоги
    elapsed = (datetime.now() - start_time).total_seconds()
    
    print("\n" + "=" * 60)
    print("✅ ПОДКАСТ ГОТОВ!")
    print("=" * 60)
    print(f"   📰 Новостей: {len(news_list)}")
    print(f"   📝 Текст: {len(script)} символов")
    print(f"   🎵 Аудио: {audio_file}")
    print(f"   ⏱️  Время: {elapsed:.1f} сек")
    print("=" * 60)
    
    return True


# ============================================
# ТОЧКА ВХОДА
# ============================================

def main():
    """Главная функция."""
    
    # Проверяем режим CI (GitHub Actions)
    is_ci = "--ci" in sys.argv
    
    if is_ci:
        logger.info("🤖 Режим CI/CD")
    
    # Запускаем пайплайн
    success = asyncio.run(run_pipeline())
    
    # Возвращаем код выхода
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

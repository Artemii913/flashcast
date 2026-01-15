#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================
FlashCast — TTS Generator (Озвучка)
============================================
Описание:
    Скрипт преобразует текст подкаста в аудио MP3
    используя Edge TTS (бесплатные голоса Microsoft).

Доступные русские голоса:
    - ru-RU-DmitryNeural (мужской) ← по умолчанию
    - ru-RU-SvetlanaNeural (женский)

Использование:
    python tts_generator.py podcast_script_2026-01-15.txt

Зависимости:
    pip install edge-tts

============================================
"""

import asyncio
import edge_tts
import sys
import os
from datetime import datetime
import logging

# ============================================
# НАСТРОЙКА ЛОГИРОВАНИЯ
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('FlashCast-TTS')


# ============================================
# КОНФИГУРАЦИЯ
# ============================================

# Доступные голоса
VOICES = {
    "dmitry": "ru-RU-DmitryNeural",    # Мужской голос
    "svetlana": "ru-RU-SvetlanaNeural"  # Женский голос
}

# Голос по умолчанию
DEFAULT_VOICE = "dmitry"

# Скорость речи (от -50% до +50%)
# Примеры: "-10%" — медленнее, "+20%" — быстрее
SPEECH_RATE = "+0%"

# Громкость (от -50% до +50%)
VOLUME = "+0%"


# ============================================
# ОСНОВНАЯ ФУНКЦИЯ ОЗВУЧКИ
# ============================================

async def text_to_speech(
    text: str,
    output_file: str,
    voice: str = DEFAULT_VOICE,
    rate: str = SPEECH_RATE,
    volume: str = VOLUME
) -> bool:
    """
    Преобразует текст в аудио MP3.
    
    Args:
        text: Текст для озвучки
        output_file: Путь к выходному MP3 файлу
        voice: Ключ голоса (dmitry/svetlana)
        rate: Скорость речи
        volume: Громкость
        
    Returns:
        True если успешно, False при ошибке
    """
    
    # Получаем полное имя голоса
    voice_name = VOICES.get(voice, VOICES[DEFAULT_VOICE])
    
    logger.info(f"🎙️  Голос: {voice_name}")
    logger.info(f"⚡ Скорость: {rate}")
    logger.info(f"🔊 Громкость: {volume}")
    logger.info(f"📝 Текст: {len(text)} символов")
    
    try:
        # Создаём объект для синтеза
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice_name,
            rate=rate,
            volume=volume
        )
        
        logger.info("⏳ Генерация аудио...")
        
        # Сохраняем в файл
        await communicate.save(output_file)
        
        # Проверяем размер файла
        file_size = os.path.getsize(output_file)
        file_size_mb = file_size / (1024 * 1024)
        
        logger.info(f"✅ Сохранено: {output_file}")
        logger.info(f"📦 Размер: {file_size_mb:.2f} MB")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка генерации: {e}")
        return False


async def list_voices():
    """
    Выводит список всех доступных голосов.
    """
    logger.info("📋 Загружаю список голосов...")
    
    voices = await edge_tts.list_voices()
    
    # Фильтруем русские голоса
    ru_voices = [v for v in voices if v['Locale'].startswith('ru-')]
    
    print("\n🇷🇺 Русские голоса:")
    print("-" * 50)
    for v in ru_voices:
        gender = "👨" if v['Gender'] == 'Male' else "👩"
        print(f"  {gender} {v['ShortName']}")
    print("-" * 50)
    
    return ru_voices


# ============================================
# ТОЧКА ВХОДА
# ============================================

def main():
    """
    Главная функция.
    
    Использование:
        python tts_generator.py <текстовый_файл>
        python tts_generator.py --list-voices
        python tts_generator.py <текст> --voice svetlana
    """
    
    print("=" * 50)
    print("🎙️  FlashCast TTS Generator")
    print("=" * 50)
    
    # Проверяем аргументы командной строки
    if len(sys.argv) < 2:
        print("""
Использование:
    python tts_generator.py <текстовый_файл.txt>
    python tts_generator.py --list-voices
    python tts_generator.py <файл.txt> --voice svetlana
    
Примеры:
    python tts_generator.py podcast_script_2026-01-15.txt
    python tts_generator.py script.txt --voice dmitry
        """)
        return
    
    # Список голосов
    if sys.argv[1] == "--list-voices":
        asyncio.run(list_voices())
        return
    
    # Путь к текстовому файлу
    input_file = sys.argv[1]
    
    # Проверяем существование файла
    if not os.path.exists(input_file):
        logger.error(f"❌ Файл не найден: {input_file}")
        return
    
    # Определяем голос
    voice = DEFAULT_VOICE
    if "--voice" in sys.argv:
        voice_index = sys.argv.index("--voice") + 1
        if voice_index < len(sys.argv):
            voice = sys.argv[voice_index]
    
    # Читаем текст
    logger.info(f"📖 Читаю файл: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Формируем имя выходного файла
    timestamp = datetime.now().strftime("%Y-%m-%d")
    output_file = f"podcast_{timestamp}.mp3"
    
    # Запускаем озвучку
    success = asyncio.run(text_to_speech(
        text=text,
        output_file=output_file,
        voice=voice
    ))
    
    if success:
        print("\n" + "=" * 50)
        print("✅ ГОТОВО!")
        print(f"   Аудио: {output_file}")
        print("=" * 50)
    else:
        print("\n❌ Ошибка генерации аудио")


if __name__ == "__main__":
    main()

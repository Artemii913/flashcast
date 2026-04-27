# FlashCast — Проверенные RSS-источники

Дата проверки: **2026-04-28**  
Метод: `feedparser.parse(url)` — засчитывается только если вернул ≥ 1 запись.

---

## Финальный итог

| Категория | Источники | Кол-во |
|---|---|---|
| Новости | Коммерсантъ, Медуза, Интерфакс, ТАСС | 4 |
| Технологии | Habr, 3DNews, iXBT, VC.ru | 4 |
| Экономика | РБК, Ведомости, Forbes Russia, The Bell | 4 |
| Политика | Коммерсантъ Политика, Интерфакс, ТАСС | 3 |
| Наука | N+1, Naked Science, Postnauka | 3 |
| Культура | Lenta Культура, The Art Newspaper Russia, Афиша Daily, Colta.ru, Газета.ру Культура | 5 |
| Спорт | Sports.ru, Lenta Спорт, Soccer.ru | 3 |

---

## Полная проверка (все кандидаты)

### Новости

| Источник | URL | Статус | Записей | Итог |
|---|---|---|---|---|
| Коммерсантъ | https://www.kommersant.ru/RSS/news.xml | 301→OK | 267 | ✅ |
| Медуза | https://meduza.io/rss/all | 200 | 30 | ✅ |
| Интерфакс | https://www.interfax.ru/rss.asp | 301→OK | 25 | ✅ |
| ТАСС | https://tass.ru/rss/v2.xml | 200 | 100 | ✅ |

### Технологии

| Источник | URL | Статус | Записей | Итог |
|---|---|---|---|---|
| Habr | https://habr.com/ru/rss/best/daily/ | 301→OK | 40 | ✅ |
| 3DNews | https://3dnews.ru/news/rss/ | 200 | 63 | ✅ |
| iXBT | https://www.ixbt.com/export/news.rss | 200 | 50 | ✅ |
| VC.ru | https://vc.ru/rss | 200 | 12 | ✅ |

### Экономика

| Источник | URL | Статус | Записей | Итог |
|---|---|---|---|---|
| РБК | https://rssexport.rbc.ru/rbcnews/news/30/full.rss | 200 | 30 | ✅ |
| Ведомости | https://www.vedomosti.ru/rss/rubric/economics | 200 | 200 | ✅ |
| Forbes Russia | https://www.forbes.ru/newrss.xml | 200 | 19 | ✅ |
| The Bell | https://thebell.io/feed/ | 200 | 20 | ✅ |

### Политика

| Источник | URL | Статус | Записей | Итог |
|---|---|---|---|---|
| Коммерсантъ Политика | https://www.kommersant.ru/RSS/section-politics.xml | 301→OK | 32 | ✅ |
| Интерфакс | https://www.interfax.ru/rss.asp | 301→OK | 25 | ✅ |
| ТАСС | https://tass.ru/rss/v2.xml | 200 | 100 | ✅ |
| РИА Новости (старый) | https://ria.ru/export/rss2/politics/index.xml | — | 0 | ❌ сломан |
| Lenta Политика (старый) | https://lenta.ru/rss/news/russia/politics | — | 0 | ❌ сломан |

### Наука

| Источник | URL | Статус | Записей | Итог |
|---|---|---|---|---|
| N+1 | https://nplus1.ru/rss | 200 | 10 | ✅ |
| Naked Science | https://naked-science.ru/feed | 200 | 20 | ✅ |
| Postnauka | https://postnauka.org/feed | 200 | 15 | ✅ |
| Indicator.ru | https://indicator.ru/feed/ | 301→пустой | 0 | ❌ |

### Культура

| Источник | URL | Статус | Записей | Итог |
|---|---|---|---|---|
| Lenta Культура | https://lenta.ru/rss/news/culture/ | 200 | 195 | ✅ |
| The Art Newspaper Russia | https://www.theartnewspaper.ru/rss/ | 200 | 42 | ✅ |
| Афиша Daily | https://daily.afisha.ru/rss/ | 200 | 5 | ✅ |
| Colta.ru | https://www.colta.ru/rss | 200 | 50 | ✅ |
| Газета.ру Культура | https://www.gazeta.ru/export/rss/culture.xml | 200 | 15 | ✅ |
| Сноб | https://snob.ru/rss/ | 200 | 50 | ⏸ резерв |
| РИА Культура (старый) | https://ria.ru/export/rss2/culture/index.xml | 404 | 0 | ❌ |
| Афиша (главная) | https://www.afisha.ru/rss/ | 404 | 0 | ❌ |
| Кинопоиск | https://www.kinopoisk.ru/news/rss/ | 403 | 0 | ❌ |
| Коммерсантъ Стиль | https://www.kommersant.ru/RSS/section-lifestyle.xml | 301→пустой | 0 | ❌ |
| Коммерсантъ Weekend | https://www.kommersant.ru/RSS/section-weekend.xml | 301→пустой | 0 | ❌ |
| Кино-Театр.ру | https://www.kino-teatr.ru/rss/news.rss | 302→пустой | 0 | ❌ |
| РГ Культура | https://rg.ru/tema/kultura.atom | 401 | 0 | ❌ |

### Спорт

| Источник | URL | Статус | Записей | Итог |
|---|---|---|---|---|
| Sports.ru | https://www.sports.ru/rss/main.xml | 200 | 20 | ✅ |
| Lenta Спорт | https://lenta.ru/rss/news/sport/ | 200 | 200 | ✅ |
| Soccer.ru | https://www.soccer.ru/rss/ | 301→OK | 41 | ✅ |
| Championat.com (все варианты) | /rss/, /rss/news.xml, /rss/all_news.xml, /football/rss.xml | 404 | 0 | ❌ |
| Совспорт | https://www.sovsport.ru/rss/all.xml | 404 | 0 | ❌ |
| Match TV | https://www.matchtv.ru/feeds/rss | 301→пустой | 0 | ❌ |
| Eurosport.ru | https://www.eurosport.ru/rss.xml | нет ответа | 0 | ❌ |
| Газета.ру Спорт | https://www.gazeta.ru/export/sport.xml | 404 | 0 | ❌ |
| Sport24.ru | https://sport24.ru/rss/index.xml | 404 | 0 | ❌ |
| РГ Спорт | https://rg.ru/tema/sport.atom | 401 | 0 | ❌ |

---

## Источники в резерве

| Источник | URL | Записей | Причина отложить |
|---|---|---|---|
| Сноб | https://snob.ru/rss/ | 50 | Культура уже набрала 5 источников — достаточно. Подключить если кто-то из текущих отвалится. |

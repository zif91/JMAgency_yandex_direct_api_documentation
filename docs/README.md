# Документация Yandex Direct API v5

Полное руководство для разработчиков по работе с API Яндекс Директа версии 5.

## Содержание

### Начало работы
- [Обзор API](./getting-started/overview.md) — Введение в API Яндекс Директа
- [Регистрация приложения](./getting-started/registration.md) — Как зарегистрировать приложение
- [Аутентификация](./getting-started/authentication.md) — OAuth 2.0 и получение токена
- [Песочница](./getting-started/sandbox.md) — Тестовая среда для разработки

### Основные концепции
- [Формат запросов](./concepts/request-format.md) — Структура HTTP-запросов к API
- [Формат ответов](./concepts/response-format.md) — Структура ответов API
- [Система баллов (Units)](./concepts/units.md) — Лимиты и ограничения API
- [Обработка ошибок](./concepts/errors.md) — Коды ошибок и их обработка

### Справочник сервисов API
- [Campaigns](./services/campaigns.md) — Управление кампаниями
- [AdGroups](./services/adgroups.md) — Управление группами объявлений
- [Ads](./services/ads.md) — Управление объявлениями
- [Keywords](./services/keywords.md) — Управление ключевыми фразами
- [Bids](./services/bids.md) — Управление ставками
- [BidModifiers](./services/bidmodifiers.md) — Корректировки ставок
- [Reports](./services/reports.md) — Формирование отчетов
- [Clients](./services/clients.md) — Управление клиентами
- [AgencyClients](./services/agencyclients.md) — Клиенты агентства
- [Dictionaries](./services/dictionaries.md) — Справочники
- [RetargetingLists](./services/retargetinglists.md) — Списки ретаргетинга
- [Sitelinks](./services/sitelinks.md) — Быстрые ссылки
- [VCards](./services/vcards.md) — Виртуальные визитки
- [AdImages](./services/adimages.md) — Изображения
- [AdExtensions](./services/adextensions.md) — Расширения объявлений

### Примеры кода
- [Python примеры](./examples/python.md) — Примеры использования на Python

### Инструменты
- [Multi-Account Panel](../panel/README.md) — Панель управления с мульти-аккаунтами и AI-аудитом

---

## Быстрый старт

### Базовые URL

| Окружение | URL |
|-----------|-----|
| **Production** | `https://api.direct.yandex.com/json/v5/{service}` |
| **Sandbox** | `https://api-sandbox.direct.yandex.com/json/v5/{service}` |
| **Production v501** | `https://api.direct.yandex.com/json/v501/{service}` |

### Пример запроса

```bash
curl -X POST "https://api.direct.yandex.com/json/v5/campaigns" \
  -H "Authorization: Bearer YOUR_OAUTH_TOKEN" \
  -H "Client-Login: your-login" \
  -H "Accept-Language: ru" \
  -H "Content-Type: application/json" \
  -d '{
    "method": "get",
    "params": {
      "SelectionCriteria": {},
      "FieldNames": ["Id", "Name", "Status", "State"]
    }
  }'
```

### Иерархия объектов

```
Campaign (Кампания)
└── AdGroup (Группа объявлений)
    ├── Ad (Объявление)
    └── Keyword (Ключевая фраза)
```

---

## Полезные ссылки

- [Официальная документация Yandex Direct API](https://yandex.ru/dev/direct/doc/ru/)
- [Yandex OAuth](https://oauth.yandex.ru/)
- [Интерфейс Яндекс Директа](https://direct.yandex.ru/)

---

*Документация актуальна для API версии 5*

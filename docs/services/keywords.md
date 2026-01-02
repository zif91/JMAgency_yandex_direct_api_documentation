# Сервис Keywords

[← Назад к оглавлению](../README.md)

## Обзор

Сервис **Keywords** предназначен для управления ключевыми фразами и автотаргетингами в группах объявлений.

## Endpoints

| Формат | URL |
|--------|-----|
| JSON | `https://api.direct.yandex.com/json/v5/keywords` |
| JSON (v501) | `https://api.direct.yandex.com/json/v501/keywords` |
| SOAP | `https://api.direct.yandex.com/v5/keywords` |
| WSDL | `https://api.direct.yandex.com/v5/keywords?wsdl` |

## Методы

| Метод | Описание |
|-------|----------|
| [add](#add) | Создание ключевых фраз |
| [get](#get) | Получение данных о фразах |
| [update](#update) | Изменение фраз |
| [delete](#delete) | Удаление фраз |
| [suspend](#suspend) | Приостановка показов |
| [resume](#resume) | Возобновление показов |

---

## Статусы ключевой фразы

### State (состояние показов)

| Значение | Описание |
|----------|----------|
| `ON` | Показы включены |
| `OFF` | Показы выключены |
| `SUSPENDED` | Приостановлено пользователем |

### Status (статус модерации)

| Значение | Описание |
|----------|----------|
| `DRAFT` | Черновик |
| `ACCEPTED` | Принята |
| `REJECTED` | Отклонена |

### ServingStatus (статус показов)

| Значение | Описание |
|----------|----------|
| `ELIGIBLE` | Показы возможны |
| `RARELY_SERVED` | Показы редки |

---

## add

Создание новых ключевых фраз. Максимум **10 000 фраз** за запрос.

### Запрос

```json
{
  "method": "add",
  "params": {
    "Keywords": [
      {
        "Keyword": "купить телефон",
        "AdGroupId": 789012,
        "Bid": 1500000,
        "ContextBid": 500000,
        "StrategyPriority": "NORMAL",
        "UserParam1": "param1",
        "UserParam2": "param2"
      }
    ]
  }
}
```

### Параметры ключевой фразы

| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `Keyword` | string | Да | Текст фразы (макс. 4096 символов) |
| `AdGroupId` | long | Да | ID группы объявлений |
| `Bid` | long | Нет | Ставка на поиске (микроединицы) |
| `ContextBid` | long | Нет | Ставка в сетях (микроединицы) |
| `StrategyPriority` | enum | Нет | Приоритет: `LOW`, `NORMAL`, `HIGH` |
| `UserParam1` | string | Нет | Пользовательский параметр 1 |
| `UserParam2` | string | Нет | Пользовательский параметр 2 |

### Автотаргетинг

```json
{
  "method": "add",
  "params": {
    "Keywords": [
      {
        "Keyword": "---autotargeting",
        "AdGroupId": 789012,
        "Bid": 2000000
      }
    ]
  }
}
```

> **Важно:** Для создания автотаргетинга используйте специальное значение `---autotargeting` в поле `Keyword`.

### Ответ

```json
{
  "result": {
    "AddResults": [
      {
        "Id": 444555666
      }
    ]
  }
}
```

---

## get

Получение информации о ключевых фразах.

### Запрос

```json
{
  "method": "get",
  "params": {
    "SelectionCriteria": {
      "Ids": [444555666],
      "AdGroupIds": [789012],
      "CampaignIds": [123456],
      "States": ["ON"],
      "Statuses": ["ACCEPTED"],
      "ServingStatuses": ["ELIGIBLE"]
    },
    "FieldNames": [
      "Id",
      "Keyword",
      "AdGroupId",
      "CampaignId",
      "State",
      "Status",
      "ServingStatus",
      "Bid",
      "ContextBid",
      "StrategyPriority",
      "StatisticsSearch",
      "StatisticsNetwork"
    ],
    "Page": {
      "Limit": 10000,
      "Offset": 0
    }
  }
}
```

### SelectionCriteria

| Параметр | Тип | Описание |
|----------|-----|----------|
| `Ids` | array[long] | ID фраз (макс. 10000) |
| `AdGroupIds` | array[long] | ID групп (макс. 1000) |
| `CampaignIds` | array[long] | ID кампаний (макс. 10) |
| `States` | array[enum] | Состояния показов |
| `Statuses` | array[enum] | Статусы модерации |
| `ServingStatuses` | array[enum] | Статусы показов |
| `ModifiedSince` | string | Изменённые после даты |

### FieldNames

| Поле | Описание |
|------|----------|
| `Id` | Идентификатор |
| `Keyword` | Текст фразы |
| `AdGroupId` | ID группы |
| `CampaignId` | ID кампании |
| `State` | Состояние показов |
| `Status` | Статус модерации |
| `ServingStatus` | Статус показов |
| `Bid` | Ставка на поиске |
| `ContextBid` | Ставка в сетях |
| `StrategyPriority` | Приоритет стратегии |
| `UserParam1` | Пользовательский параметр 1 |
| `UserParam2` | Пользовательский параметр 2 |
| `StatisticsSearch` | Статистика на поиске |
| `StatisticsNetwork` | Статистика в сетях |
| `ProductivityL` | Продуктивность (нижняя граница) |
| `ProductivityU` | Продуктивность (верхняя граница) |

### Ответ

```json
{
  "result": {
    "Keywords": [
      {
        "Id": 444555666,
        "Keyword": "купить телефон",
        "AdGroupId": 789012,
        "CampaignId": 123456,
        "State": "ON",
        "Status": "ACCEPTED",
        "ServingStatus": "ELIGIBLE",
        "Bid": 1500000,
        "ContextBid": 500000,
        "StrategyPriority": "NORMAL",
        "StatisticsSearch": {
          "Impressions": 1500,
          "Clicks": 45
        }
      }
    ]
  }
}
```

---

## update

Изменение параметров ключевых фраз.

### Запрос

```json
{
  "method": "update",
  "params": {
    "Keywords": [
      {
        "Id": 444555666,
        "Keyword": "купить телефон недорого",
        "Bid": 2000000,
        "StrategyPriority": "HIGH"
      }
    ]
  }
}
```

### Ответ

```json
{
  "result": {
    "UpdateResults": [
      {
        "Id": 444555666
      }
    ]
  }
}
```

---

## delete

Удаление ключевых фраз.

```json
{
  "method": "delete",
  "params": {
    "SelectionCriteria": {
      "Ids": [444555666, 444555667]
    }
  }
}
```

---

## suspend

Приостановка показов по ключевым фразам.

```json
{
  "method": "suspend",
  "params": {
    "SelectionCriteria": {
      "Ids": [444555666]
    }
  }
}
```

---

## resume

Возобновление показов по ключевым фразам.

```json
{
  "method": "resume",
  "params": {
    "SelectionCriteria": {
      "Ids": [444555666]
    }
  }
}
```

---

## Синтаксис ключевых фраз

### Операторы

| Оператор | Описание | Пример |
|----------|----------|--------|
| `""` | Точное соответствие | `"купить телефон"` |
| `!` | Фиксация словоформы | `!купить !телефон` |
| `+` | Обязательное слово | `+как купить телефон` |
| `[]` | Фиксация порядка слов | `[купить телефон]` |
| `-` | Минус-слова | `купить телефон -бесплатно` |

### Примеры

```
купить телефон                    # Широкое соответствие
"купить телефон"                  # Точная фраза
!купить !телефон                  # Точные словоформы
купить телефон -бесплатно -б/у    # С минус-словами
[купить телефон]                  # Фиксированный порядок
```

---

## Примеры использования

### Python: Добавление ключевых фраз

```python
def add_keywords(client, adgroup_id: int, keywords: list, default_bid: float = 30.0):
    """
    Добавление ключевых фраз в группу.

    Args:
        client: API клиент
        adgroup_id: ID группы объявлений
        keywords: Список ключевых фраз
        default_bid: Ставка по умолчанию (рубли)
    """
    bid_micros = int(default_bid * 1_000_000)

    keywords_data = [
        {
            "Keyword": kw,
            "AdGroupId": adgroup_id,
            "Bid": bid_micros,
            "StrategyPriority": "NORMAL"
        }
        for kw in keywords
    ]

    response = client.request("keywords", {
        "method": "add",
        "params": {
            "Keywords": keywords_data
        }
    })

    results = response.get("AddResults", [])
    successful = [r["Id"] for r in results if "Errors" not in r]
    failed = [
        {"keyword": keywords[i], "errors": r["Errors"]}
        for i, r in enumerate(results)
        if "Errors" in r
    ]

    return successful, failed


# Использование
keywords = [
    "купить телефон",
    "телефон цена",
    "смартфон купить"
]

added, failed = add_keywords(client, 789012, keywords, default_bid=50.0)
print(f"Добавлено: {len(added)}, ошибок: {len(failed)}")
```

### Python: Получение фраз группы со статистикой

```python
def get_keywords_with_stats(client, adgroup_id: int):
    response = client.request("keywords", {
        "method": "get",
        "params": {
            "SelectionCriteria": {
                "AdGroupIds": [adgroup_id],
                "States": ["ON"]
            },
            "FieldNames": [
                "Id", "Keyword", "State", "Bid",
                "StatisticsSearch", "StatisticsNetwork"
            ]
        }
    })

    keywords = response.get("Keywords", [])

    for kw in keywords:
        search_stats = kw.get("StatisticsSearch", {})
        impressions = search_stats.get("Impressions", 0)
        clicks = search_stats.get("Clicks", 0)
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        bid = kw.get("Bid", 0) / 1_000_000

        print(f"{kw['Keyword']}: {clicks} кликов, CTR={ctr:.2f}%, ставка={bid}₽")

    return keywords
```

### Python: Массовое обновление ставок

```python
def update_keyword_bids(client, keyword_bids: dict):
    """
    Массовое обновление ставок.

    Args:
        keyword_bids: {keyword_id: new_bid_in_rubles}
    """
    keywords_data = [
        {
            "Id": kw_id,
            "Bid": int(bid * 1_000_000)
        }
        for kw_id, bid in keyword_bids.items()
    ]

    response = client.request("keywords", {
        "method": "update",
        "params": {
            "Keywords": keywords_data
        }
    })

    results = response.get("UpdateResults", [])
    successful = [r["Id"] for r in results if "Errors" not in r]

    return successful


# Использование
new_bids = {
    444555666: 45.0,  # 45 рублей
    444555667: 30.0,  # 30 рублей
    444555668: 55.0   # 55 рублей
}

updated = update_keyword_bids(client, new_bids)
print(f"Обновлено ставок: {len(updated)}")
```

---

[← Ads](./ads.md) | [Bids →](./bids.md)

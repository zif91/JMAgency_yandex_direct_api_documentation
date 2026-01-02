# Формат запросов

[← Назад к оглавлению](../README.md)

## Обзор

Все запросы к API Яндекс Директа выполняются методом **POST** по протоколу **HTTPS**. API поддерживает два формата данных: JSON (рекомендуемый) и SOAP/XML.

## Структура URL

```
https://api.direct.yandex.com/json/v5/{service}
```

Где `{service}` — название сервиса API (campaigns, adgroups, ads и т.д.).

### Примеры URL

| Сервис | URL |
|--------|-----|
| Campaigns | `https://api.direct.yandex.com/json/v5/campaigns` |
| AdGroups | `https://api.direct.yandex.com/json/v5/adgroups` |
| Ads | `https://api.direct.yandex.com/json/v5/ads` |
| Keywords | `https://api.direct.yandex.com/json/v5/keywords` |
| Reports | `https://api.direct.yandex.com/json/v5/reports` |

## HTTP-заголовки

### Обязательные заголовки

```http
Authorization: Bearer {oauth_token}
Content-Type: application/json; charset=utf-8
```

### Рекомендуемые заголовки

```http
Accept-Language: ru
Accept-Encoding: gzip
```

### Заголовки для агентств

```http
Client-Login: {client_login}
Use-Operator-Units: true
```

### Полный список заголовков

| Заголовок | Обязательный | Описание |
|-----------|--------------|----------|
| `Authorization` | Да | OAuth-токен в формате `Bearer {token}` |
| `Content-Type` | Да | `application/json; charset=utf-8` |
| `Accept-Language` | Нет | Язык сообщений: `ru`, `en`, `tr` |
| `Client-Login` | Для агентств | Логин клиента агентства |
| `Use-Operator-Units` | Нет | `true` — использовать баллы агентства |
| `Accept-Encoding` | Нет | `gzip` — сжатие ответа |
| `Payment-Token` | Для финансов | Токен для финансовых операций |

## Структура тела запроса

### Базовая структура

```json
{
  "method": "название_метода",
  "params": {
    // параметры метода
  }
}
```

### Пример запроса get

```json
{
  "method": "get",
  "params": {
    "SelectionCriteria": {
      "Ids": [123456, 789012]
    },
    "FieldNames": ["Id", "Name", "Status", "State"],
    "Page": {
      "Limit": 100,
      "Offset": 0
    }
  }
}
```

### Пример запроса add

```json
{
  "method": "add",
  "params": {
    "Campaigns": [
      {
        "Name": "Моя кампания",
        "StartDate": "2024-01-15",
        "DailyBudget": {
          "Amount": 3000000000,
          "Mode": "STANDARD"
        },
        "TextCampaign": {
          "BiddingStrategy": {
            "Search": {
              "BiddingStrategyType": "HIGHEST_POSITION"
            },
            "Network": {
              "BiddingStrategyType": "SERVING_OFF"
            }
          }
        }
      }
    ]
  }
}
```

### Пример запроса update

```json
{
  "method": "update",
  "params": {
    "Campaigns": [
      {
        "Id": 123456,
        "Name": "Новое название кампании"
      }
    ]
  }
}
```

### Пример запроса delete

```json
{
  "method": "delete",
  "params": {
    "SelectionCriteria": {
      "Ids": [123456, 789012]
    }
  }
}
```

## Параметры отбора (SelectionCriteria)

Большинство методов используют объект `SelectionCriteria` для фильтрации данных:

```json
{
  "SelectionCriteria": {
    "Ids": [123, 456],
    "Types": ["TEXT_CAMPAIGN", "SMART_CAMPAIGN"],
    "States": ["ON", "SUSPENDED"],
    "Statuses": ["ACCEPTED", "MODERATION"]
  }
}
```

### Типовые параметры отбора

| Параметр | Тип | Описание |
|----------|-----|----------|
| `Ids` | array[long] | Идентификаторы объектов (макс. 1000-10000) |
| `Types` | array[enum] | Типы объектов |
| `States` | array[enum] | Состояния объектов |
| `Statuses` | array[enum] | Статусы модерации |
| `CampaignIds` | array[long] | Фильтр по кампаниям |
| `AdGroupIds` | array[long] | Фильтр по группам объявлений |

## Пагинация

Для получения больших объёмов данных используйте параметры пагинации:

```json
{
  "method": "get",
  "params": {
    "SelectionCriteria": {},
    "FieldNames": ["Id", "Name"],
    "Page": {
      "Limit": 1000,
      "Offset": 0
    }
  }
}
```

### Параметры пагинации

| Параметр | Тип | По умолчанию | Максимум |
|----------|-----|--------------|----------|
| `Limit` | int | 10000 | Зависит от сервиса |
| `Offset` | int | 0 | — |

### Пример итерации по страницам (Python)

```python
def get_all_campaigns(client):
    all_campaigns = []
    offset = 0
    limit = 1000

    while True:
        response = client.request("campaigns", {
            "method": "get",
            "params": {
                "SelectionCriteria": {},
                "FieldNames": ["Id", "Name"],
                "Page": {"Limit": limit, "Offset": offset}
            }
        })

        campaigns = response.get("result", {}).get("Campaigns", [])
        all_campaigns.extend(campaigns)

        if len(campaigns) < limit:
            break

        offset += limit

    return all_campaigns
```

## Денежные значения

Все денежные параметры передаются в **микроединицах** — сумма в валюте рекламодателя, умноженная на 1 000 000.

### Примеры

| Реальная сумма | Значение в API |
|----------------|----------------|
| 1 000 ₽ | 1 000 000 000 |
| 500 ₽ | 500 000 000 |
| 0.50 ₽ | 500 000 |

### Формула конвертации

```python
# Из рублей в микроединицы
api_value = real_value * 1_000_000

# Из микроединиц в рубли
real_value = api_value / 1_000_000
```

## Полный пример запроса

### cURL

```bash
curl -X POST "https://api.direct.yandex.com/json/v5/campaigns" \
  -H "Authorization: Bearer AgAAAAA...YOUR_TOKEN" \
  -H "Accept-Language: ru" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "method": "get",
    "params": {
      "SelectionCriteria": {
        "States": ["ON", "SUSPENDED"]
      },
      "FieldNames": ["Id", "Name", "Status", "State", "DailyBudget"],
      "TextCampaignFieldNames": ["BiddingStrategy"],
      "Page": {
        "Limit": 100,
        "Offset": 0
      }
    }
  }'
```

### Python (requests)

```python
import requests

url = "https://api.direct.yandex.com/json/v5/campaigns"
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Accept-Language": "ru",
    "Content-Type": "application/json; charset=utf-8"
}
body = {
    "method": "get",
    "params": {
        "SelectionCriteria": {"States": ["ON", "SUSPENDED"]},
        "FieldNames": ["Id", "Name", "Status", "State"],
        "Page": {"Limit": 100}
    }
}

response = requests.post(url, json=body, headers=headers)
data = response.json()
print(data)
```

---

[← Песочница](../getting-started/sandbox.md) | [Формат ответов →](./response-format.md)

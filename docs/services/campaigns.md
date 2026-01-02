# Сервис Campaigns

[← Назад к оглавлению](../README.md)

## Обзор

Сервис **Campaigns** предназначен для управления рекламными кампаниями в Яндекс Директе.

## Endpoints

| Формат | URL |
|--------|-----|
| JSON | `https://api.direct.yandex.com/json/v5/campaigns` |
| JSON (v501) | `https://api.direct.yandex.com/json/v501/campaigns` |
| SOAP | `https://api.direct.yandex.com/v5/campaigns` |
| WSDL | `https://api.direct.yandex.com/v5/campaigns?wsdl` |

## Методы

| Метод | Описание |
|-------|----------|
| [add](#add) | Создание кампаний |
| [get](#get) | Получение данных о кампаниях |
| [update](#update) | Изменение кампаний |
| [delete](#delete) | Удаление кампаний |
| [suspend](#suspend) | Приостановка показов |
| [resume](#resume) | Возобновление показов |
| [archive](#archive) | Архивирование кампаний |
| [unarchive](#unarchive) | Разархивирование кампаний |

---

## Типы кампаний

| Тип | Описание | Только чтение |
|-----|----------|---------------|
| `TEXT_CAMPAIGN` | Текстово-графические объявления | Нет |
| `UNIFIED_CAMPAIGN` | Унифицированные перформанс-кампании | Нет |
| `SMART_CAMPAIGN` | Смарт-баннеры | Нет |
| `DYNAMIC_TEXT_CAMPAIGN` | Динамические объявления | Нет |
| `MOBILE_APP_CAMPAIGN` | Реклама мобильных приложений | Нет |
| `CPM_BANNER_CAMPAIGN` | Медийные кампании | Нет |
| `MCBANNER_CAMPAIGN` | Баннер на поиске | Да |
| `CPM_DEALS_CAMPAIGN` | Медийная с deals | Да |
| `CPM_FRONTPAGE_CAMPAIGN` | Главная страница Яндекса | Да |
| `CPM_PRICE` | Фиксированный CPM | Да |

## Статусы и состояния

### State (состояние показов)

| Значение | Описание |
|----------|----------|
| `CONVERTED` | Преобразована |
| `ARCHIVED` | Заархивирована |
| `SUSPENDED` | Показы приостановлены |
| `ENDED` | Показы завершены |
| `ON` | Показы идут |
| `OFF` | Показы остановлены |

### Status (статус модерации)

| Значение | Описание |
|----------|----------|
| `DRAFT` | Черновик |
| `MODERATION` | На модерации |
| `ACCEPTED` | Принята |
| `REJECTED` | Отклонена |

### StatusPayment (готовность к оплате)

| Значение | Описание |
|----------|----------|
| `DISALLOWED` | Не готова к оплате |
| `ALLOWED` | Готова к оплате |

---

## add

Создание новых кампаний. Максимум **10 кампаний** за один запрос.

### Запрос

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

### Параметры кампании

| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `Name` | string | Да | Название (макс. 255 символов) |
| `StartDate` | string | Да | Дата начала (YYYY-MM-DD) |
| `DailyBudget` | object | Да | Дневной бюджет |
| `ClientInfo` | string | Нет | Информация о клиенте |
| `TimeZone` | string | Нет | Часовой пояс (по умолчанию Europe/Moscow) |
| `EndDate` | string | Нет | Дата окончания |
| `NegativeKeywords` | array | Нет | Минус-фразы |
| `BlockedIps` | array | Нет | Заблокированные IP (макс. 25) |
| `ExcludedSites` | array | Нет | Исключённые площадки (макс. 1000) |
| `TimeTargeting` | object | Нет | Временной таргетинг |
| `Notification` | object | Нет | Настройки уведомлений |

### DailyBudget

```json
{
  "Amount": 3000000000,
  "Mode": "STANDARD"
}
```

| Параметр | Описание |
|----------|----------|
| `Amount` | Бюджет в микроединицах (3000000000 = 3000 ₽) |
| `Mode` | `STANDARD` — стандартный, `DISTRIBUTED` — распределённый |

### Ответ

```json
{
  "result": {
    "AddResults": [
      {
        "Id": 123456
      }
    ]
  }
}
```

---

## get

Получение информации о кампаниях.

### Запрос

```json
{
  "method": "get",
  "params": {
    "SelectionCriteria": {
      "Ids": [123456, 789012],
      "Types": ["TEXT_CAMPAIGN"],
      "States": ["ON", "SUSPENDED"],
      "Statuses": ["ACCEPTED"]
    },
    "FieldNames": [
      "Id",
      "Name",
      "Status",
      "State",
      "DailyBudget",
      "Statistics"
    ],
    "TextCampaignFieldNames": [
      "BiddingStrategy",
      "Settings"
    ],
    "Page": {
      "Limit": 100,
      "Offset": 0
    }
  }
}
```

### SelectionCriteria

| Параметр | Тип | Описание |
|----------|-----|----------|
| `Ids` | array[long] | ID кампаний (макс. 1000) |
| `Types` | array[enum] | Типы кампаний |
| `States` | array[enum] | Состояния |
| `Statuses` | array[enum] | Статусы модерации |
| `StatusesPayment` | array[enum] | Статусы оплаты |

### FieldNames (общие поля)

| Поле | Описание |
|------|----------|
| `Id` | Идентификатор |
| `Name` | Название |
| `ClientInfo` | Информация о клиенте |
| `StartDate` | Дата начала |
| `EndDate` | Дата окончания |
| `TimeTargeting` | Временной таргетинг |
| `TimeZone` | Часовой пояс |
| `NegativeKeywords` | Минус-фразы |
| `BlockedIps` | Заблокированные IP |
| `ExcludedSites` | Исключённые площадки |
| `DailyBudget` | Дневной бюджет |
| `Notification` | Настройки уведомлений |
| `Type` | Тип кампании |
| `Status` | Статус модерации |
| `State` | Состояние показов |
| `StatusPayment` | Статус оплаты |
| `StatusClarification` | Пояснение к статусу |
| `SourceId` | ID исходной кампании |
| `Statistics` | Статистика |
| `Currency` | Валюта |
| `Funds` | Информация о бюджете |
| `RepresentedBy` | Представитель |

### Ответ

```json
{
  "result": {
    "Campaigns": [
      {
        "Id": 123456,
        "Name": "Моя кампания",
        "Status": "ACCEPTED",
        "State": "ON",
        "Type": "TEXT_CAMPAIGN",
        "DailyBudget": {
          "Amount": 3000000000,
          "Mode": "STANDARD"
        },
        "Statistics": {
          "Impressions": 15000,
          "Clicks": 450
        }
      }
    ]
  }
}
```

---

## update

Изменение параметров кампаний.

### Запрос

```json
{
  "method": "update",
  "params": {
    "Campaigns": [
      {
        "Id": 123456,
        "Name": "Новое название",
        "DailyBudget": {
          "Amount": 5000000000,
          "Mode": "DISTRIBUTED"
        }
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
        "Id": 123456
      }
    ]
  }
}
```

---

## delete

Удаление кампаний.

### Запрос

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

### Ответ

```json
{
  "result": {
    "DeleteResults": [
      {
        "Id": 123456
      },
      {
        "Id": 789012
      }
    ]
  }
}
```

---

## suspend

Приостановка показов кампаний.

### Запрос

```json
{
  "method": "suspend",
  "params": {
    "SelectionCriteria": {
      "Ids": [123456]
    }
  }
}
```

---

## resume

Возобновление показов кампаний.

### Запрос

```json
{
  "method": "resume",
  "params": {
    "SelectionCriteria": {
      "Ids": [123456]
    }
  }
}
```

---

## archive

Архивирование кампаний.

### Запрос

```json
{
  "method": "archive",
  "params": {
    "SelectionCriteria": {
      "Ids": [123456]
    }
  }
}
```

---

## unarchive

Разархивирование кампаний.

### Запрос

```json
{
  "method": "unarchive",
  "params": {
    "SelectionCriteria": {
      "Ids": [123456]
    }
  }
}
```

---

## Примеры использования

### Python: Получение всех активных кампаний

```python
def get_active_campaigns(client):
    response = client.request("campaigns", {
        "method": "get",
        "params": {
            "SelectionCriteria": {
                "States": ["ON"]
            },
            "FieldNames": [
                "Id", "Name", "Status", "State",
                "DailyBudget", "Statistics"
            ]
        }
    })

    campaigns = response.get("Campaigns", [])

    for campaign in campaigns:
        budget = campaign.get("DailyBudget", {}).get("Amount", 0) / 1_000_000
        clicks = campaign.get("Statistics", {}).get("Clicks", 0)
        print(f"{campaign['Name']}: {clicks} кликов, бюджет {budget} ₽")

    return campaigns
```

### Python: Создание текстовой кампании

```python
def create_text_campaign(client, name: str, daily_budget: float):
    response = client.request("campaigns", {
        "method": "add",
        "params": {
            "Campaigns": [{
                "Name": name,
                "StartDate": "2024-01-15",
                "DailyBudget": {
                    "Amount": int(daily_budget * 1_000_000),
                    "Mode": "STANDARD"
                },
                "TextCampaign": {
                    "BiddingStrategy": {
                        "Search": {
                            "BiddingStrategyType": "WB_MAXIMUM_CLICKS",
                            "WbMaximumClicks": {
                                "WeeklySpendLimit": int(daily_budget * 7 * 1_000_000)
                            }
                        },
                        "Network": {
                            "BiddingStrategyType": "SERVING_OFF"
                        }
                    }
                }
            }]
        }
    })

    result = response.get("AddResults", [{}])[0]
    if "Errors" in result:
        raise Exception(result["Errors"])

    return result["Id"]
```

---

[← Обработка ошибок](../concepts/errors.md) | [AdGroups →](./adgroups.md)

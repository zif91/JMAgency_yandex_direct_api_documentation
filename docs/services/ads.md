# Сервис Ads

[← Назад к оглавлению](../README.md)

## Обзор

Сервис **Ads** предназначен для управления объявлениями в Яндекс Директе.

## Endpoints

| Формат | URL |
|--------|-----|
| JSON | `https://api.direct.yandex.com/json/v5/ads` |
| JSON (v501) | `https://api.direct.yandex.com/json/v501/ads` |
| SOAP | `https://api.direct.yandex.com/v5/ads` |
| WSDL | `https://api.direct.yandex.com/v5/ads?wsdl` |

## Методы

| Метод | Описание |
|-------|----------|
| [add](#add) | Создание объявлений |
| [get](#get) | Получение данных об объявлениях |
| [update](#update) | Изменение объявлений |
| [delete](#delete) | Удаление объявлений |
| [suspend](#suspend) | Приостановка показов |
| [resume](#resume) | Возобновление показов |
| [archive](#archive) | Архивирование |
| [unarchive](#unarchive) | Разархивирование |
| [moderate](#moderate) | Отправка на модерацию |

---

## Типы объявлений

| Тип | Описание |
|-----|----------|
| `TEXT_AD` | Текстово-графическое объявление |
| `DYNAMIC_TEXT_AD` | Динамическое объявление |
| `MOBILE_APP_AD` | Реклама мобильного приложения |
| `TEXT_IMAGE_AD` | Графическое объявление |
| `IMAGE_AD` | Баннер |
| `CPC_VIDEO_AD` | Видеообъявление |
| `CPM_BANNER_AD` | Медийный баннер |
| `CPM_VIDEO_AD` | Медийное видео |
| `SMART_AD` | Смарт-баннер |

## Статусы объявления

### State (состояние показов)

| Значение | Описание |
|----------|----------|
| `ON` | Показы включены |
| `OFF` | Показы выключены |
| `SUSPENDED` | Приостановлено пользователем |
| `OFF_BY_MONITORING` | Остановлено мониторингом |
| `ARCHIVED` | Заархивировано |

### Status (статус модерации)

| Значение | Описание |
|----------|----------|
| `DRAFT` | Черновик |
| `MODERATION` | На модерации |
| `PREACCEPTED` | Предварительно принято |
| `ACCEPTED` | Принято |
| `REJECTED` | Отклонено |

---

## add

Создание новых объявлений. Максимум **1000 объявлений** за запрос.

### Запрос (текстовое объявление)

```json
{
  "method": "add",
  "params": {
    "Ads": [
      {
        "AdGroupId": 789012,
        "TextAd": {
          "Title": "Заголовок объявления",
          "Title2": "Дополнительный заголовок",
          "Text": "Текст объявления до 81 символа",
          "Href": "https://example.com/landing",
          "Mobile": "NO",
          "SitelinkSetId": 123,
          "VCardId": 456,
          "AdExtensionIds": [789]
        }
      }
    ]
  }
}
```

### Параметры TextAd

| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `Title` | string | Да | Заголовок (макс. 35 символов) |
| `Title2` | string | Нет | Второй заголовок (макс. 30 символов) |
| `Text` | string | Да | Текст (макс. 81 символ) |
| `Href` | string | Да* | URL перехода |
| `DisplayUrlPath` | string | Нет | Отображаемая ссылка |
| `Mobile` | enum | Нет | `YES`/`NO` — мобильное объявление |
| `SitelinkSetId` | long | Нет | ID набора быстрых ссылок |
| `VCardId` | long | Нет | ID визитки |
| `AdExtensionIds` | array[long] | Нет | ID расширений |
| `AdImageHash` | string | Нет | Хеш изображения |
| `VideoExtension` | object | Нет | Видеодополнение |
| `TurboPageId` | long | Нет | ID турбо-страницы |
| `BusinessId` | long | Нет | ID организации |
| `PreferVCardOverBusiness` | enum | Нет | Приоритет визитки над организацией |

### Ответ

```json
{
  "result": {
    "AddResults": [
      {
        "Id": 111222333
      }
    ]
  }
}
```

---

## get

Получение информации об объявлениях.

### Запрос

```json
{
  "method": "get",
  "params": {
    "SelectionCriteria": {
      "Ids": [111222333],
      "AdGroupIds": [789012],
      "CampaignIds": [123456],
      "Types": ["TEXT_AD"],
      "States": ["ON"],
      "Statuses": ["ACCEPTED"]
    },
    "FieldNames": [
      "Id",
      "AdGroupId",
      "CampaignId",
      "Type",
      "Status",
      "State",
      "StatusClarification"
    ],
    "TextAdFieldNames": [
      "Title",
      "Title2",
      "Text",
      "Href",
      "Mobile",
      "SitelinkSetId",
      "VCardId"
    ],
    "Page": {
      "Limit": 1000,
      "Offset": 0
    }
  }
}
```

### SelectionCriteria

| Параметр | Тип | Описание |
|----------|-----|----------|
| `Ids` | array[long] | ID объявлений (макс. 10000) |
| `AdGroupIds` | array[long] | ID групп (макс. 1000) |
| `CampaignIds` | array[long] | ID кампаний (макс. 10) |
| `Types` | array[enum] | Типы объявлений |
| `States` | array[enum] | Состояния показов |
| `Statuses` | array[enum] | Статусы модерации |

### FieldNames (общие поля)

| Поле | Описание |
|------|----------|
| `Id` | Идентификатор объявления |
| `AdGroupId` | ID группы |
| `CampaignId` | ID кампании |
| `Type` | Тип объявления |
| `Subtype` | Подтип |
| `Status` | Статус модерации |
| `State` | Состояние показов |
| `StatusClarification` | Пояснение к статусу |
| `AdCategories` | Категории объявления |

### Ответ

```json
{
  "result": {
    "Ads": [
      {
        "Id": 111222333,
        "AdGroupId": 789012,
        "CampaignId": 123456,
        "Type": "TEXT_AD",
        "Status": "ACCEPTED",
        "State": "ON",
        "TextAd": {
          "Title": "Заголовок объявления",
          "Title2": "Дополнительный заголовок",
          "Text": "Текст объявления",
          "Href": "https://example.com/landing",
          "Mobile": "NO"
        }
      }
    ]
  }
}
```

---

## update

Изменение параметров объявлений.

### Запрос

```json
{
  "method": "update",
  "params": {
    "Ads": [
      {
        "Id": 111222333,
        "TextAd": {
          "Title": "Новый заголовок",
          "Text": "Новый текст объявления"
        }
      }
    ]
  }
}
```

> **Важно:** После изменения объявление автоматически отправляется на повторную модерацию.

---

## delete

Удаление объявлений.

```json
{
  "method": "delete",
  "params": {
    "SelectionCriteria": {
      "Ids": [111222333, 111222334]
    }
  }
}
```

---

## suspend

Приостановка показов объявлений.

```json
{
  "method": "suspend",
  "params": {
    "SelectionCriteria": {
      "Ids": [111222333]
    }
  }
}
```

---

## resume

Возобновление показов объявлений.

```json
{
  "method": "resume",
  "params": {
    "SelectionCriteria": {
      "Ids": [111222333]
    }
  }
}
```

---

## archive

Архивирование объявлений.

```json
{
  "method": "archive",
  "params": {
    "SelectionCriteria": {
      "Ids": [111222333]
    }
  }
}
```

---

## unarchive

Разархивирование объявлений.

```json
{
  "method": "unarchive",
  "params": {
    "SelectionCriteria": {
      "Ids": [111222333]
    }
  }
}
```

---

## moderate

Отправка объявлений на модерацию.

```json
{
  "method": "moderate",
  "params": {
    "SelectionCriteria": {
      "Ids": [111222333]
    }
  }
}
```

---

## Примеры использования

### Python: Создание текстового объявления

```python
def create_text_ad(client, adgroup_id: int, title: str, text: str, url: str):
    response = client.request("ads", {
        "method": "add",
        "params": {
            "Ads": [{
                "AdGroupId": adgroup_id,
                "TextAd": {
                    "Title": title[:35],  # Ограничение 35 символов
                    "Text": text[:81],    # Ограничение 81 символ
                    "Href": url,
                    "Mobile": "NO"
                }
            }]
        }
    })

    result = response.get("AddResults", [{}])[0]
    if "Errors" in result:
        raise Exception(result["Errors"])

    return result["Id"]
```

### Python: Получение всех объявлений группы

```python
def get_adgroup_ads(client, adgroup_id: int):
    response = client.request("ads", {
        "method": "get",
        "params": {
            "SelectionCriteria": {
                "AdGroupIds": [adgroup_id]
            },
            "FieldNames": ["Id", "Type", "Status", "State"],
            "TextAdFieldNames": ["Title", "Title2", "Text", "Href"]
        }
    })

    return response.get("Ads", [])


# Использование
ads = get_adgroup_ads(client, 789012)
for ad in ads:
    if ad["Type"] == "TEXT_AD":
        print(f"{ad['Id']}: {ad['TextAd']['Title']} - {ad['Status']}")
```

### Python: Массовое управление объявлениями

```python
def manage_ads(client, ad_ids: list, action: str):
    """
    Управление объявлениями.
    action: 'suspend', 'resume', 'archive', 'unarchive', 'moderate'
    """
    valid_actions = ['suspend', 'resume', 'archive', 'unarchive', 'moderate']
    if action not in valid_actions:
        raise ValueError(f"Invalid action. Use one of: {valid_actions}")

    response = client.request("ads", {
        "method": action,
        "params": {
            "SelectionCriteria": {
                "Ids": ad_ids
            }
        }
    })

    results = response.get(f"{action.capitalize()}Results", [])
    successful = [r["Id"] for r in results if "Errors" not in r]
    failed = [r for r in results if "Errors" in r]

    return successful, failed


# Приостановить объявления
suspended, failed = manage_ads(client, [111, 222, 333], "suspend")
print(f"Приостановлено: {len(suspended)}, ошибок: {len(failed)}")
```

---

[← AdGroups](./adgroups.md) | [Keywords →](./keywords.md)

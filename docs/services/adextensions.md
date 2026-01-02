# Сервис AdExtensions

[← Назад к оглавлению](../README.md)

## Обзор

Сервис **AdExtensions** предназначен для управления расширениями объявлений. В настоящее время доступен только один тип расширений — уточнения (callouts).

## Endpoints

| Формат | URL |
|--------|-----|
| JSON | `https://api.direct.yandex.com/json/v5/adextensions` |
| JSON (v501) | `https://api.direct.yandex.com/json/v501/adextensions` |
| SOAP | `https://api.direct.yandex.com/v5/adextensions` |

## Методы

| Метод | Описание |
|-------|----------|
| [add](#add) | Создание расширений |
| [get](#get) | Получение данных о расширениях |
| [delete](#delete) | Удаление расширений |

---

## add

Создание уточнений (callouts).

### Запрос

```json
{
  "method": "add",
  "params": {
    "AdExtensions": [
      {
        "Callout": {
          "CalloutText": "Бесплатная доставка"
        }
      },
      {
        "Callout": {
          "CalloutText": "Гарантия 2 года"
        }
      },
      {
        "Callout": {
          "CalloutText": "Скидки до 50%"
        }
      }
    ]
  }
}
```

### Параметры Callout

| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `CalloutText` | string | Да | Текст уточнения (макс. 25 символов) |

### Ограничения

- Максимум **8** уточнений на объявление
- Текст до **25** символов

### Ответ

```json
{
  "result": {
    "AddResults": [
      {
        "Id": 111222333
      },
      {
        "Id": 111222334
      },
      {
        "Id": 111222335
      }
    ]
  }
}
```

---

## get

Получение информации о расширениях.

### Запрос

```json
{
  "method": "get",
  "params": {
    "SelectionCriteria": {
      "Ids": [111222333, 111222334],
      "Types": ["CALLOUT"],
      "States": ["ON"],
      "Statuses": ["ACCEPTED"]
    },
    "FieldNames": [
      "Id",
      "Type",
      "State",
      "Status",
      "StatusClarification",
      "Associated"
    ],
    "CalloutFieldNames": [
      "CalloutText"
    ],
    "Page": {
      "Limit": 10000,
      "Offset": 0
    }
  }
}
```

### SelectionCriteria

| Параметр | Описание |
|----------|----------|
| `Ids` | ID расширений |
| `Types` | Типы (`CALLOUT`) |
| `States` | Состояния (`ON`, `OFF`, `DELETED`) |
| `Statuses` | Статусы модерации |

### State

| Значение | Описание |
|----------|----------|
| `ON` | Активно |
| `OFF` | Выключено |
| `DELETED` | Удалено |

### Status

| Значение | Описание |
|----------|----------|
| `DRAFT` | Черновик |
| `MODERATION` | На модерации |
| `ACCEPTED` | Принято |
| `REJECTED` | Отклонено |

### Ответ

```json
{
  "result": {
    "AdExtensions": [
      {
        "Id": 111222333,
        "Type": "CALLOUT",
        "State": "ON",
        "Status": "ACCEPTED",
        "Associated": "YES",
        "Callout": {
          "CalloutText": "Бесплатная доставка"
        }
      }
    ]
  }
}
```

---

## delete

Удаление расширений.

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

## Использование уточнений в объявлениях

При создании объявления укажите ID расширений в параметре `AdExtensionIds`:

```json
{
  "method": "add",
  "params": {
    "Ads": [
      {
        "AdGroupId": 789012,
        "TextAd": {
          "Title": "Заголовок объявления",
          "Text": "Текст объявления",
          "Href": "https://example.com",
          "AdExtensionIds": [111222333, 111222334, 111222335]
        }
      }
    ]
  }
}
```

---

## Пример использования (Python)

```python
def create_callouts(client, texts: list):
    """
    Создание уточнений.

    Args:
        texts: Список текстов уточнений (макс. 25 символов каждый)
    """
    extensions = [
        {"Callout": {"CalloutText": text[:25]}}
        for text in texts
    ]

    response = client.request("adextensions", {
        "method": "add",
        "params": {
            "AdExtensions": extensions
        }
    })

    results = response.get("AddResults", [])
    ids = [r["Id"] for r in results if "Id" in r]

    return ids


def get_all_callouts(client):
    """Получение всех активных уточнений."""
    response = client.request("adextensions", {
        "method": "get",
        "params": {
            "SelectionCriteria": {
                "Types": ["CALLOUT"],
                "States": ["ON"]
            },
            "FieldNames": ["Id", "Status", "Associated"],
            "CalloutFieldNames": ["CalloutText"]
        }
    })

    callouts = response.get("AdExtensions", [])

    for callout in callouts:
        text = callout.get("Callout", {}).get("CalloutText", "")
        print(f"ID: {callout['Id']}, Text: {text}, Status: {callout['Status']}")

    return callouts


# Использование
callout_ids = create_callouts(client, [
    "Бесплатная доставка",
    "Гарантия 2 года",
    "Скидки до 50%",
    "Работаем 24/7"
])

print(f"Созданы уточнения: {callout_ids}")
```

---

[← AdImages](./adimages.md) | [Python примеры →](../examples/python.md)

# Сервис RetargetingLists

[← Назад к оглавлению](../README.md)

## Обзор

Сервис **RetargetingLists** предназначен для управления списками ретаргетинга.

## Endpoints

| Формат | URL |
|--------|-----|
| JSON | `https://api.direct.yandex.com/json/v5/retargetinglists` |
| JSON (v501) | `https://api.direct.yandex.com/json/v501/retargetinglists` |
| SOAP | `https://api.direct.yandex.com/v5/retargetinglists` |

## Методы

| Метод | Описание |
|-------|----------|
| [add](#add) | Создание списков ретаргетинга |
| [get](#get) | Получение данных о списках |
| [update](#update) | Изменение списков |
| [delete](#delete) | Удаление списков |

---

## add

Создание нового списка ретаргетинга.

### Запрос

```json
{
  "method": "add",
  "params": {
    "RetargetingLists": [
      {
        "Name": "Посетители сайта за 30 дней",
        "Rules": [
          {
            "RuleType": "ALL",
            "Goals": [
              {
                "GoalId": 12345678,
                "Period": 30
              }
            ]
          }
        ]
      }
    ]
  }
}
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `Name` | string | Да | Название списка |
| `Description` | string | Нет | Описание |
| `Rules` | array | Да | Правила отбора |

### Rules (правила)

| Параметр | Описание |
|----------|----------|
| `RuleType` | `ALL` (все) или `ANY` (любое) |
| `Goals` | Массив целей Метрики |

### Goals (цели)

| Параметр | Описание |
|----------|----------|
| `GoalId` | ID цели в Яндекс Метрике |
| `Period` | Период в днях (1-540) |
| `Operator` | `GREATER_THAN`, `LESS_THAN`, `EQUALS`, `NOT_EQUALS` |
| `Value` | Значение для сравнения |

### Ответ

```json
{
  "result": {
    "AddResults": [
      {
        "Id": 777888999
      }
    ]
  }
}
```

---

## get

Получение информации о списках ретаргетинга.

### Запрос

```json
{
  "method": "get",
  "params": {
    "SelectionCriteria": {
      "Ids": [777888999]
    },
    "FieldNames": [
      "Id",
      "Name",
      "Description",
      "IsAvailable",
      "Rules",
      "Scope"
    ]
  }
}
```

### Ответ

```json
{
  "result": {
    "RetargetingLists": [
      {
        "Id": 777888999,
        "Name": "Посетители сайта за 30 дней",
        "IsAvailable": "YES",
        "Scope": "FOR_RETARGETINGS_AND_AUDIENCES",
        "Rules": [
          {
            "RuleType": "ALL",
            "Goals": [
              {
                "GoalId": 12345678,
                "Period": 30
              }
            ]
          }
        ]
      }
    ]
  }
}
```

---

## update

Изменение списка ретаргетинга.

```json
{
  "method": "update",
  "params": {
    "RetargetingLists": [
      {
        "Id": 777888999,
        "Name": "Обновлённый список",
        "Rules": [
          {
            "RuleType": "ALL",
            "Goals": [
              {
                "GoalId": 12345678,
                "Period": 60
              }
            ]
          }
        ]
      }
    ]
  }
}
```

---

## delete

Удаление списков ретаргетинга.

```json
{
  "method": "delete",
  "params": {
    "SelectionCriteria": {
      "Ids": [777888999]
    }
  }
}
```

---

## Пример использования (Python)

```python
def create_retargeting_list(client, name: str, goal_id: int, period_days: int = 30):
    """Создание списка ретаргетинга."""
    response = client.request("retargetinglists", {
        "method": "add",
        "params": {
            "RetargetingLists": [{
                "Name": name,
                "Rules": [{
                    "RuleType": "ALL",
                    "Goals": [{
                        "GoalId": goal_id,
                        "Period": period_days
                    }]
                }]
            }]
        }
    })

    result = response.get("AddResults", [{}])[0]
    return result.get("Id")


def get_all_retargeting_lists(client):
    """Получение всех списков ретаргетинга."""
    response = client.request("retargetinglists", {
        "method": "get",
        "params": {
            "SelectionCriteria": {},
            "FieldNames": ["Id", "Name", "IsAvailable", "Rules"]
        }
    })

    return response.get("RetargetingLists", [])
```

---

[← Dictionaries](./dictionaries.md) | [Sitelinks →](./sitelinks.md)

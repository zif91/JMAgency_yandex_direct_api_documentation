# Сервис BidModifiers

[← Назад к оглавлению](../README.md)

## Обзор

Сервис **BidModifiers** предназначен для управления корректировками ставок на уровне кампаний и групп объявлений.

## Endpoints

| Формат | URL |
|--------|-----|
| JSON | `https://api.direct.yandex.com/json/v5/bidmodifiers` |
| JSON (v501) | `https://api.direct.yandex.com/json/v501/bidmodifiers` |
| SOAP | `https://api.direct.yandex.com/v5/bidmodifiers` |
| WSDL | `https://api.direct.yandex.com/v5/bidmodifiers?wsdl` |

## Методы

| Метод | Описание |
|-------|----------|
| [add](#add) | Создание корректировок |
| [get](#get) | Получение данных о корректировках |
| [set](#set) | Изменение значений корректировок |
| [delete](#delete) | Удаление корректировок |
| [toggle](#toggle) | Включение/выключение корректировок |

---

## Типы корректировок

| Тип | Описание | Уровень |
|-----|----------|---------|
| `MOBILE_ADJUSTMENT` | Для мобильных устройств | Кампания, Группа |
| `DESKTOP_ADJUSTMENT` | Для десктопов | Кампания, Группа |
| `DEMOGRAPHICS_ADJUSTMENT` | По полу и возрасту | Кампания, Группа |
| `RETARGETING_ADJUSTMENT` | По аудиториям ретаргетинга | Кампания, Группа |
| `REGIONAL_ADJUSTMENT` | По регионам | Кампания, Группа |
| `VIDEO_ADJUSTMENT` | Для видеодополнений | Кампания |
| `SMART_AD_ADJUSTMENT` | Для смарт-объявлений | Кампания |
| `INCOME_GRADE_ADJUSTMENT` | По уровню дохода | Кампания |

---

## add

Создание новых корректировок ставок.

### Запрос (мобильная корректировка)

```json
{
  "method": "add",
  "params": {
    "BidModifiers": [
      {
        "CampaignId": 123456,
        "MobileAdjustment": {
          "BidModifier": 150
        }
      }
    ]
  }
}
```

### Запрос (демографическая корректировка)

```json
{
  "method": "add",
  "params": {
    "BidModifiers": [
      {
        "CampaignId": 123456,
        "DemographicsAdjustments": [
          {
            "Gender": "FEMALE",
            "Age": "AGE_25_34",
            "BidModifier": 120
          },
          {
            "Gender": "MALE",
            "Age": "AGE_35_44",
            "BidModifier": 80
          }
        ]
      }
    ]
  }
}
```

### Запрос (региональная корректировка)

```json
{
  "method": "add",
  "params": {
    "BidModifiers": [
      {
        "CampaignId": 123456,
        "RegionalAdjustments": [
          {
            "RegionId": 1,
            "BidModifier": 130
          },
          {
            "RegionId": 2,
            "BidModifier": 110
          }
        ]
      }
    ]
  }
}
```

### Запрос (корректировка по ретаргетингу)

```json
{
  "method": "add",
  "params": {
    "BidModifiers": [
      {
        "CampaignId": 123456,
        "RetargetingAdjustments": [
          {
            "RetargetingConditionId": 777888,
            "BidModifier": 200
          }
        ]
      }
    ]
  }
}
```

### Значения BidModifier

| Значение | Описание |
|----------|----------|
| `0` | Отключить показы |
| `1-99` | Понижающая корректировка |
| `100` | Без изменений |
| `101-1300` | Повышающая корректировка |

### Пол (Gender)

| Значение | Описание |
|----------|----------|
| `MALE` | Мужской |
| `FEMALE` | Женский |
| `GENDER_ALL` | Любой |

### Возраст (Age)

| Значение | Описание |
|----------|----------|
| `AGE_0_17` | До 18 лет |
| `AGE_18_24` | 18-24 года |
| `AGE_25_34` | 25-34 года |
| `AGE_35_44` | 35-44 года |
| `AGE_45_54` | 45-54 года |
| `AGE_55` | 55+ лет |
| `AGE_ALL` | Любой возраст |

### Ответ

```json
{
  "result": {
    "AddResults": [
      {
        "Id": 999888777
      }
    ]
  }
}
```

---

## get

Получение информации о корректировках.

### Запрос

```json
{
  "method": "get",
  "params": {
    "SelectionCriteria": {
      "CampaignIds": [123456],
      "AdGroupIds": [789012],
      "Ids": [999888777],
      "Types": ["MOBILE_ADJUSTMENT", "DEMOGRAPHICS_ADJUSTMENT"],
      "Levels": ["CAMPAIGN", "AD_GROUP"]
    },
    "FieldNames": [
      "Id",
      "CampaignId",
      "AdGroupId",
      "Type",
      "Level",
      "Enabled"
    ],
    "MobileAdjustmentFieldNames": ["BidModifier"],
    "DemographicsAdjustmentFieldNames": ["Gender", "Age", "BidModifier", "Enabled"],
    "RegionalAdjustmentFieldNames": ["RegionId", "BidModifier", "Enabled"],
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
| `CampaignIds` | array[long] | ID кампаний |
| `AdGroupIds` | array[long] | ID групп |
| `Ids` | array[long] | ID корректировок |
| `Types` | array[enum] | Типы корректировок |
| `Levels` | array[enum] | Уровни: `CAMPAIGN`, `AD_GROUP` |

### Ответ

```json
{
  "result": {
    "BidModifiers": [
      {
        "Id": 999888777,
        "CampaignId": 123456,
        "Type": "MOBILE_ADJUSTMENT",
        "Level": "CAMPAIGN",
        "Enabled": "YES",
        "MobileAdjustment": {
          "BidModifier": 150
        }
      },
      {
        "Id": 999888778,
        "CampaignId": 123456,
        "Type": "DEMOGRAPHICS_ADJUSTMENT",
        "Level": "CAMPAIGN",
        "DemographicsAdjustments": [
          {
            "Gender": "FEMALE",
            "Age": "AGE_25_34",
            "BidModifier": 120,
            "Enabled": "YES"
          }
        ]
      }
    ]
  }
}
```

---

## set

Изменение значений корректировок.

### Запрос

```json
{
  "method": "set",
  "params": {
    "BidModifiers": [
      {
        "Id": 999888777,
        "BidModifier": 180
      }
    ]
  }
}
```

---

## delete

Удаление корректировок.

```json
{
  "method": "delete",
  "params": {
    "SelectionCriteria": {
      "Ids": [999888777, 999888778]
    }
  }
}
```

---

## toggle

Включение или выключение корректировок без удаления.

### Запрос

```json
{
  "method": "toggle",
  "params": {
    "BidModifierToggleItems": [
      {
        "Id": 999888777,
        "Enabled": "NO"
      },
      {
        "Id": 999888778,
        "Enabled": "YES"
      }
    ]
  }
}
```

---

## Примеры использования

### Python: Добавление мобильной корректировки

```python
def add_mobile_adjustment(client, campaign_id: int, modifier: int):
    """
    Добавление корректировки для мобильных устройств.

    Args:
        modifier: 0-1300 (0=отключить, 100=без изменений, 150=+50%)
    """
    response = client.request("bidmodifiers", {
        "method": "add",
        "params": {
            "BidModifiers": [{
                "CampaignId": campaign_id,
                "MobileAdjustment": {
                    "BidModifier": modifier
                }
            }]
        }
    })

    result = response.get("AddResults", [{}])[0]
    if "Errors" in result:
        raise Exception(result["Errors"])

    return result["Id"]


# Увеличить ставки на мобильных на 50%
modifier_id = add_mobile_adjustment(client, 123456, 150)
```

### Python: Добавление демографических корректировок

```python
def add_demographics_adjustments(client, campaign_id: int, adjustments: list):
    """
    Добавление корректировок по полу и возрасту.

    Args:
        adjustments: [{"gender": "FEMALE", "age": "AGE_25_34", "modifier": 120}, ...]
    """
    demographics = [
        {
            "Gender": adj["gender"],
            "Age": adj["age"],
            "BidModifier": adj["modifier"]
        }
        for adj in adjustments
    ]

    response = client.request("bidmodifiers", {
        "method": "add",
        "params": {
            "BidModifiers": [{
                "CampaignId": campaign_id,
                "DemographicsAdjustments": demographics
            }]
        }
    })

    return response.get("AddResults", [])


# Использование
adjustments = [
    {"gender": "FEMALE", "age": "AGE_25_34", "modifier": 130},  # +30%
    {"gender": "FEMALE", "age": "AGE_35_44", "modifier": 120},  # +20%
    {"gender": "MALE", "age": "AGE_45_54", "modifier": 80},     # -20%
]

add_demographics_adjustments(client, 123456, adjustments)
```

### Python: Получение всех корректировок кампании

```python
def get_campaign_modifiers(client, campaign_id: int):
    response = client.request("bidmodifiers", {
        "method": "get",
        "params": {
            "SelectionCriteria": {
                "CampaignIds": [campaign_id]
            },
            "FieldNames": ["Id", "Type", "Level", "Enabled"],
            "MobileAdjustmentFieldNames": ["BidModifier"],
            "DemographicsAdjustmentFieldNames": ["Gender", "Age", "BidModifier"],
            "RegionalAdjustmentFieldNames": ["RegionId", "BidModifier"]
        }
    })

    modifiers = response.get("BidModifiers", [])

    for mod in modifiers:
        print(f"ID: {mod['Id']}, Type: {mod['Type']}, Enabled: {mod['Enabled']}")

        if mod["Type"] == "MOBILE_ADJUSTMENT":
            print(f"  Mobile: {mod['MobileAdjustment']['BidModifier']}%")
        elif mod["Type"] == "DEMOGRAPHICS_ADJUSTMENT":
            for demo in mod.get("DemographicsAdjustments", []):
                print(f"  {demo['Gender']}/{demo['Age']}: {demo['BidModifier']}%")

    return modifiers
```

---

[← Bids](./bids.md) | [Reports →](./reports.md)

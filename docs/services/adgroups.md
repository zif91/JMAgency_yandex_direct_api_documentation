# Сервис AdGroups

[← Назад к оглавлению](../README.md)

## Обзор

Сервис **AdGroups** предназначен для управления группами объявлений в рекламных кампаниях.

## Endpoints

| Формат | URL |
|--------|-----|
| JSON | `https://api.direct.yandex.com/json/v5/adgroups` |
| JSON (v501) | `https://api.direct.yandex.com/json/v501/adgroups` |
| SOAP | `https://api.direct.yandex.com/v5/adgroups` |
| WSDL | `https://api.direct.yandex.com/v5/adgroups?wsdl` |

## Методы

| Метод | Описание |
|-------|----------|
| [add](#add) | Создание групп объявлений |
| [get](#get) | Получение данных о группах |
| [update](#update) | Изменение групп |
| [delete](#delete) | Удаление групп |

---

## Типы групп объявлений

Тип группы определяется типом родительской кампании:

| Тип кампании | Тип группы |
|--------------|------------|
| TEXT_CAMPAIGN | TEXT_AD_GROUP |
| UNIFIED_CAMPAIGN | UNIFIED_AD_GROUP |
| DYNAMIC_TEXT_CAMPAIGN | DYNAMIC_TEXT_AD_GROUP |
| MOBILE_APP_CAMPAIGN | MOBILE_APP_AD_GROUP |
| SMART_CAMPAIGN | SMART_AD_GROUP |
| CPM_BANNER_CAMPAIGN | CPM_BANNER_AD_GROUP |

## Статусы группы

### Status (статус модерации)

| Значение | Описание |
|----------|----------|
| `DRAFT` | Черновик |
| `MODERATION` | На модерации |
| `PREACCEPTED` | Предварительно принята |
| `ACCEPTED` | Принята |
| `REJECTED` | Отклонена |

### ServingStatus (статус показов)

| Значение | Описание |
|----------|----------|
| `ELIGIBLE` | Показы возможны |
| `RARELY_SERVED` | Показы редки |

---

## add

Создание новых групп объявлений. Максимум **1000 групп** за один запрос.

### Запрос

```json
{
  "method": "add",
  "params": {
    "AdGroups": [
      {
        "Name": "Группа объявлений 1",
        "CampaignId": 123456,
        "RegionIds": [1, 10174],
        "NegativeKeywords": ["бесплатно", "скачать"],
        "TrackingParams": "utm_source=yandex&utm_medium=cpc"
      }
    ]
  }
}
```

### Параметры группы

| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `Name` | string | Да | Название (макс. 255 символов) |
| `CampaignId` | long | Да | ID кампании |
| `RegionIds` | array[long] | Да | ID регионов показа |
| `NegativeKeywords` | array[string] | Нет | Минус-фразы группы |
| `NegativeKeywordSharedSetIds` | array[long] | Нет | ID наборов минус-фраз |
| `TrackingParams` | string | Нет | UTM-параметры |
| `RestrictedRegionIds` | array[long] | Нет | Исключённые регионы |

### Параметры для текстовых групп (TextAdGroup)

```json
{
  "TextAdGroup": {
    "FeedId": 12345,
    "FeedCategoryIds": [1, 2, 3]
  }
}
```

### Ответ

```json
{
  "result": {
    "AddResults": [
      {
        "Id": 789012
      }
    ]
  }
}
```

---

## get

Получение информации о группах объявлений.

### Запрос

```json
{
  "method": "get",
  "params": {
    "SelectionCriteria": {
      "CampaignIds": [123456],
      "Ids": [789012, 789013],
      "Types": ["TEXT_AD_GROUP"],
      "Statuses": ["ACCEPTED"],
      "ServingStatuses": ["ELIGIBLE"]
    },
    "FieldNames": [
      "Id",
      "Name",
      "CampaignId",
      "Status",
      "ServingStatus",
      "Type",
      "RegionIds",
      "NegativeKeywords"
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
| `CampaignIds` | array[long] | ID кампаний (макс. 10) |
| `Ids` | array[long] | ID групп (макс. 10000) |
| `Types` | array[enum] | Типы групп |
| `Statuses` | array[enum] | Статусы модерации |
| `ServingStatuses` | array[enum] | Статусы показов |
| `AppIconStatuses` | array[enum] | Статусы иконок (для мобильных) |

### FieldNames

| Поле | Описание |
|------|----------|
| `Id` | Идентификатор группы |
| `Name` | Название |
| `CampaignId` | ID кампании |
| `RegionIds` | ID регионов показа |
| `RestrictedRegionIds` | Исключённые регионы |
| `NegativeKeywords` | Минус-фразы |
| `NegativeKeywordSharedSetIds` | ID наборов минус-фраз |
| `TrackingParams` | UTM-параметры |
| `Status` | Статус модерации |
| `ServingStatus` | Статус показов |
| `Type` | Тип группы |
| `Subtype` | Подтип группы |

### Ответ

```json
{
  "result": {
    "AdGroups": [
      {
        "Id": 789012,
        "Name": "Группа объявлений 1",
        "CampaignId": 123456,
        "Status": "ACCEPTED",
        "ServingStatus": "ELIGIBLE",
        "Type": "TEXT_AD_GROUP",
        "RegionIds": [1, 10174],
        "NegativeKeywords": ["бесплатно", "скачать"]
      }
    ]
  }
}
```

---

## update

Изменение параметров групп объявлений.

### Запрос

```json
{
  "method": "update",
  "params": {
    "AdGroups": [
      {
        "Id": 789012,
        "Name": "Новое название группы",
        "RegionIds": [1, 213],
        "NegativeKeywords": ["бесплатно", "скачать", "торрент"]
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
        "Id": 789012
      }
    ]
  }
}
```

---

## delete

Удаление групп объявлений.

### Запрос

```json
{
  "method": "delete",
  "params": {
    "SelectionCriteria": {
      "Ids": [789012, 789013]
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
        "Id": 789012
      },
      {
        "Id": 789013
      }
    ]
  }
}
```

---

## Регионы (RegionIds)

Основные коды регионов:

| Код | Регион |
|-----|--------|
| `0` | Все регионы |
| `1` | Москва и область |
| `2` | Санкт-Петербург и область |
| `10174` | Россия (вся) |
| `166` | Украина |
| `149` | Беларусь |
| `159` | Казахстан |

> Полный список регионов можно получить через сервис [Dictionaries](./dictionaries.md).

---

## Примеры использования

### Python: Получение групп кампании

```python
def get_campaign_adgroups(client, campaign_id: int):
    response = client.request("adgroups", {
        "method": "get",
        "params": {
            "SelectionCriteria": {
                "CampaignIds": [campaign_id]
            },
            "FieldNames": [
                "Id", "Name", "Status", "ServingStatus",
                "RegionIds", "NegativeKeywords"
            ]
        }
    })

    return response.get("AdGroups", [])


# Использование
adgroups = get_campaign_adgroups(client, 123456)
for group in adgroups:
    print(f"{group['Id']}: {group['Name']} - {group['Status']}")
```

### Python: Создание группы с минус-фразами

```python
def create_adgroup(client, campaign_id: int, name: str, regions: list, negatives: list = None):
    params = {
        "Name": name,
        "CampaignId": campaign_id,
        "RegionIds": regions
    }

    if negatives:
        params["NegativeKeywords"] = negatives

    response = client.request("adgroups", {
        "method": "add",
        "params": {
            "AdGroups": [params]
        }
    })

    result = response.get("AddResults", [{}])[0]
    if "Errors" in result:
        raise Exception(result["Errors"])

    return result["Id"]


# Использование
adgroup_id = create_adgroup(
    client,
    campaign_id=123456,
    name="Новая группа",
    regions=[1, 2],  # Москва и Санкт-Петербург
    negatives=["бесплатно", "скачать"]
)
```

### Python: Массовое обновление регионов

```python
def update_adgroups_regions(client, adgroup_ids: list, region_ids: list):
    adgroups = [
        {"Id": adgroup_id, "RegionIds": region_ids}
        for adgroup_id in adgroup_ids
    ]

    response = client.request("adgroups", {
        "method": "update",
        "params": {
            "AdGroups": adgroups
        }
    })

    results = response.get("UpdateResults", [])

    successful = [r["Id"] for r in results if "Errors" not in r]
    failed = [r for r in results if "Errors" in r]

    return successful, failed
```

---

[← Campaigns](./campaigns.md) | [Ads →](./ads.md)

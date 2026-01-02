# Сервис Dictionaries

[← Назад к оглавлению](../README.md)

## Обзор

Сервис **Dictionaries** предназначен для получения справочных данных: регионов, часовых поясов, валют, ограничений и другой информации.

## Endpoints

| Формат | URL |
|--------|-----|
| JSON | `https://api.direct.yandex.com/json/v5/dictionaries` |
| JSON (v501) | `https://api.direct.yandex.com/json/v501/dictionaries` |
| SOAP | `https://api.direct.yandex.com/v5/dictionaries` |

## Методы

| Метод | Описание |
|-------|----------|
| [get](#get) | Получение справочных данных |

---

## get

Получение различных справочников.

### Запрос

```json
{
  "method": "get",
  "params": {
    "DictionaryNames": [
      "GeoRegions",
      "TimeZones",
      "Currencies",
      "Constants",
      "AdCategories",
      "OperationSystemVersions",
      "ProductivityAssertions",
      "SupplySidePlatforms",
      "Interests",
      "AudienceCriteriaTypes",
      "AudienceDemographicProfiles",
      "AudienceInterests",
      "FilterSchemas"
    ]
  }
}
```

### Доступные справочники

| Справочник | Описание |
|------------|----------|
| `GeoRegions` | Регионы (страны, города) |
| `TimeZones` | Часовые пояса |
| `Currencies` | Валюты и курсы |
| `Constants` | Константы API |
| `AdCategories` | Категории объявлений |
| `OperationSystemVersions` | Версии ОС |
| `ProductivityAssertions` | Критерии продуктивности |
| `SupplySidePlatforms` | SSP-площадки |
| `Interests` | Интересы аудитории |
| `AudienceCriteriaTypes` | Типы критериев аудитории |
| `AudienceDemographicProfiles` | Демографические профили |
| `AudienceInterests` | Интересы для таргетинга |
| `FilterSchemas` | Схемы фильтров |

---

## GeoRegions

Справочник географических регионов.

### Запрос

```json
{
  "method": "get",
  "params": {
    "DictionaryNames": ["GeoRegions"]
  }
}
```

### Ответ

```json
{
  "result": {
    "GeoRegions": [
      {
        "GeoRegionId": 225,
        "GeoRegionName": "Россия",
        "GeoRegionType": "COUNTRY",
        "ParentId": 10000
      },
      {
        "GeoRegionId": 1,
        "GeoRegionName": "Москва и Московская область",
        "GeoRegionType": "REGION",
        "ParentId": 225
      },
      {
        "GeoRegionId": 213,
        "GeoRegionName": "Москва",
        "GeoRegionType": "CITY",
        "ParentId": 1
      }
    ]
  }
}
```

### Типы регионов

| Тип | Описание |
|-----|----------|
| `WORLD` | Мир |
| `CONTINENT` | Континент |
| `REGION_LEVEL_1` | Регион уровня 1 |
| `COUNTRY` | Страна |
| `REGION` | Регион (область) |
| `CITY` | Город |
| `CITY_DISTRICT` | Район города |
| `VILLAGE` | Населённый пункт |

---

## TimeZones

Справочник часовых поясов.

### Ответ

```json
{
  "result": {
    "TimeZones": [
      {
        "TimeZone": "Europe/Moscow",
        "TimeZoneName": "Москва (UTC+3)"
      },
      {
        "TimeZone": "Europe/Kiev",
        "TimeZoneName": "Киев (UTC+2)"
      },
      {
        "TimeZone": "Asia/Almaty",
        "TimeZoneName": "Алматы (UTC+6)"
      }
    ]
  }
}
```

---

## Currencies

Справочник валют и курсов.

### Ответ

```json
{
  "result": {
    "Currencies": [
      {
        "Currency": "RUB",
        "Properties": [
          {
            "Name": "MIN_PRICE",
            "Value": "300000"
          },
          {
            "Name": "MIN_DAILY_BUDGET",
            "Value": "300000000"
          }
        ],
        "Rate": "1.0",
        "RateWithVAT": "1.2"
      },
      {
        "Currency": "USD",
        "Rate": "75.5",
        "RateWithVAT": "90.6"
      }
    ]
  }
}
```

---

## Constants

Константы API (лимиты, ограничения).

### Ответ

```json
{
  "result": {
    "Constants": [
      {
        "Name": "MAX_KEYWORDS_PER_AD_GROUP",
        "Value": "200"
      },
      {
        "Name": "MAX_ADS_PER_AD_GROUP",
        "Value": "50"
      },
      {
        "Name": "MAX_AD_GROUPS_PER_CAMPAIGN",
        "Value": "1000"
      },
      {
        "Name": "MAX_CAMPAIGNS_PER_REQUEST",
        "Value": "10"
      }
    ]
  }
}
```

---

## Пример использования (Python)

```python
class DictionaryManager:
    def __init__(self, client):
        self.client = client
        self._cache = {}

    def get_regions(self, force_refresh: bool = False):
        """Получение справочника регионов с кешированием."""
        if "regions" not in self._cache or force_refresh:
            response = self.client.request("dictionaries", {
                "method": "get",
                "params": {
                    "DictionaryNames": ["GeoRegions"]
                }
            })
            self._cache["regions"] = response.get("GeoRegions", [])

        return self._cache["regions"]

    def find_region_by_name(self, name: str):
        """Поиск региона по названию."""
        regions = self.get_regions()
        name_lower = name.lower()

        for region in regions:
            if name_lower in region["GeoRegionName"].lower():
                return region

        return None

    def get_child_regions(self, parent_id: int):
        """Получение дочерних регионов."""
        regions = self.get_regions()
        return [r for r in regions if r.get("ParentId") == parent_id]

    def get_timezones(self):
        """Получение справочника часовых поясов."""
        if "timezones" not in self._cache:
            response = self.client.request("dictionaries", {
                "method": "get",
                "params": {
                    "DictionaryNames": ["TimeZones"]
                }
            })
            self._cache["timezones"] = response.get("TimeZones", [])

        return self._cache["timezones"]

    def get_api_constants(self):
        """Получение констант API."""
        response = self.client.request("dictionaries", {
            "method": "get",
            "params": {
                "DictionaryNames": ["Constants"]
            }
        })

        constants = {}
        for const in response.get("Constants", []):
            constants[const["Name"]] = const["Value"]

        return constants


# Использование
dm = DictionaryManager(client)

# Найти регион
moscow = dm.find_region_by_name("Москва")
print(f"ID Москвы: {moscow['GeoRegionId']}")

# Получить города России
russia_children = dm.get_child_regions(225)

# Получить лимиты
limits = dm.get_api_constants()
print(f"Макс. ключевых фраз в группе: {limits['MAX_KEYWORDS_PER_AD_GROUP']}")
```

---

[← AgencyClients](./agencyclients.md) | [RetargetingLists →](./retargetinglists.md)

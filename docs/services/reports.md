# Сервис Reports

[← Назад к оглавлению](../README.md)

## Обзор

Сервис **Reports** предназначен для формирования и получения статистических отчётов по рекламным кампаниям.

## Endpoint

```
https://api.direct.yandex.com/json/v5/reports
```

> **Важно:** Сервис Reports имеет особый формат запросов и ответов, отличающийся от других сервисов API.

---

## Типы отчётов

| Тип | Описание | Группировка |
|-----|----------|-------------|
| `ACCOUNT_PERFORMANCE_REPORT` | По аккаунту | — |
| `CAMPAIGN_PERFORMANCE_REPORT` | По кампаниям | CampaignId |
| `ADGROUP_PERFORMANCE_REPORT` | По группам объявлений | AdGroupId |
| `AD_PERFORMANCE_REPORT` | По объявлениям | AdId |
| `CRITERIA_PERFORMANCE_REPORT` | По условиям показа | CriteriaId, CriteriaType |
| `CUSTOM_REPORT` | Произвольный | — |
| `SEARCH_QUERY_PERFORMANCE_REPORT` | По поисковым запросам | Query |
| `REACH_AND_FREQUENCY_PERFORMANCE_REPORT` | По охвату и частоте | CampaignId |

---

## Процесс получения отчёта

```
┌─────────────────────────────────────────────────────────────┐
│                      Отправка запроса                        │
└────────────────────────────┬────────────────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
    ┌─────────────────┐           ┌─────────────────┐
    │   HTTP 200 OK   │           │  HTTP 201/202   │
    │  (онлайн-режим) │           │ (офлайн-режим)  │
    └────────┬────────┘           └────────┬────────┘
             │                             │
             ▼                             ▼
    ┌─────────────────┐           ┌─────────────────┐
    │  Отчёт готов!   │           │   Ожидание...   │
    │   (TSV в теле)  │           │ (повторить по   │
    └─────────────────┘           │   retryIn)      │
                                  └────────┬────────┘
                                           │
                                           ▼
                                  ┌─────────────────┐
                                  │   HTTP 200 OK   │
                                  │   Отчёт готов!  │
                                  └─────────────────┘
```

### HTTP-коды ответов

| Код | Описание | Действие |
|-----|----------|----------|
| `200` | Отчёт готов | Обработать TSV в теле ответа |
| `201` | Отчёт в очереди | Повторить запрос позже |
| `202` | Отчёт формируется | Повторить через `retryIn` секунд |
| `400` | Ошибка запроса | Исправить параметры |
| `500` | Ошибка сервера | Повторить позже |

---

## Структура запроса

```json
{
  "params": {
    "ReportName": "Campaign Performance Report",
    "ReportType": "CAMPAIGN_PERFORMANCE_REPORT",
    "DateRangeType": "LAST_7_DAYS",
    "Format": "TSV",
    "IncludeVAT": "NO",
    "IncludeDiscount": "NO",
    "SelectionCriteria": {
      "Filter": [
        {
          "Field": "Impressions",
          "Operator": "GREATER_THAN",
          "Values": ["100"]
        }
      ]
    },
    "FieldNames": [
      "Date",
      "CampaignId",
      "CampaignName",
      "Impressions",
      "Clicks",
      "Cost"
    ],
    "OrderBy": [
      {
        "Field": "Date",
        "SortOrder": "ASCENDING"
      }
    ],
    "Page": {
      "Limit": 10000
    }
  }
}
```

---

## Параметры отчёта

### ReportName (обязательный)

Название отчёта. Должно быть уникальным для офлайн-режима.

### ReportType (обязательный)

Тип отчёта, определяющий набор доступных полей.

### DateRangeType (обязательный)

| Значение | Описание |
|----------|----------|
| `TODAY` | Текущий день |
| `YESTERDAY` | Вчерашний день |
| `LAST_3_DAYS` | Последние 3 дня |
| `LAST_5_DAYS` | Последние 5 дней |
| `LAST_7_DAYS` | Последние 7 дней |
| `LAST_14_DAYS` | Последние 14 дней |
| `LAST_30_DAYS` | Последние 30 дней |
| `LAST_90_DAYS` | Последние 90 дней |
| `LAST_365_DAYS` | Последние 365 дней |
| `THIS_WEEK_MON_TODAY` | С понедельника по сегодня |
| `THIS_WEEK_SUN_TODAY` | С воскресенья по сегодня |
| `LAST_WEEK` | Прошлая неделя |
| `THIS_MONTH` | Текущий месяц |
| `LAST_MONTH` | Прошлый месяц |
| `ALL_TIME` | Вся доступная статистика |
| `CUSTOM_DATE` | Произвольный период |
| `AUTO` | Период с возможными изменениями |

При `CUSTOM_DATE` указывайте `DateFrom` и `DateTo` в `SelectionCriteria`.

### Format (обязательный)

На данный момент поддерживается только `TSV`.

### IncludeVAT (обязательный)

- `YES` — включать НДС в денежные значения
- `NO` — без НДС

### FieldNames (обязательный)

Список полей для включения в отчёт. Зависит от `ReportType`.

---

## Основные поля отчётов

### Сегменты (группировка)

| Поле | Описание |
|------|----------|
| `Date` | Дата |
| `CampaignId` | ID кампании |
| `AdGroupId` | ID группы |
| `AdId` | ID объявления |
| `CriteriaId` | ID условия показа |
| `Query` | Поисковый запрос |
| `Device` | Устройство |
| `Slot` | Место показа |
| `CarrierType` | Тип подключения |
| `Age` | Возраст аудитории |
| `Gender` | Пол аудитории |
| `TargetingLocationId` | ID региона показа |

### Метрики

| Поле | Описание |
|------|----------|
| `Impressions` | Показы |
| `Clicks` | Клики |
| `Cost` | Расход |
| `Ctr` | CTR (%) |
| `AvgCpc` | Средняя цена клика |
| `AvgCpm` | Средняя цена 1000 показов |
| `AvgImpressionPosition` | Средняя позиция показа |
| `AvgClickPosition` | Средняя позиция клика |
| `BounceRate` | Показатель отказов |
| `AvgPageviews` | Среднее число просмотров |
| `ConversionRate` | Коэффициент конверсии |
| `Conversions` | Конверсии |
| `CostPerConversion` | Цена конверсии |
| `GoalsRoi` | ROI по целям |
| `Revenue` | Доход |

### Атрибуты

| Поле | Описание |
|------|----------|
| `CampaignName` | Название кампании |
| `AdGroupName` | Название группы |
| `Criterion` | Условие показа |
| `CriterionType` | Тип условия |
| `AdNetworkType` | Тип площадки |
| `MatchType` | Тип соответствия |

---

## SelectionCriteria

### Filter

Фильтрация данных:

```json
{
  "Filter": [
    {
      "Field": "Clicks",
      "Operator": "GREATER_THAN",
      "Values": ["10"]
    },
    {
      "Field": "CampaignId",
      "Operator": "IN",
      "Values": ["123456", "789012"]
    }
  ]
}
```

### Операторы фильтрации

| Оператор | Описание |
|----------|----------|
| `EQUALS` | Равно |
| `NOT_EQUALS` | Не равно |
| `IN` | В списке |
| `NOT_IN` | Не в списке |
| `LESS_THAN` | Меньше |
| `GREATER_THAN` | Больше |
| `STARTS_WITH_IGNORE_CASE` | Начинается с |
| `DOES_NOT_START_WITH_IGNORE_CASE` | Не начинается с |
| `STARTS_WITH_ANY_IGNORE_CASE` | Начинается с любого из |
| `DOES_NOT_START_WITH_ALL_IGNORE_CASE` | Не начинается ни с одного |

### DateFrom / DateTo

Для `CUSTOM_DATE`:

```json
{
  "SelectionCriteria": {
    "DateFrom": "2024-01-01",
    "DateTo": "2024-01-31"
  }
}
```

---

## HTTP-заголовки

### Запрос

```http
Authorization: Bearer {token}
Accept-Language: ru
Content-Type: application/json
processingMode: auto
returnMoneyInMicros: false
skipReportHeader: true
skipColumnHeader: false
skipReportSummary: true
```

### Специальные заголовки

| Заголовок | Описание | Значение |
|-----------|----------|----------|
| `processingMode` | Режим обработки | `auto`, `online`, `offline` |
| `returnMoneyInMicros` | Формат денег | `true`, `false` |
| `skipReportHeader` | Пропустить заголовок | `true`, `false` |
| `skipColumnHeader` | Пропустить названия колонок | `true`, `false` |
| `skipReportSummary` | Пропустить итоги | `true`, `false` |

### Ответ

```http
retryIn: 30
RequestId: 12345678901234567890
```

---

## Примеры запросов

### Отчёт по кампаниям за последнюю неделю

```json
{
  "params": {
    "ReportName": "Weekly Campaign Report",
    "ReportType": "CAMPAIGN_PERFORMANCE_REPORT",
    "DateRangeType": "LAST_7_DAYS",
    "Format": "TSV",
    "IncludeVAT": "NO",
    "SelectionCriteria": {},
    "FieldNames": [
      "Date",
      "CampaignName",
      "Impressions",
      "Clicks",
      "Ctr",
      "Cost",
      "AvgCpc"
    ],
    "OrderBy": [
      {"Field": "Date", "SortOrder": "ASCENDING"}
    ]
  }
}
```

### Отчёт по ключевым фразам с фильтрацией

```json
{
  "params": {
    "ReportName": "Keywords with Clicks",
    "ReportType": "CRITERIA_PERFORMANCE_REPORT",
    "DateRangeType": "LAST_30_DAYS",
    "Format": "TSV",
    "IncludeVAT": "NO",
    "SelectionCriteria": {
      "Filter": [
        {"Field": "Clicks", "Operator": "GREATER_THAN", "Values": ["5"]},
        {"Field": "CriterionType", "Operator": "EQUALS", "Values": ["KEYWORD"]}
      ]
    },
    "FieldNames": [
      "CampaignName",
      "AdGroupName",
      "Criterion",
      "Impressions",
      "Clicks",
      "Ctr",
      "Cost",
      "AvgCpc",
      "ConversionRate"
    ]
  }
}
```

### Отчёт по поисковым запросам

```json
{
  "params": {
    "ReportName": "Search Queries Report",
    "ReportType": "SEARCH_QUERY_PERFORMANCE_REPORT",
    "DateRangeType": "LAST_14_DAYS",
    "Format": "TSV",
    "IncludeVAT": "NO",
    "SelectionCriteria": {},
    "FieldNames": [
      "Query",
      "CampaignName",
      "AdGroupName",
      "Criterion",
      "Impressions",
      "Clicks",
      "Cost"
    ],
    "OrderBy": [
      {"Field": "Clicks", "SortOrder": "DESCENDING"}
    ],
    "Page": {"Limit": 5000}
  }
}
```

---

## Пример кода (Python)

```python
import requests
import time
import pandas as pd
from io import StringIO


class ReportManager:
    """Менеджер для работы с отчётами API Яндекс Директ."""

    def __init__(self, token: str, login: str = None):
        self.token = token
        self.login = login
        self.url = "https://api.direct.yandex.com/json/v5/reports"

    def get_report(self, report_definition: dict, max_retries: int = 10) -> pd.DataFrame:
        """
        Запрашивает и получает отчёт.

        Args:
            report_definition: Параметры отчёта
            max_retries: Максимум попыток для офлайн-режима

        Returns:
            pandas DataFrame с данными отчёта
        """
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept-Language": "ru",
            "Content-Type": "application/json",
            "processingMode": "auto",
            "returnMoneyInMicros": "false",
            "skipReportHeader": "true",
            "skipColumnHeader": "false",
            "skipReportSummary": "true"
        }

        if self.login:
            headers["Client-Login"] = self.login

        body = {"params": report_definition}

        for attempt in range(max_retries):
            try:
                response = requests.post(self.url, json=body, headers=headers)

                if response.status_code == 200:
                    print("Отчёт получен успешно!")
                    return self._parse_tsv(response.text)

                elif response.status_code in [201, 202]:
                    retry_in = int(response.headers.get("retryIn", 30))
                    print(f"Отчёт формируется. Ожидание {retry_in} сек... "
                          f"(попытка {attempt + 1}/{max_retries})")
                    time.sleep(retry_in)

                elif response.status_code == 400:
                    error = response.json()
                    raise Exception(f"Ошибка запроса: {error}")

                elif response.status_code >= 500:
                    print(f"Ошибка сервера {response.status_code}. Повтор...")
                    time.sleep(30)

                else:
                    raise Exception(f"Неожиданный статус: {response.status_code}")

            except requests.RequestException as e:
                print(f"Сетевая ошибка: {e}. Повтор...")
                time.sleep(30)

        raise Exception("Не удалось получить отчёт после нескольких попыток")

    def _parse_tsv(self, tsv_data: str) -> pd.DataFrame:
        """Парсит TSV-данные в DataFrame."""
        lines = tsv_data.strip().split('\n')

        if len(lines) < 2:
            return pd.DataFrame()

        # Первая строка — заголовки
        df = pd.read_csv(StringIO(tsv_data), sep='\t')

        return df


# Использование
if __name__ == "__main__":
    TOKEN = "YOUR_OAUTH_TOKEN"

    manager = ReportManager(TOKEN)

    report_def = {
        "ReportName": "Campaign Performance",
        "ReportType": "CAMPAIGN_PERFORMANCE_REPORT",
        "DateRangeType": "LAST_7_DAYS",
        "Format": "TSV",
        "IncludeVAT": "NO",
        "SelectionCriteria": {},
        "FieldNames": [
            "Date", "CampaignName", "Impressions",
            "Clicks", "Ctr", "Cost"
        ],
        "OrderBy": [{"Field": "Date", "SortOrder": "ASCENDING"}]
    }

    df = manager.get_report(report_def)
    print(df.head(10))
```

---

## Денежные значения

По умолчанию денежные значения возвращаются в **микроединицах**.

Для получения в основной валюте:

```http
returnMoneyInMicros: false
```

---

[← BidModifiers](./bidmodifiers.md) | [Clients →](./clients.md)

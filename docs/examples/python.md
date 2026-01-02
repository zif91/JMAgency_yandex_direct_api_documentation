# Примеры на Python

[← Назад к оглавлению](../README.md)

## Базовый клиент API

### Установка зависимостей

```bash
pip install requests pandas
```

### Базовый класс клиента

```python
import requests
import time
from typing import Optional, Dict, Any, List


class YandexDirectError(Exception):
    """Ошибка API Яндекс Директа."""

    def __init__(self, code: int, message: str, details: str = "", request_id: str = ""):
        self.code = code
        self.message = message
        self.details = details
        self.request_id = request_id
        super().__init__(f"[{code}] {message}: {details}")


class YandexDirectClient:
    """Клиент для работы с API Яндекс Директа v5."""

    BASE_URL = "https://api.direct.yandex.com/json/v5"
    SANDBOX_URL = "https://api-sandbox.direct.yandex.com/json/v5"

    def __init__(
        self,
        token: str,
        login: Optional[str] = None,
        use_sandbox: bool = False,
        use_operator_units: bool = False,
        language: str = "ru"
    ):
        """
        Инициализация клиента.

        Args:
            token: OAuth-токен
            login: Логин клиента (для агентств)
            use_sandbox: Использовать песочницу
            use_operator_units: Использовать баллы агентства
            language: Язык сообщений (ru, en, tr)
        """
        self.token = token
        self.login = login
        self.use_operator_units = use_operator_units
        self.language = language
        self.base_url = self.SANDBOX_URL if use_sandbox else self.BASE_URL

        # Статистика баллов
        self.units_spent = 0
        self.units_remaining = 0
        self.units_daily_limit = 0

    def _get_headers(self) -> Dict[str, str]:
        """Формирование HTTP-заголовков."""
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept-Language": self.language,
            "Content-Type": "application/json; charset=utf-8"
        }

        if self.login:
            headers["Client-Login"] = self.login

        if self.use_operator_units:
            headers["Use-Operator-Units"] = "true"

        return headers

    def _parse_units(self, units_header: str) -> None:
        """Парсинг заголовка Units."""
        if units_header:
            parts = units_header.split("/")
            if len(parts) == 3:
                self.units_spent = int(parts[0])
                self.units_remaining = int(parts[1])
                self.units_daily_limit = int(parts[2])

    def request(
        self,
        service: str,
        body: Dict[str, Any],
        timeout: int = 60,
        retries: int = 3
    ) -> Dict[str, Any]:
        """
        Выполнение запроса к API.

        Args:
            service: Название сервиса (campaigns, adgroups и т.д.)
            body: Тело запроса
            timeout: Таймаут в секундах
            retries: Количество повторных попыток

        Returns:
            Результат запроса (содержимое поля result)

        Raises:
            YandexDirectError: При ошибке API
        """
        url = f"{self.base_url}/{service}"
        headers = self._get_headers()

        last_error = None

        for attempt in range(retries):
            try:
                response = requests.post(
                    url,
                    json=body,
                    headers=headers,
                    timeout=timeout
                )

                # Парсинг заголовка Units
                self._parse_units(response.headers.get("Units", ""))

                # Проверка HTTP-статуса
                if response.status_code >= 500:
                    wait_time = 2 ** attempt * 5
                    print(f"Ошибка сервера {response.status_code}. "
                          f"Повтор через {wait_time} сек...")
                    time.sleep(wait_time)
                    continue

                data = response.json()

                # Проверка на ошибку API
                if "error" in data:
                    error = data["error"]
                    raise YandexDirectError(
                        code=error.get("error_code", 0),
                        message=error.get("error_string", "Unknown error"),
                        details=error.get("error_detail", ""),
                        request_id=error.get("request_id", "")
                    )

                return data.get("result", data)

            except requests.RequestException as e:
                last_error = e
                wait_time = 2 ** attempt * 5
                print(f"Сетевая ошибка: {e}. Повтор через {wait_time} сек...")
                time.sleep(wait_time)

        raise last_error or Exception("Неизвестная ошибка")

    def get_units_info(self) -> Dict[str, Any]:
        """Получение информации о баллах."""
        return {
            "spent": self.units_spent,
            "remaining": self.units_remaining,
            "daily_limit": self.units_daily_limit,
            "usage_percent": round(
                (self.units_daily_limit - self.units_remaining) /
                self.units_daily_limit * 100, 2
            ) if self.units_daily_limit > 0 else 0
        }
```

---

## Примеры использования

### 1. Получение списка кампаний

```python
def get_campaigns(client: YandexDirectClient, states: List[str] = None):
    """
    Получение списка кампаний.

    Args:
        states: Фильтр по состояниям (ON, OFF, SUSPENDED и т.д.)
    """
    selection = {}
    if states:
        selection["States"] = states

    response = client.request("campaigns", {
        "method": "get",
        "params": {
            "SelectionCriteria": selection,
            "FieldNames": [
                "Id", "Name", "Status", "State",
                "Type", "DailyBudget", "Statistics"
            ]
        }
    })

    campaigns = response.get("Campaigns", [])

    for campaign in campaigns:
        budget = campaign.get("DailyBudget", {}).get("Amount", 0) / 1_000_000
        stats = campaign.get("Statistics", {})
        clicks = stats.get("Clicks", 0)
        impressions = stats.get("Impressions", 0)

        print(f"[{campaign['Id']}] {campaign['Name']}")
        print(f"    Статус: {campaign['Status']}, Состояние: {campaign['State']}")
        print(f"    Бюджет: {budget:.2f} ₽, Клики: {clicks}, Показы: {impressions}")
        print()

    return campaigns


# Использование
client = YandexDirectClient(token="YOUR_TOKEN")
active_campaigns = get_campaigns(client, states=["ON"])
```

### 2. Создание полной структуры кампании

```python
def create_campaign_structure(
    client: YandexDirectClient,
    campaign_name: str,
    daily_budget: float,
    adgroup_name: str,
    regions: List[int],
    keywords: List[str],
    ad_title: str,
    ad_text: str,
    ad_url: str
) -> Dict[str, int]:
    """
    Создание полной структуры: кампания → группа → объявление + ключевые фразы.

    Returns:
        {"campaign_id": ..., "adgroup_id": ..., "ad_id": ..., "keyword_ids": [...]}
    """
    result = {}

    # 1. Создание кампании
    campaign_response = client.request("campaigns", {
        "method": "add",
        "params": {
            "Campaigns": [{
                "Name": campaign_name,
                "StartDate": time.strftime("%Y-%m-%d"),
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

    campaign_id = campaign_response["AddResults"][0]["Id"]
    result["campaign_id"] = campaign_id
    print(f"Создана кампания ID: {campaign_id}")

    # 2. Создание группы объявлений
    adgroup_response = client.request("adgroups", {
        "method": "add",
        "params": {
            "AdGroups": [{
                "Name": adgroup_name,
                "CampaignId": campaign_id,
                "RegionIds": regions
            }]
        }
    })

    adgroup_id = adgroup_response["AddResults"][0]["Id"]
    result["adgroup_id"] = adgroup_id
    print(f"Создана группа ID: {adgroup_id}")

    # 3. Создание объявления
    ad_response = client.request("ads", {
        "method": "add",
        "params": {
            "Ads": [{
                "AdGroupId": adgroup_id,
                "TextAd": {
                    "Title": ad_title[:35],
                    "Text": ad_text[:81],
                    "Href": ad_url,
                    "Mobile": "NO"
                }
            }]
        }
    })

    ad_id = ad_response["AddResults"][0]["Id"]
    result["ad_id"] = ad_id
    print(f"Создано объявление ID: {ad_id}")

    # 4. Добавление ключевых фраз
    keywords_data = [
        {
            "Keyword": kw,
            "AdGroupId": adgroup_id
        }
        for kw in keywords
    ]

    keywords_response = client.request("keywords", {
        "method": "add",
        "params": {
            "Keywords": keywords_data
        }
    })

    keyword_ids = [r["Id"] for r in keywords_response["AddResults"] if "Id" in r]
    result["keyword_ids"] = keyword_ids
    print(f"Добавлено ключевых фраз: {len(keyword_ids)}")

    return result


# Использование
structure = create_campaign_structure(
    client,
    campaign_name="Тестовая кампания",
    daily_budget=1000,
    adgroup_name="Основная группа",
    regions=[1, 2],  # Москва и СПб
    keywords=["купить товар", "заказать товар", "товар цена"],
    ad_title="Купите товар со скидкой",
    ad_text="Лучшие цены на товары. Доставка бесплатно!",
    ad_url="https://example.com"
)
```

### 3. Получение статистики (Reports)

```python
import pandas as pd
from io import StringIO


class ReportManager:
    """Менеджер отчётов."""

    def __init__(self, client: YandexDirectClient):
        self.client = client
        self.reports_url = f"{client.base_url}/reports"

    def get_report(
        self,
        report_type: str,
        field_names: List[str],
        date_range: str = "LAST_7_DAYS",
        filters: List[Dict] = None,
        report_name: str = None
    ) -> pd.DataFrame:
        """
        Получение отчёта.

        Args:
            report_type: Тип отчёта (CAMPAIGN_PERFORMANCE_REPORT и т.д.)
            field_names: Список полей
            date_range: Период (LAST_7_DAYS, LAST_30_DAYS и т.д.)
            filters: Фильтры
            report_name: Название отчёта
        """
        headers = {
            "Authorization": f"Bearer {self.client.token}",
            "Accept-Language": self.client.language,
            "Content-Type": "application/json",
            "processingMode": "auto",
            "returnMoneyInMicros": "false",
            "skipReportHeader": "true",
            "skipColumnHeader": "false",
            "skipReportSummary": "true"
        }

        if self.client.login:
            headers["Client-Login"] = self.client.login

        selection = {}
        if filters:
            selection["Filter"] = filters

        body = {
            "params": {
                "ReportName": report_name or f"Report_{int(time.time())}",
                "ReportType": report_type,
                "DateRangeType": date_range,
                "Format": "TSV",
                "IncludeVAT": "NO",
                "SelectionCriteria": selection,
                "FieldNames": field_names
            }
        }

        max_retries = 20

        for attempt in range(max_retries):
            response = requests.post(
                self.reports_url,
                json=body,
                headers=headers,
                timeout=300
            )

            if response.status_code == 200:
                return pd.read_csv(StringIO(response.text), sep='\t')

            elif response.status_code in [201, 202]:
                retry_in = int(response.headers.get("retryIn", 30))
                print(f"Отчёт формируется. Ожидание {retry_in} сек... "
                      f"(попытка {attempt + 1}/{max_retries})")
                time.sleep(retry_in)

            else:
                raise Exception(f"Ошибка отчёта: {response.status_code} - {response.text}")

        raise Exception("Не удалось получить отчёт")


# Использование
report_manager = ReportManager(client)

# Статистика по кампаниям за последнюю неделю
df = report_manager.get_report(
    report_type="CAMPAIGN_PERFORMANCE_REPORT",
    field_names=[
        "Date", "CampaignName", "Impressions",
        "Clicks", "Ctr", "Cost", "AvgCpc"
    ],
    date_range="LAST_7_DAYS"
)

print(df.head())
print(f"\nВсего кликов: {df['Clicks'].sum()}")
print(f"Всего потрачено: {df['Cost'].sum():.2f} ₽")
```

### 4. Массовое обновление ставок

```python
def optimize_bids_by_ctr(
    client: YandexDirectClient,
    campaign_id: int,
    min_ctr: float = 2.0,
    max_ctr: float = 10.0,
    min_bid: float = 10.0,
    max_bid: float = 100.0
):
    """
    Оптимизация ставок на основе CTR.

    Повышает ставки для фраз с высоким CTR,
    понижает для фраз с низким CTR.
    """
    # Получаем ключевые фразы со статистикой
    response = client.request("keywords", {
        "method": "get",
        "params": {
            "SelectionCriteria": {
                "CampaignIds": [campaign_id],
                "States": ["ON"]
            },
            "FieldNames": [
                "Id", "Keyword", "Bid", "StatisticsSearch"
            ]
        }
    })

    keywords = response.get("Keywords", [])
    bids_to_update = []

    for kw in keywords:
        stats = kw.get("StatisticsSearch", {})
        impressions = stats.get("Impressions", 0)
        clicks = stats.get("Clicks", 0)

        if impressions < 100:
            continue  # Недостаточно данных

        ctr = (clicks / impressions) * 100
        current_bid = kw.get("Bid", 0) / 1_000_000

        # Расчёт новой ставки на основе CTR
        if ctr >= max_ctr:
            new_bid = min(current_bid * 1.3, max_bid)
        elif ctr <= min_ctr:
            new_bid = max(current_bid * 0.7, min_bid)
        else:
            # Линейная интерполяция
            ratio = (ctr - min_ctr) / (max_ctr - min_ctr)
            new_bid = min_bid + ratio * (max_bid - min_bid)

        if abs(new_bid - current_bid) > 1:  # Изменение > 1 рубля
            bids_to_update.append({
                "KeywordId": kw["Id"],
                "Bid": int(new_bid * 1_000_000)
            })
            print(f"[{kw['Keyword'][:30]}] CTR={ctr:.2f}% | "
                  f"Ставка: {current_bid:.2f} → {new_bid:.2f} ₽")

    if bids_to_update:
        # Метод set бесплатный!
        client.request("bids", {
            "method": "set",
            "params": {
                "Bids": bids_to_update
            }
        })
        print(f"\nОбновлено ставок: {len(bids_to_update)}")

    return len(bids_to_update)


# Использование
updated = optimize_bids_by_ctr(client, campaign_id=123456)
```

### 5. Мониторинг баллов и автоматическая пауза

```python
class RateLimitedClient(YandexDirectClient):
    """Клиент с контролем расхода баллов."""

    def __init__(self, *args, units_threshold: int = 1000, **kwargs):
        super().__init__(*args, **kwargs)
        self.units_threshold = units_threshold
        self.requests_count = 0

    def request(self, *args, **kwargs):
        # Проверка остатка баллов
        if self.units_remaining > 0 and self.units_remaining < self.units_threshold:
            wait_minutes = 5
            print(f"Осталось мало баллов ({self.units_remaining}). "
                  f"Пауза {wait_minutes} минут...")
            time.sleep(wait_minutes * 60)

        result = super().request(*args, **kwargs)
        self.requests_count += 1

        # Логирование каждые 10 запросов
        if self.requests_count % 10 == 0:
            info = self.get_units_info()
            print(f"[Статистика] Запросов: {self.requests_count}, "
                  f"Баллов: {info['remaining']}/{info['daily_limit']} "
                  f"({info['usage_percent']}%)")

        return result


# Использование
client = RateLimitedClient(
    token="YOUR_TOKEN",
    units_threshold=500  # Пауза при остатке < 500 баллов
)
```

---

## Полный пример приложения

```python
#!/usr/bin/env python3
"""
Пример приложения для работы с Yandex Direct API.
"""

import os
import argparse
from yandex_direct_client import YandexDirectClient, ReportManager


def main():
    parser = argparse.ArgumentParser(description="Yandex Direct API Client")
    parser.add_argument("--token", default=os.environ.get("YANDEX_DIRECT_TOKEN"))
    parser.add_argument("--login", default=os.environ.get("YANDEX_DIRECT_LOGIN"))
    parser.add_argument("--sandbox", action="store_true")
    parser.add_argument("action", choices=["campaigns", "report", "info"])
    args = parser.parse_args()

    if not args.token:
        print("Ошибка: укажите токен через --token или YANDEX_DIRECT_TOKEN")
        return

    client = YandexDirectClient(
        token=args.token,
        login=args.login,
        use_sandbox=args.sandbox
    )

    if args.action == "campaigns":
        response = client.request("campaigns", {
            "method": "get",
            "params": {
                "SelectionCriteria": {},
                "FieldNames": ["Id", "Name", "Status", "State"]
            }
        })
        for c in response.get("Campaigns", []):
            print(f"[{c['Id']}] {c['Name']} - {c['State']}")

    elif args.action == "report":
        rm = ReportManager(client)
        df = rm.get_report(
            report_type="ACCOUNT_PERFORMANCE_REPORT",
            field_names=["Date", "Impressions", "Clicks", "Cost"],
            date_range="LAST_7_DAYS"
        )
        print(df)

    elif args.action == "info":
        response = client.request("clients", {
            "method": "get",
            "params": {
                "FieldNames": ["ClientId", "Login", "Currency"]
            }
        })
        for c in response.get("Clients", []):
            print(f"ID: {c['ClientId']}, Login: {c['Login']}, Currency: {c['Currency']}")

    # Вывод информации о баллах
    info = client.get_units_info()
    print(f"\nБаллы: {info['remaining']}/{info['daily_limit']} ({info['usage_percent']}%)")


if __name__ == "__main__":
    main()
```

---

## Переменные окружения

Для безопасного хранения токенов используйте переменные окружения:

```bash
export YANDEX_DIRECT_TOKEN="your_oauth_token_here"
export YANDEX_DIRECT_LOGIN="client_login"  # Для агентств
```

```python
import os

token = os.environ.get("YANDEX_DIRECT_TOKEN")
login = os.environ.get("YANDEX_DIRECT_LOGIN")

client = YandexDirectClient(token=token, login=login)
```

---

[← AdExtensions](../services/adextensions.md) | [Назад к оглавлению →](../README.md)

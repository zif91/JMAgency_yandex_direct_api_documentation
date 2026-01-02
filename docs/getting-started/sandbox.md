# Песочница (Sandbox)

[← Назад к оглавлению](../README.md)

## Обзор

Песочница — это тестовая среда API Яндекс Директа, полностью изолированная от реальных данных. Она предназначена для разработки и отладки приложений без риска повлиять на реальные рекламные кампании.

## Ключевые особенности

| Характеристика | Описание |
|----------------|----------|
| **Изоляция** | Полностью отделена от боевых данных |
| **Безопасность** | Изменения не влияют на реальные кампании |
| **Имитация** | Симулирует все состояния кампаний |
| **Бесплатность** | Не требует реальных средств на счету |

## URL-адреса Песочницы

```
WSDL:  https://api-sandbox.direct.yandex.com/v5/{service}?wsdl
SOAP:  https://api-sandbox.direct.yandex.com/v5/{service}
JSON:  https://api-sandbox.direct.yandex.com/json/v5/{service}
```

### Сравнение с Production

| Окружение | URL |
|-----------|-----|
| Production | `https://api.direct.yandex.com/json/v5/{service}` |
| Sandbox | `https://api-sandbox.direct.yandex.com/json/v5/{service}` |

## Возможности Песочницы

### Что можно делать:

- Вызывать все методы API
- Создавать тестовые кампании и объявления
- Проверять работу приложения с разными сценариями
- Получать симулированные статистические отчёты
- Тестировать обработку ошибок

### Чего нельзя делать:

- Просматривать данные через веб-интерфейс Директа
- Показывать объявления реальным пользователям
- Списывать реальные средства

## Симуляция состояний

Песочница симулирует все возможные состояния кампаний:

```
Создание → Модерация → Активность → Приостановка → Архивация
```

### Примеры симулируемых сценариев:

- Прохождение модерации
- Отклонение объявлений
- Недостаточность средств
- Превышение лимитов

## Работа со статистикой

Статистические отчёты в Песочнице содержат **симулированные данные**, структура которых идентична реальным отчётам.

### Пример запроса отчёта в Песочнице:

```bash
curl -X POST "https://api-sandbox.direct.yandex.com/json/v5/reports" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Accept-Language: ru" \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "ReportName": "Test Report",
      "ReportType": "CAMPAIGN_PERFORMANCE_REPORT",
      "DateRangeType": "LAST_7_DAYS",
      "Format": "TSV",
      "IncludeVAT": "NO",
      "SelectionCriteria": {},
      "FieldNames": ["CampaignId", "CampaignName", "Impressions", "Clicks"]
    }
  }'
```

## Ограничения Песочницы

### Технические ограничения

- Те же лимиты API, что и в Production
- Максимум одна кампания на отчёт в сервисе Reports
- Не более 5 одновременных соединений

### Срок хранения данных

- Данные хранятся **1 месяц** с момента последнего обращения
- После истечения срока данные автоматически удаляются

### Отсутствие веб-интерфейса

Песочница **не имеет веб-интерфейса** — доступ только через API. Для просмотра созданных объектов используйте метод `get` соответствующего сервиса.

## Активация Песочницы

### Шаг 1: Включение Песочницы

1. Войдите в [Яндекс Директ](https://direct.yandex.ru/)
2. Перейдите в **"Настройки"** → **"API"**
3. Найдите раздел **"Песочница"**
4. Нажмите **"Включить"**

### Шаг 2: Получение тестового токена

Используйте тот же OAuth-токен, что и для Production. Разница только в URL-адресе API.

## Пример использования

### Python-класс для работы с Песочницей:

```python
class YandexDirectClient:
    def __init__(self, token: str, use_sandbox: bool = False):
        self.token = token
        self.base_url = (
            "https://api-sandbox.direct.yandex.com/json/v5"
            if use_sandbox
            else "https://api.direct.yandex.com/json/v5"
        )

    def get_campaigns(self):
        """Получить список кампаний"""
        return self._request("campaigns", {
            "method": "get",
            "params": {
                "SelectionCriteria": {},
                "FieldNames": ["Id", "Name", "Status"]
            }
        })

    def _request(self, service: str, body: dict):
        import requests

        response = requests.post(
            f"{self.base_url}/{service}",
            json=body,
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept-Language": "ru",
                "Content-Type": "application/json"
            }
        )
        return response.json()


# Использование
client = YandexDirectClient(token="YOUR_TOKEN", use_sandbox=True)
campaigns = client.get_campaigns()
print(campaigns)
```

## Переход к Production

После успешного тестирования в Песочнице:

1. Убедитесь, что приложение корректно обрабатывает все сценарии
2. Проверьте обработку ошибок
3. Замените URL Песочницы на Production
4. Проведите финальное тестирование с реальными данными (в ограниченном объёме)

---

[← Аутентификация](./authentication.md) | [Формат запросов →](../concepts/request-format.md)

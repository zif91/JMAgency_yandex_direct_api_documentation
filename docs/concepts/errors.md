# Обработка ошибок

[← Назад к оглавлению](../README.md)

## Типы ошибок

API Яндекс Директа различает два типа ошибок:

1. **Ошибки выполнения запроса** — проблемы, препятствующие выполнению всего запроса
2. **Ошибки операций** — проблемы с отдельными объектами, не влияющие на остальные операции

## Ошибки выполнения запроса

### Структура ответа

```json
{
  "error": {
    "request_id": "1234567890123456789",
    "error_code": 53,
    "error_string": "Authorization error",
    "error_detail": "Invalid OAuth token"
  }
}
```

### Поля ответа

| Поле | Описание |
|------|----------|
| `request_id` | Уникальный идентификатор запроса (для поддержки) |
| `error_code` | Числовой код ошибки |
| `error_string` | Краткое описание ошибки |
| `error_detail` | Подробное описание |

## Ошибки операций

При ошибке операции над отдельным объектом остальные объекты обрабатываются нормально:

```json
{
  "result": {
    "AddResults": [
      {
        "Id": 123456
      },
      {
        "Errors": [
          {
            "Code": 8800,
            "Message": "Объект не найден",
            "Details": "Группа объявлений не существует"
          }
        ]
      },
      {
        "Id": 789012,
        "Warnings": [
          {
            "Code": 1000,
            "Message": "Предупреждение",
            "Details": "Объект создан с предупреждением"
          }
        ]
      }
    ]
  }
}
```

## HTTP-коды ответов

| Код | Значение | Описание | Действие |
|-----|----------|----------|----------|
| `200` | OK | Успешное выполнение | Обработать результат |
| `201` | Created | Отчёт в очереди | Повторить запрос позже |
| `202` | Accepted | Отчёт формируется | Повторить запрос позже |
| `400` | Bad Request | Неверный запрос | Исправить параметры |
| `401` | Unauthorized | Ошибка авторизации | Проверить/обновить токен |
| `403` | Forbidden | Доступ запрещён | Проверить права |
| `404` | Not Found | Сервис не найден | Проверить URL |
| `429` | Too Many Requests | Превышен лимит | Снизить частоту |
| `500` | Server Error | Ошибка сервера | Повторить позже |
| `502` | Bad Gateway | Ошибка шлюза | Повторить позже |
| `503` | Unavailable | Сервис недоступен | Повторить позже |

## Основные коды ошибок API

### Авторизация и доступ

| Код | Описание | Решение |
|-----|----------|---------|
| `52` | Токен отозван или истёк | Получить новый токен |
| `53` | Неверный токен | Проверить токен |
| `54` | Недостаточно прав | Проверить права доступа |
| `55` | Доступ запрещён | Проверить разрешения клиента |
| `56` | Требуется Client-Login | Добавить заголовок для агентства |

### Лимиты и ограничения

| Код | Описание | Решение |
|-----|----------|---------|
| `152` | Превышен лимит баллов | Подождать восстановления |
| `153` | Слишком много соединений | Уменьшить параллельность |
| `506` | Превышен лимит объектов | Уменьшить размер запроса |

### Валидация данных

| Код | Описание | Решение |
|-----|----------|---------|
| `8000` | Неверный формат запроса | Проверить JSON-структуру |
| `8002` | Обязательный параметр | Добавить недостающий параметр |
| `8800` | Объект не найден | Проверить ID объекта |
| `9000` | Внутренняя ошибка сервиса | Повторить позже |

### Модерация и статусы

| Код | Описание | Решение |
|-----|----------|---------|
| `4001` | Объект на модерации | Дождаться завершения |
| `4002` | Объект отклонён | Исправить и отправить заново |
| `4003` | Объект заархивирован | Разархивировать объект |

## Обработка ошибок (Python)

### Базовый обработчик

```python
class YandexDirectError(Exception):
    def __init__(self, code: int, message: str, details: str = "", request_id: str = ""):
        self.code = code
        self.message = message
        self.details = details
        self.request_id = request_id
        super().__init__(f"[{code}] {message}: {details}")


class YandexDirectClient:
    def request(self, service: str, body: dict) -> dict:
        response = requests.post(
            f"https://api.direct.yandex.com/json/v5/{service}",
            json=body,
            headers=self.headers
        )

        # Обработка HTTP-ошибок
        if response.status_code >= 400:
            self._handle_http_error(response)

        data = response.json()

        # Обработка ошибок API
        if "error" in data:
            error = data["error"]
            raise YandexDirectError(
                code=error["error_code"],
                message=error["error_string"],
                details=error.get("error_detail", ""),
                request_id=error.get("request_id", "")
            )

        return data["result"]

    def _handle_http_error(self, response):
        if response.status_code == 401:
            raise YandexDirectError(53, "Unauthorized", "Invalid or expired token")
        elif response.status_code == 429:
            raise YandexDirectError(152, "Too Many Requests", "Rate limit exceeded")
        elif response.status_code >= 500:
            raise YandexDirectError(9000, "Server Error", f"HTTP {response.status_code}")
        else:
            raise YandexDirectError(8000, "Request Error", f"HTTP {response.status_code}")
```

### Retry-логика

```python
import time
from functools import wraps

def retry_on_error(max_retries=3, retry_codes=(152, 9000, 502, 503)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)

                except YandexDirectError as e:
                    last_error = e

                    if e.code not in retry_codes:
                        raise

                    wait_time = 2 ** attempt * 10  # 10, 20, 40 секунд
                    print(f"Ошибка {e.code}. Повтор через {wait_time} сек...")
                    time.sleep(wait_time)

            raise last_error

        return wrapper
    return decorator


# Использование
class YandexDirectClient:
    @retry_on_error(max_retries=3)
    def get_campaigns(self):
        return self.request("campaigns", {
            "method": "get",
            "params": {"SelectionCriteria": {}, "FieldNames": ["Id", "Name"]}
        })
```

### Обработка частичных ошибок

```python
def process_batch_results(results: list, operation: str) -> tuple:
    """
    Разделяет результаты на успешные и ошибочные.

    Returns:
        (successful_ids, errors)
    """
    successful = []
    errors = []

    for idx, result in enumerate(results):
        if "Errors" in result:
            for error in result["Errors"]:
                errors.append({
                    "index": idx,
                    "code": error["Code"],
                    "message": error["Message"],
                    "details": error.get("Details", "")
                })
        else:
            successful.append(result.get("Id"))

        if "Warnings" in result:
            for warning in result["Warnings"]:
                print(f"Предупреждение [{warning['Code']}]: {warning['Message']}")

    return successful, errors


# Использование
response = client.request("campaigns", {
    "method": "add",
    "params": {"Campaigns": campaigns_data}
})

successful_ids, errors = process_batch_results(
    response.get("AddResults", []),
    "add"
)

print(f"Успешно создано: {len(successful_ids)} кампаний")
if errors:
    print(f"Ошибок: {len(errors)}")
    for error in errors:
        print(f"  Индекс {error['index']}: [{error['code']}] {error['message']}")
```

## Логирование ошибок

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("yandex_direct")

class YandexDirectClient:
    def request(self, service: str, body: dict) -> dict:
        try:
            response = requests.post(url, json=body, headers=self.headers)
            data = response.json()

            if "error" in data:
                error = data["error"]
                logger.error(
                    f"API Error | RequestId: {error.get('request_id')} | "
                    f"Code: {error['error_code']} | {error['error_string']} | "
                    f"Details: {error.get('error_detail')}"
                )
                raise YandexDirectError(...)

            logger.info(f"Request to {service} successful | Units: {response.headers.get('Units')}")
            return data["result"]

        except requests.RequestException as e:
            logger.exception(f"Network error during request to {service}")
            raise
```

## Рекомендации по обработке ошибок

1. **Всегда логируйте `request_id`** — это поможет службе поддержки найти проблему

2. **Разделяйте типы ошибок**:
   - Временные (сеть, лимиты) — повторять с задержкой
   - Постоянные (валидация, права) — не повторять, исправлять

3. **Используйте экспоненциальную задержку** для повторных попыток

4. **Обрабатывайте частичные успехи** — один объект с ошибкой не должен блокировать остальные

5. **Мониторьте ошибки** — частые ошибки могут указывать на проблемы в логике

---

[← Система баллов](./units.md) | [Сервис Campaigns →](../services/campaigns.md)

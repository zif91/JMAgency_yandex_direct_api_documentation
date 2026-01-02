# Формат ответов

[← Назад к оглавлению](../README.md)

## Обзор

API Яндекс Директа возвращает ответы в формате JSON. Структура ответа зависит от типа запроса и результата его выполнения.

## Успешный ответ

### Структура

```json
{
  "result": {
    // данные ответа
  }
}
```

### Пример ответа метода get

```json
{
  "result": {
    "Campaigns": [
      {
        "Id": 123456,
        "Name": "Моя кампания",
        "Status": "ACCEPTED",
        "State": "ON",
        "DailyBudget": {
          "Amount": 3000000000,
          "Mode": "STANDARD"
        }
      },
      {
        "Id": 789012,
        "Name": "Вторая кампания",
        "Status": "ACCEPTED",
        "State": "SUSPENDED"
      }
    ]
  }
}
```

### Пример ответа метода add

```json
{
  "result": {
    "AddResults": [
      {
        "Id": 123456
      },
      {
        "Id": 789012,
        "Warnings": [
          {
            "Code": 1000,
            "Message": "Элемент успешно добавлен с предупреждением",
            "Details": "Дополнительная информация"
          }
        ]
      }
    ]
  }
}
```

### Пример ответа метода update

```json
{
  "result": {
    "UpdateResults": [
      {
        "Id": 123456
      },
      {
        "Id": 789012,
        "Errors": [
          {
            "Code": 8800,
            "Message": "Объект не найден",
            "Details": "Кампания с указанным Id не существует"
          }
        ]
      }
    ]
  }
}
```

## HTTP-заголовки ответа

### Основные заголовки

| Заголовок | Описание | Пример |
|-----------|----------|--------|
| `RequestId` | Уникальный ID запроса | `1234567890123456789` |
| `Units` | Информация о баллах | `10/20828/64000` |
| `Content-Type` | Тип содержимого | `application/json; charset=utf-8` |

### Заголовок Units

Формат: `{потрачено}/{осталось}/{суточный_лимит}`

```
Units: 10/20828/64000
```

- `10` — потрачено на данный запрос
- `20828` — осталось баллов
- `64000` — суточный лимит

## Ответ с ошибкой

### Ошибка выполнения запроса

При ошибке выполнения всего запроса:

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

### Ошибка операции над объектом

При ошибке операции над отдельным объектом:

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
            "Details": "Кампания с указанным Id не существует"
          }
        ]
      }
    ]
  }
}
```

## HTTP-коды ответов

### Успешные коды

| Код | Значение | Описание |
|-----|----------|----------|
| `200` | OK | Запрос выполнен успешно |
| `201` | Created | Отчёт поставлен в очередь (Reports) |
| `202` | Accepted | Отчёт формируется (Reports) |

### Коды ошибок

| Код | Значение | Описание |
|-----|----------|----------|
| `400` | Bad Request | Неверный формат запроса |
| `401` | Unauthorized | Ошибка авторизации |
| `403` | Forbidden | Доступ запрещён |
| `404` | Not Found | Сервис не найден |
| `429` | Too Many Requests | Превышен лимит запросов |
| `500` | Internal Server Error | Внутренняя ошибка сервера |
| `502` | Bad Gateway | Ошибка шлюза |
| `503` | Service Unavailable | Сервис временно недоступен |

## Структура предупреждений и ошибок

### Warning (предупреждение)

```json
{
  "Code": 1000,
  "Message": "Краткое описание",
  "Details": "Подробное описание"
}
```

Предупреждение не прерывает операцию — объект создаётся/изменяется.

### Error (ошибка)

```json
{
  "Code": 8800,
  "Message": "Краткое описание",
  "Details": "Подробное описание"
}
```

Ошибка прерывает операцию — объект не создаётся/не изменяется.

## Пагинация в ответах

При наличии дополнительных данных ответ содержит `LimitedBy`:

```json
{
  "result": {
    "Campaigns": [...],
    "LimitedBy": 1000
  }
}
```

`LimitedBy` указывает на номер последнего возвращённого объекта. Для получения следующей порции данных используйте `Offset`.

## Денежные значения в ответах

По умолчанию денежные значения возвращаются в **микроединицах**.

### Получение значений в основной валюте

Добавьте заголовок:

```http
returnMoneyInMicros: false
```

### Пример различия

| Заголовок | Значение в ответе | Реальная сумма |
|-----------|-------------------|----------------|
| `returnMoneyInMicros: true` (по умолчанию) | `1000000000` | 1000 ₽ |
| `returnMoneyInMicros: false` | `1000.00` | 1000 ₽ |

## Язык сообщений

Язык сообщений об ошибках определяется заголовком `Accept-Language`:

| Значение | Язык |
|----------|------|
| `ru` | Русский |
| `en` | Английский |
| `tr` | Турецкий |

При отсутствии заголовка или неподдерживаемом языке — английский.

## Обработка ответов (Python)

```python
import requests

def make_request(service: str, body: dict) -> dict:
    url = f"https://api.direct.yandex.com/json/v5/{service}"
    headers = {
        "Authorization": "Bearer YOUR_TOKEN",
        "Accept-Language": "ru",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=body, headers=headers)

    # Проверка HTTP-статуса
    if response.status_code != 200:
        raise Exception(f"HTTP Error: {response.status_code}")

    data = response.json()

    # Проверка на ошибку API
    if "error" in data:
        error = data["error"]
        raise Exception(
            f"API Error {error['error_code']}: {error['error_string']} - {error['error_detail']}"
        )

    # Извлечение информации о баллах
    units = response.headers.get("Units", "")
    if units:
        spent, remaining, daily = units.split("/")
        print(f"Баллы: потрачено {spent}, осталось {remaining}/{daily}")

    return data["result"]


# Использование
result = make_request("campaigns", {
    "method": "get",
    "params": {
        "SelectionCriteria": {},
        "FieldNames": ["Id", "Name"]
    }
})

for campaign in result.get("Campaigns", []):
    print(f"ID: {campaign['Id']}, Name: {campaign['Name']}")
```

---

[← Формат запросов](./request-format.md) | [Система баллов →](./units.md)

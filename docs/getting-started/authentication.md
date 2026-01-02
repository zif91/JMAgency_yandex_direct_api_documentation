# Аутентификация OAuth 2.0

[← Назад к оглавлению](../README.md)

## Обзор

API Яндекс Директа использует протокол **OAuth 2.0** для авторизации. Авторизационный токен (OAuth-токен) — это специальный код, разрешающий доступ к данным конкретного пользователя.

## Способы получения токена

### 1. Ручное получение (отладочный токен)

Подходит для:
- Разработки и отладки
- Небольшого количества пользователей одного бизнеса
- Скриптов без взаимодействия с пользователем

#### Процесс получения:

1. Перейдите на страницу [получения токена](https://oauth.yandex.ru/authorize?response_type=token&client_id=YOUR_CLIENT_ID)
2. Авторизуйтесь под нужным аккаунтом
3. Подтвердите доступ приложения к данным
4. Скопируйте токен из URL после редиректа

#### Формат URL для получения токена:

```
https://oauth.yandex.ru/authorize?response_type=token&client_id={CLIENT_ID}
```

### 2. Автоматическое получение

Подходит для:
- Приложений с множеством пользователей
- Сервисов с разграничением прав доступа

#### Процесс получения:

1. Приложение перенаправляет пользователя на страницу авторизации Яндекса
2. Пользователь авторизуется и подтверждает разрешения
3. Яндекс OAuth перенаправляет обратно с кодом авторизации
4. Приложение обменивает код на токен

#### Пример URL авторизации:

```
https://oauth.yandex.ru/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}
```

#### Обмен кода на токен:

```bash
curl -X POST "https://oauth.yandex.ru/token" \
  -d "grant_type=authorization_code" \
  -d "code={AUTHORIZATION_CODE}" \
  -d "client_id={CLIENT_ID}" \
  -d "client_secret={CLIENT_SECRET}"
```

## HTTP-заголовки запросов

### Обязательные заголовки

| Заголовок | Описание | Пример |
|-----------|----------|--------|
| `Authorization` | OAuth-токен пользователя | `Bearer 0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f0f` |
| `Content-Type` | Тип содержимого запроса | `application/json; charset=utf-8` |

### Опциональные заголовки

| Заголовок | Описание | Значения |
|-----------|----------|----------|
| `Accept-Language` | Язык сообщений об ошибках | `ru`, `en`, `tr` |
| `Client-Login` | Логин рекламодателя (для агентств) | Логин клиента |
| `Use-Operator-Units` | Расходовать баллы агентства | `true` |
| `Accept-Encoding` | Сжатие ответа | `gzip` |
| `Payment-Token` | Финансовый токен | Токен для финансовых операций |

## Примеры использования

### Базовый запрос

```bash
curl -X POST "https://api.direct.yandex.com/json/v5/campaigns" \
  -H "Authorization: Bearer YOUR_OAUTH_TOKEN" \
  -H "Accept-Language: ru" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "method": "get",
    "params": {
      "SelectionCriteria": {},
      "FieldNames": ["Id", "Name"]
    }
  }'
```

### Запрос от имени агентства

```bash
curl -X POST "https://api.direct.yandex.com/json/v5/campaigns" \
  -H "Authorization: Bearer AGENCY_OAUTH_TOKEN" \
  -H "Client-Login: client-login" \
  -H "Accept-Language: ru" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "method": "get",
    "params": {
      "SelectionCriteria": {},
      "FieldNames": ["Id", "Name"]
    }
  }'
```

### Запрос с использованием баллов агентства

```bash
curl -X POST "https://api.direct.yandex.com/json/v5/campaigns" \
  -H "Authorization: Bearer AGENCY_OAUTH_TOKEN" \
  -H "Client-Login: client-login" \
  -H "Use-Operator-Units: true" \
  -H "Accept-Language: ru" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{...}'
```

## Обработка ошибок токена

### Коды ошибок

| Код | Описание | Решение |
|-----|----------|---------|
| `1002` | Неверный токен | Проверить токен или получить новый |
| `53` | Токен отозван | Получить новый токен |
| `52` | Истёк срок действия | Обновить токен |

### Пример ошибки

```json
{
  "error": {
    "request_id": "1234567890",
    "error_code": 1002,
    "error_string": "Invalid OAuth token",
    "error_detail": "Token is invalid or expired"
  }
}
```

## Безопасность токенов

### Рекомендации

1. **Никогда не передавайте токены** в URL-параметрах
2. **Храните токены** в защищённом хранилище (env-переменные, vault)
3. **Не коммитьте токены** в репозитории
4. **Используйте отдельные токены** для разных окружений
5. **Регулярно ротируйте** токены

### Пример безопасного хранения (Python)

```python
import os

# Загрузка токена из переменной окружения
OAUTH_TOKEN = os.environ.get('YANDEX_DIRECT_TOKEN')

if not OAUTH_TOKEN:
    raise ValueError("YANDEX_DIRECT_TOKEN environment variable is not set")
```

## Время жизни токена

- Токены Яндекс OAuth имеют **длительный срок действия**
- Токен может быть отозван пользователем в настройках аккаунта
- Рекомендуется реализовать механизм обновления токена при ошибке авторизации

---

[← Регистрация](./registration.md) | [Песочница →](./sandbox.md)

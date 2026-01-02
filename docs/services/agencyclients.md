# Сервис AgencyClients

[← Назад к оглавлению](../README.md)

## Обзор

Сервис **AgencyClients** предназначен для управления клиентами рекламного агентства.

> **Важно:** В заголовке `Authorization` указывайте токен представителя агентства. Заголовок `Client-Login` НЕ указывается.

## Endpoints

| Формат | URL |
|--------|-----|
| JSON | `https://api.direct.yandex.com/json/v5/agencyclients` |
| JSON (v501) | `https://api.direct.yandex.com/json/v501/agencyclients` |
| SOAP | `https://api.direct.yandex.com/v5/agencyclients` |

## Методы

| Метод | Описание |
|-------|----------|
| [add](#add) | Создание клиента агентства |
| [get](#get) | Получение данных о клиентах |
| [update](#update) | Изменение данных клиента |

---

## add

Создание нового клиента агентства.

### Запрос

```json
{
  "method": "add",
  "params": {
    "AgencyClients": [
      {
        "Login": "new-client-login",
        "FirstName": "Иван",
        "LastName": "Иванов",
        "Currency": "RUB",
        "Grants": [
          {
            "Privilege": "EDIT_CAMPAIGNS",
            "Value": "YES"
          }
        ],
        "Notification": {
          "Lang": "RU",
          "Email": "client@example.com"
        },
        "Settings": [
          {
            "Option": "DISPLAY_STORE_RATING",
            "Value": "YES"
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
| `Login` | string | Да | Логин клиента |
| `FirstName` | string | Да | Имя |
| `LastName` | string | Да | Фамилия |
| `Currency` | enum | Да | Валюта |
| `Grants` | array | Нет | Права доступа |
| `Notification` | object | Нет | Настройки уведомлений |
| `Settings` | array | Нет | Настройки |

### Права доступа (Grants)

| Privilege | Описание |
|-----------|----------|
| `EDIT_CAMPAIGNS` | Редактирование кампаний |
| `IMPORT_XLS` | Импорт из Excel |
| `TRANSFER_MONEY` | Перевод средств |

### Ответ

```json
{
  "result": {
    "AddResults": [
      {
        "ClientId": 87654321
      }
    ]
  }
}
```

---

## get

Получение информации о клиентах агентства.

### Запрос

```json
{
  "method": "get",
  "params": {
    "SelectionCriteria": {
      "Logins": ["client-login-1", "client-login-2"],
      "Archived": "NO"
    },
    "FieldNames": [
      "AccountQuality",
      "Archived",
      "ClientId",
      "ClientInfo",
      "CountryId",
      "CreatedAt",
      "Currency",
      "Grants",
      "Login",
      "OverdraftSumAvailable",
      "Representatives",
      "Restrictions",
      "Settings",
      "Type",
      "VatRate"
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
| `Logins` | array[string] | Логины клиентов |
| `Archived` | enum | `YES`, `NO` — фильтр по архивации |

### Ответ

```json
{
  "result": {
    "Clients": [
      {
        "ClientId": 87654321,
        "Login": "client-login-1",
        "Currency": "RUB",
        "Type": "AGENCY_CLIENT",
        "Archived": "NO",
        "Grants": [
          {
            "Privilege": "EDIT_CAMPAIGNS",
            "Value": "YES",
            "Agency": "my-agency"
          }
        ]
      }
    ]
  }
}
```

---

## update

Изменение данных клиента агентства.

### Запрос

```json
{
  "method": "update",
  "params": {
    "AgencyClients": [
      {
        "ClientId": 87654321,
        "Grants": [
          {
            "Privilege": "EDIT_CAMPAIGNS",
            "Value": "NO"
          }
        ]
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
        "ClientId": 87654321
      }
    ]
  }
}
```

---

## Пример использования (Python)

```python
class AgencyManager:
    def __init__(self, client):
        self.client = client

    def get_all_clients(self, include_archived: bool = False):
        """Получение всех клиентов агентства."""
        response = self.client.request("agencyclients", {
            "method": "get",
            "params": {
                "SelectionCriteria": {
                    "Archived": "YES" if include_archived else "NO"
                },
                "FieldNames": [
                    "ClientId", "Login", "Currency",
                    "Archived", "Grants", "AccountQuality"
                ]
            }
        })

        return response.get("Clients", [])

    def create_client(self, login: str, first_name: str, last_name: str,
                      currency: str = "RUB", can_edit: bool = True):
        """Создание нового клиента."""
        grants = []
        if can_edit:
            grants.append({
                "Privilege": "EDIT_CAMPAIGNS",
                "Value": "YES"
            })

        response = self.client.request("agencyclients", {
            "method": "add",
            "params": {
                "AgencyClients": [{
                    "Login": login,
                    "FirstName": first_name,
                    "LastName": last_name,
                    "Currency": currency,
                    "Grants": grants
                }]
            }
        })

        result = response.get("AddResults", [{}])[0]
        if "Errors" in result:
            raise Exception(result["Errors"])

        return result["ClientId"]

    def update_client_grants(self, client_id: int, can_edit: bool):
        """Обновление прав клиента."""
        response = self.client.request("agencyclients", {
            "method": "update",
            "params": {
                "AgencyClients": [{
                    "ClientId": client_id,
                    "Grants": [{
                        "Privilege": "EDIT_CAMPAIGNS",
                        "Value": "YES" if can_edit else "NO"
                    }]
                }]
            }
        })

        return response.get("UpdateResults", [])
```

---

[← Clients](./clients.md) | [Dictionaries →](./dictionaries.md)

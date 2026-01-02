# Сервис Clients

[← Назад к оглавлению](../README.md)

## Обзор

Сервис **Clients** предназначен для управления параметрами рекламодателя и настройками пользователя.

## Endpoints

| Формат | URL |
|--------|-----|
| JSON | `https://api.direct.yandex.com/json/v5/clients` |
| JSON (v501) | `https://api.direct.yandex.com/json/v501/clients` |
| SOAP | `https://api.direct.yandex.com/v5/clients` |

## Методы

| Метод | Описание |
|-------|----------|
| [get](#get) | Получение данных о клиенте |
| [update](#update) | Изменение настроек |

---

## get

Получение информации о рекламодателе.

### Запрос

```json
{
  "method": "get",
  "params": {
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
      "Notification",
      "OverdraftSumAvailable",
      "Phone",
      "Representatives",
      "Restrictions",
      "Settings",
      "Type",
      "VatRate"
    ]
  }
}
```

### FieldNames

| Поле | Описание |
|------|----------|
| `AccountQuality` | Показатель качества аккаунта |
| `Archived` | Флаг архивации |
| `ClientId` | ID клиента |
| `ClientInfo` | Информация о клиенте |
| `CountryId` | ID страны |
| `CreatedAt` | Дата создания |
| `Currency` | Валюта |
| `Grants` | Права доступа |
| `Login` | Логин |
| `Notification` | Настройки уведомлений |
| `OverdraftSumAvailable` | Доступный овердрафт |
| `Phone` | Телефон |
| `Representatives` | Представители |
| `Restrictions` | Ограничения |
| `Settings` | Настройки |
| `Type` | Тип клиента |
| `VatRate` | Ставка НДС |

### Ответ

```json
{
  "result": {
    "Clients": [
      {
        "ClientId": 12345678,
        "Login": "my-login",
        "Currency": "RUB",
        "Type": "CLIENT",
        "CountryId": 225,
        "VatRate": 20.0,
        "CreatedAt": "2020-01-15",
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

---

## update

Изменение настроек клиента.

### Запрос

```json
{
  "method": "update",
  "params": {
    "Clients": [
      {
        "ClientInfo": "Новая информация о клиенте",
        "Phone": "+7 (999) 123-45-67",
        "Settings": [
          {
            "Option": "DISPLAY_STORE_RATING",
            "Value": "YES"
          },
          {
            "Option": "CORRECT_TYPOS_AUTOMATICALLY",
            "Value": "NO"
          }
        ],
        "Notification": {
          "Lang": "RU",
          "Email": "notify@example.com",
          "EmailSubscriptions": [
            {
              "Option": "RECEIVE_RECOMMENDATIONS",
              "Value": "NO"
            }
          ]
        }
      }
    ]
  }
}
```

### Настройки (Settings)

| Option | Описание |
|--------|----------|
| `DISPLAY_STORE_RATING` | Показывать рейтинг магазина |
| `CORRECT_TYPOS_AUTOMATICALLY` | Автоматическое исправление опечаток |
| `SHARED_ACCOUNT_ENABLED` | Общий счёт |

### Ответ

```json
{
  "result": {
    "UpdateResults": [
      {
        "ClientId": 12345678
      }
    ]
  }
}
```

---

## Пример использования (Python)

```python
def get_client_info(client):
    """Получение информации о текущем клиенте."""
    response = client.request("clients", {
        "method": "get",
        "params": {
            "FieldNames": [
                "ClientId", "Login", "Currency",
                "Type", "VatRate", "Settings"
            ]
        }
    })

    clients = response.get("Clients", [])
    if clients:
        info = clients[0]
        print(f"ID: {info['ClientId']}")
        print(f"Login: {info['Login']}")
        print(f"Currency: {info['Currency']}")
        print(f"VAT Rate: {info['VatRate']}%")
        return info

    return None


def update_client_notification(client, email: str, lang: str = "RU"):
    """Обновление настроек уведомлений."""
    response = client.request("clients", {
        "method": "update",
        "params": {
            "Clients": [{
                "Notification": {
                    "Lang": lang,
                    "Email": email
                }
            }]
        }
    })

    return response.get("UpdateResults", [])
```

---

[← Reports](./reports.md) | [AgencyClients →](./agencyclients.md)

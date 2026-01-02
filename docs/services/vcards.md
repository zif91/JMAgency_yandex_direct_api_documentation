# Сервис VCards

[← Назад к оглавлению](../README.md)

## Обзор

Сервис **VCards** предназначен для управления виртуальными визитками, которые отображаются в объявлениях.

## Endpoints

| Формат | URL |
|--------|-----|
| JSON | `https://api.direct.yandex.com/json/v5/vcards` |
| JSON (v501) | `https://api.direct.yandex.com/json/v501/vcards` |
| SOAP | `https://api.direct.yandex.com/v5/vcards` |

## Методы

| Метод | Описание |
|-------|----------|
| [add](#add) | Создание визиток |
| [get](#get) | Получение данных о визитках |
| [delete](#delete) | Удаление визиток |

---

## add

Создание виртуальной визитки.

### Запрос

```json
{
  "method": "add",
  "params": {
    "VCards": [
      {
        "CampaignId": 123456,
        "Country": "Россия",
        "City": "Москва",
        "Street": "ул. Примерная",
        "House": "10",
        "Building": "1",
        "Apartment": "15",
        "CompanyName": "ООО Пример",
        "Phone": {
          "CountryCode": "+7",
          "CityCode": "495",
          "PhoneNumber": "123-45-67",
          "Extension": "100"
        },
        "WorkTime": "0;6;09;00;18;00",
        "ContactEmail": "info@example.com",
        "Ogrn": "1234567890123",
        "ExtraMessage": "Работаем без выходных",
        "MetroStationId": 20490,
        "PointOnMap": {
          "X": 37.617644,
          "Y": 55.755819,
          "X1": 37.610,
          "Y1": 55.750,
          "X2": 37.625,
          "Y2": 55.760
        }
      }
    ]
  }
}
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `CampaignId` | long | Да | ID кампании |
| `Country` | string | Да | Страна |
| `City` | string | Да | Город |
| `Street` | string | Нет | Улица |
| `House` | string | Нет | Дом |
| `Building` | string | Нет | Строение/корпус |
| `Apartment` | string | Нет | Квартира/офис |
| `CompanyName` | string | Да | Название компании |
| `Phone` | object | Да | Телефон |
| `WorkTime` | string | Нет | Время работы |
| `ContactEmail` | string | Нет | Email |
| `Ogrn` | string | Нет | ОГРН |
| `ExtraMessage` | string | Нет | Дополнительная информация |
| `MetroStationId` | long | Нет | ID станции метро |
| `PointOnMap` | object | Нет | Координаты на карте |

### WorkTime формат

Формат: `{день_начала};{день_конца};{час_начала};{мин_начала};{час_конца};{мин_конца}`

- Дни: 0 (понедельник) — 6 (воскресенье)
- Пример: `0;4;09;00;18;00` — Пн-Пт с 09:00 до 18:00

### Phone

| Параметр | Описание |
|----------|----------|
| `CountryCode` | Код страны (+7) |
| `CityCode` | Код города (495) |
| `PhoneNumber` | Номер телефона |
| `Extension` | Добавочный номер |

### Ответ

```json
{
  "result": {
    "AddResults": [
      {
        "Id": 888999000
      }
    ]
  }
}
```

---

## get

Получение информации о визитках.

### Запрос

```json
{
  "method": "get",
  "params": {
    "SelectionCriteria": {
      "Ids": [888999000],
      "CampaignIds": [123456]
    },
    "FieldNames": [
      "Id",
      "CampaignId",
      "Country",
      "City",
      "Street",
      "House",
      "CompanyName",
      "Phone",
      "WorkTime",
      "ContactEmail"
    ],
    "Page": {
      "Limit": 10000,
      "Offset": 0
    }
  }
}
```

### Ответ

```json
{
  "result": {
    "VCards": [
      {
        "Id": 888999000,
        "CampaignId": 123456,
        "Country": "Россия",
        "City": "Москва",
        "Street": "ул. Примерная",
        "House": "10",
        "CompanyName": "ООО Пример",
        "Phone": {
          "CountryCode": "+7",
          "CityCode": "495",
          "PhoneNumber": "123-45-67"
        },
        "WorkTime": "0;6;09;00;18;00"
      }
    ]
  }
}
```

---

## delete

Удаление визиток.

```json
{
  "method": "delete",
  "params": {
    "SelectionCriteria": {
      "Ids": [888999000]
    }
  }
}
```

---

## Пример использования (Python)

```python
def create_vcard(client, campaign_id: int, company_name: str,
                 city: str, phone: str, address: dict = None):
    """Создание визитки."""

    # Парсинг телефона
    phone_parts = phone.replace("-", "").replace(" ", "")
    phone_data = {
        "CountryCode": "+7",
        "CityCode": phone_parts[1:4],
        "PhoneNumber": f"{phone_parts[4:7]}-{phone_parts[7:9]}-{phone_parts[9:11]}"
    }

    vcard = {
        "CampaignId": campaign_id,
        "Country": "Россия",
        "City": city,
        "CompanyName": company_name,
        "Phone": phone_data
    }

    if address:
        vcard.update({
            "Street": address.get("street"),
            "House": address.get("house"),
            "Building": address.get("building"),
            "Apartment": address.get("apartment")
        })

    response = client.request("vcards", {
        "method": "add",
        "params": {
            "VCards": [vcard]
        }
    })

    result = response.get("AddResults", [{}])[0]
    return result.get("Id")


# Использование
vcard_id = create_vcard(
    client,
    campaign_id=123456,
    company_name="ООО Пример",
    city="Москва",
    phone="+7 495 123-45-67",
    address={
        "street": "ул. Ленина",
        "house": "1",
        "apartment": "100"
    }
)
```

---

[← Sitelinks](./sitelinks.md) | [AdImages →](./adimages.md)

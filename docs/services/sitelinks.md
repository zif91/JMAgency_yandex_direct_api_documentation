# Сервис Sitelinks

[← Назад к оглавлению](../README.md)

## Обзор

Сервис **Sitelinks** предназначен для управления наборами быстрых ссылок.

## Endpoints

| Формат | URL |
|--------|-----|
| JSON | `https://api.direct.yandex.com/json/v5/sitelinks` |
| JSON (v501) | `https://api.direct.yandex.com/json/v501/sitelinks` |
| SOAP | `https://api.direct.yandex.com/v5/sitelinks` |

## Методы

| Метод | Описание |
|-------|----------|
| [add](#add) | Создание наборов быстрых ссылок |
| [get](#get) | Получение данных о наборах |
| [delete](#delete) | Удаление наборов |

---

## add

Создание набора быстрых ссылок.

### Запрос

```json
{
  "method": "add",
  "params": {
    "SitelinksSets": [
      {
        "Sitelinks": [
          {
            "Title": "Каталог",
            "Href": "https://example.com/catalog",
            "Description": "Полный каталог товаров"
          },
          {
            "Title": "Акции",
            "Href": "https://example.com/sales",
            "Description": "Скидки до 50%"
          },
          {
            "Title": "Доставка",
            "Href": "https://example.com/delivery",
            "Description": "Бесплатная доставка"
          },
          {
            "Title": "Контакты",
            "Href": "https://example.com/contacts",
            "Description": "Свяжитесь с нами"
          }
        ]
      }
    ]
  }
}
```

### Параметры Sitelink

| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `Title` | string | Да | Текст ссылки (макс. 30 символов) |
| `Href` | string | Да | URL |
| `Description` | string | Нет | Описание (макс. 60 символов) |
| `TurboPageId` | long | Нет | ID турбо-страницы |

### Ограничения

- Минимум **2** ссылки в наборе
- Максимум **8** ссылок в наборе

### Ответ

```json
{
  "result": {
    "AddResults": [
      {
        "Id": 555666777
      }
    ]
  }
}
```

---

## get

Получение информации о наборах быстрых ссылок.

### Запрос

```json
{
  "method": "get",
  "params": {
    "SelectionCriteria": {
      "Ids": [555666777, 555666778]
    },
    "FieldNames": [
      "Id",
      "Sitelinks"
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
    "SitelinksSets": [
      {
        "Id": 555666777,
        "Sitelinks": [
          {
            "Title": "Каталог",
            "Href": "https://example.com/catalog",
            "Description": "Полный каталог товаров"
          },
          {
            "Title": "Акции",
            "Href": "https://example.com/sales",
            "Description": "Скидки до 50%"
          }
        ]
      }
    ]
  }
}
```

---

## delete

Удаление наборов быстрых ссылок.

```json
{
  "method": "delete",
  "params": {
    "SelectionCriteria": {
      "Ids": [555666777]
    }
  }
}
```

---

## Пример использования (Python)

```python
def create_sitelinks_set(client, sitelinks: list):
    """
    Создание набора быстрых ссылок.

    Args:
        sitelinks: [{"title": "...", "href": "...", "description": "..."}, ...]
    """
    formatted = [
        {
            "Title": s["title"][:30],
            "Href": s["href"],
            "Description": s.get("description", "")[:60]
        }
        for s in sitelinks
    ]

    response = client.request("sitelinks", {
        "method": "add",
        "params": {
            "SitelinksSets": [{
                "Sitelinks": formatted
            }]
        }
    })

    result = response.get("AddResults", [{}])[0]
    return result.get("Id")


# Использование
sitelinks = [
    {"title": "Каталог", "href": "https://example.com/catalog", "description": "Все товары"},
    {"title": "Акции", "href": "https://example.com/sales", "description": "Скидки"},
    {"title": "Доставка", "href": "https://example.com/delivery"},
    {"title": "Контакты", "href": "https://example.com/contacts"}
]

sitelinks_id = create_sitelinks_set(client, sitelinks)
print(f"Создан набор ID: {sitelinks_id}")
```

---

[← RetargetingLists](./retargetinglists.md) | [VCards →](./vcards.md)

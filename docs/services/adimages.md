# Сервис AdImages

[← Назад к оглавлению](../README.md)

## Обзор

Сервис **AdImages** предназначен для управления изображениями, используемыми в объявлениях.

## Endpoints

| Формат | URL |
|--------|-----|
| JSON | `https://api.direct.yandex.com/json/v5/adimages` |
| JSON (v501) | `https://api.direct.yandex.com/json/v501/adimages` |
| SOAP | `https://api.direct.yandex.com/v5/adimages` |

## Методы

| Метод | Описание |
|-------|----------|
| [add](#add) | Загрузка изображений |
| [get](#get) | Получение данных об изображениях |
| [delete](#delete) | Удаление изображений |

---

## add

Загрузка изображения. Можно загрузить по URL или в формате base64.

### Загрузка по URL

```json
{
  "method": "add",
  "params": {
    "AdImages": [
      {
        "ImageData": {
          "Url": "https://example.com/images/banner.jpg"
        },
        "Name": "Баннер для кампании"
      }
    ]
  }
}
```

### Загрузка в base64

```json
{
  "method": "add",
  "params": {
    "AdImages": [
      {
        "ImageData": {
          "Binary": "/9j/4AAQSkZJRgABAQEASABIAAD..."
        },
        "Name": "Баннер из файла"
      }
    ]
  }
}
```

### Параметры

| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `Name` | string | Нет | Название изображения |
| `ImageData.Url` | string | Да* | URL изображения |
| `ImageData.Binary` | string | Да* | Изображение в base64 |

> *Необходимо указать либо `Url`, либо `Binary`.

### Требования к изображениям

| Параметр | Значение |
|----------|----------|
| Форматы | JPEG, PNG, GIF |
| Макс. размер файла | 10 МБ |
| Мин. размер | 450x450 px |
| Макс. размер | 5000x5000 px |

### Ответ

```json
{
  "result": {
    "AddResults": [
      {
        "AdImageHash": "a1b2c3d4e5f6g7h8i9j0"
      }
    ]
  }
}
```

---

## get

Получение информации об изображениях.

### Запрос

```json
{
  "method": "get",
  "params": {
    "SelectionCriteria": {
      "AdImageHashes": ["a1b2c3d4e5f6g7h8i9j0"],
      "Associated": "YES"
    },
    "FieldNames": [
      "AdImageHash",
      "Name",
      "Type",
      "Subtype",
      "OriginalUrl",
      "PreviewUrl",
      "Associated"
    ],
    "Page": {
      "Limit": 10000,
      "Offset": 0
    }
  }
}
```

### SelectionCriteria

| Параметр | Описание |
|----------|----------|
| `AdImageHashes` | Хеши изображений |
| `Associated` | `YES`/`NO` — привязаны к объявлениям |

### Ответ

```json
{
  "result": {
    "AdImages": [
      {
        "AdImageHash": "a1b2c3d4e5f6g7h8i9j0",
        "Name": "Баннер для кампании",
        "Type": "REGULAR",
        "OriginalUrl": "https://avatars.mds.yandex.net/...",
        "PreviewUrl": "https://avatars.mds.yandex.net/.../preview",
        "Associated": "YES"
      }
    ]
  }
}
```

---

## delete

Удаление изображений.

```json
{
  "method": "delete",
  "params": {
    "SelectionCriteria": {
      "AdImageHashes": ["a1b2c3d4e5f6g7h8i9j0"]
    }
  }
}
```

---

## Пример использования (Python)

```python
import base64
import requests


def upload_image_from_url(client, image_url: str, name: str = None):
    """Загрузка изображения по URL."""
    response = client.request("adimages", {
        "method": "add",
        "params": {
            "AdImages": [{
                "ImageData": {"Url": image_url},
                "Name": name or "Uploaded image"
            }]
        }
    })

    result = response.get("AddResults", [{}])[0]
    if "Errors" in result:
        raise Exception(result["Errors"])

    return result.get("AdImageHash")


def upload_image_from_file(client, file_path: str, name: str = None):
    """Загрузка изображения из файла."""
    with open(file_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    response = client.request("adimages", {
        "method": "add",
        "params": {
            "AdImages": [{
                "ImageData": {"Binary": image_data},
                "Name": name or file_path.split("/")[-1]
            }]
        }
    })

    result = response.get("AddResults", [{}])[0]
    if "Errors" in result:
        raise Exception(result["Errors"])

    return result.get("AdImageHash")


def get_all_images(client, associated_only: bool = True):
    """Получение всех изображений."""
    params = {
        "SelectionCriteria": {},
        "FieldNames": ["AdImageHash", "Name", "OriginalUrl", "Associated"]
    }

    if associated_only:
        params["SelectionCriteria"]["Associated"] = "YES"

    response = client.request("adimages", {
        "method": "get",
        "params": params
    })

    return response.get("AdImages", [])


# Использование
image_hash = upload_image_from_url(
    client,
    "https://example.com/banner.jpg",
    "Главный баннер"
)
print(f"Загружено изображение: {image_hash}")
```

---

[← VCards](./vcards.md) | [AdExtensions →](./adextensions.md)

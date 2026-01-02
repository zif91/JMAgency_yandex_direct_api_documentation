# Сервис Bids

[← Назад к оглавлению](../README.md)

## Обзор

Сервис **Bids** предназначен для управления ставками на ключевые фразы и автотаргетинги. Позволяет устанавливать ставки и получать данные о ценах позиций.

## Endpoints

| Формат | URL |
|--------|-----|
| JSON | `https://api.direct.yandex.com/json/v5/bids` |
| JSON (v501) | `https://api.direct.yandex.com/json/v501/bids` |
| SOAP | `https://api.direct.yandex.com/v5/bids` |
| WSDL | `https://api.direct.yandex.com/v5/bids?wsdl` |

## Методы

| Метод | Описание | Стоимость |
|-------|----------|-----------|
| [get](#get) | Получение данных о ставках и ценах | 15 + 3 за 2000 фраз |
| [set](#set) | Установка ставок | **0 (бесплатно!)** |
| [setAuto](#setauto) | Включение автоматического управления | 15 + 1 за объект |

> **Важно:** Метод `set` не расходует баллы API!

---

## get

Получение информации о ставках, ценах позиций и охвате аудитории.

### Запрос

```json
{
  "method": "get",
  "params": {
    "SelectionCriteria": {
      "KeywordIds": [444555666, 444555667],
      "AdGroupIds": [789012],
      "CampaignIds": [123456],
      "ServingStatuses": ["ELIGIBLE"]
    },
    "FieldNames": [
      "KeywordId",
      "AdGroupId",
      "CampaignId",
      "Bid",
      "ContextBid",
      "StrategyPriority",
      "ServingStatus",
      "AuctionBids",
      "CompetitorsBids"
    ],
    "Page": {
      "Limit": 10000,
      "Offset": 0
    }
  }
}
```

### SelectionCriteria

| Параметр | Тип | Описание |
|----------|-----|----------|
| `KeywordIds` | array[long] | ID фраз (макс. 10000) |
| `AdGroupIds` | array[long] | ID групп (макс. 1000) |
| `CampaignIds` | array[long] | ID кампаний (макс. 10) |
| `ServingStatuses` | array[enum] | Статусы показов |

### FieldNames

| Поле | Описание |
|------|----------|
| `KeywordId` | ID ключевой фразы |
| `AdGroupId` | ID группы |
| `CampaignId` | ID кампании |
| `Bid` | Текущая ставка на поиске |
| `ContextBid` | Текущая ставка в сетях |
| `StrategyPriority` | Приоритет стратегии |
| `ServingStatus` | Статус показов |
| `AuctionBids` | Ставки для позиций на аукционе |
| `CompetitorsBids` | Ставки конкурентов |
| `Search` | Данные о поисковых позициях |
| `Network` | Данные о позициях в сетях |

### AuctionBids (ставки для позиций)

```json
{
  "AuctionBids": {
    "Position1": {
      "Bid": 5000000,
      "Price": 4500000,
      "TrafficVolume": 100
    },
    "Position2": {
      "Bid": 3500000,
      "Price": 3200000,
      "TrafficVolume": 85
    }
  }
}
```

| Позиция | Описание |
|---------|----------|
| `Position1` | Первое спецразмещение |
| `Position2` | Второе спецразмещение |
| `Position3` | Третье спецразмещение |
| `Position4` | Четвёртое спецразмещение |

### Ответ

```json
{
  "result": {
    "Bids": [
      {
        "KeywordId": 444555666,
        "AdGroupId": 789012,
        "CampaignId": 123456,
        "Bid": 2000000,
        "ContextBid": 1000000,
        "StrategyPriority": "NORMAL",
        "ServingStatus": "ELIGIBLE",
        "AuctionBids": {
          "Position1": {
            "Bid": 5500000,
            "Price": 5000000,
            "TrafficVolume": 100
          }
        }
      }
    ]
  }
}
```

---

## set

Установка ставок на ключевые фразы. **Бесплатный метод!**

### Запрос

```json
{
  "method": "set",
  "params": {
    "Bids": [
      {
        "KeywordId": 444555666,
        "Bid": 2500000,
        "ContextBid": 1200000
      },
      {
        "KeywordId": 444555667,
        "Bid": 3000000
      }
    ]
  }
}
```

### Параметры установки ставки

| Параметр | Тип | Описание |
|----------|-----|----------|
| `KeywordId` | long | ID ключевой фразы (обязательный) |
| `Bid` | long | Ставка на поиске (микроединицы) |
| `ContextBid` | long | Ставка в сетях (микроединицы) |
| `StrategyPriority` | enum | Приоритет: `LOW`, `NORMAL`, `HIGH` |

### Ответ

```json
{
  "result": {
    "SetResults": [
      {
        "KeywordId": 444555666
      },
      {
        "KeywordId": 444555667
      }
    ]
  }
}
```

---

## setAuto

Включение автоматического управления ставками для фраз.

### Запрос

```json
{
  "method": "setAuto",
  "params": {
    "Bids": [
      {
        "KeywordId": 444555666,
        "Scope": ["SEARCH"]
      },
      {
        "KeywordId": 444555667,
        "Scope": ["SEARCH", "NETWORK"]
      }
    ]
  }
}
```

### Параметры

| Параметр | Тип | Описание |
|----------|-----|----------|
| `KeywordId` | long | ID ключевой фразы |
| `Scope` | array[enum] | Область применения: `SEARCH`, `NETWORK` |
| `CalculateBy` | enum | Метод расчёта: `TRAFFIC_VOLUME`, `POSITION` |

### Ответ

```json
{
  "result": {
    "SetAutoResults": [
      {
        "KeywordId": 444555666
      }
    ]
  }
}
```

---

## Примеры использования

### Python: Получение рекомендуемых ставок

```python
def get_recommended_bids(client, keyword_ids: list):
    """
    Получение рекомендуемых ставок для ключевых фраз.
    """
    response = client.request("bids", {
        "method": "get",
        "params": {
            "SelectionCriteria": {
                "KeywordIds": keyword_ids
            },
            "FieldNames": [
                "KeywordId",
                "Bid",
                "AuctionBids"
            ]
        }
    })

    bids = response.get("Bids", [])
    recommendations = []

    for bid in bids:
        keyword_id = bid["KeywordId"]
        current_bid = bid.get("Bid", 0) / 1_000_000

        auction = bid.get("AuctionBids", {})
        pos1 = auction.get("Position1", {})
        recommended = pos1.get("Bid", 0) / 1_000_000

        recommendations.append({
            "keyword_id": keyword_id,
            "current_bid": current_bid,
            "recommended_bid": recommended,
            "traffic_volume": pos1.get("TrafficVolume", 0)
        })

    return recommendations


# Использование
recs = get_recommended_bids(client, [444555666, 444555667])
for rec in recs:
    print(f"ID {rec['keyword_id']}: текущая {rec['current_bid']}₽, "
          f"рекомендуемая {rec['recommended_bid']}₽ (охват {rec['traffic_volume']}%)")
```

### Python: Массовая установка ставок

```python
def set_bids_batch(client, bids_data: dict):
    """
    Массовая установка ставок.

    Args:
        bids_data: {keyword_id: bid_in_rubles}
    """
    bids = [
        {
            "KeywordId": kw_id,
            "Bid": int(bid * 1_000_000)
        }
        for kw_id, bid in bids_data.items()
    ]

    # Разбиваем на батчи по 10000
    batch_size = 10000
    all_results = []

    for i in range(0, len(bids), batch_size):
        batch = bids[i:i + batch_size]

        response = client.request("bids", {
            "method": "set",
            "params": {
                "Bids": batch
            }
        })

        results = response.get("SetResults", [])
        all_results.extend(results)

    successful = [r["KeywordId"] for r in all_results if "Errors" not in r]
    return successful


# Использование (бесплатно!)
new_bids = {
    444555666: 45.0,
    444555667: 30.0,
    444555668: 55.0
}

updated = set_bids_batch(client, new_bids)
print(f"Обновлено ставок: {len(updated)}")
```

### Python: Оптимизация ставок по позициям

```python
def optimize_bids_for_position(client, adgroup_id: int, target_position: int = 1):
    """
    Оптимизация ставок для достижения целевой позиции.

    Args:
        target_position: 1-4 (спецразмещение)
    """
    position_map = {
        1: "Position1",
        2: "Position2",
        3: "Position3",
        4: "Position4"
    }

    pos_key = position_map.get(target_position, "Position1")

    # Получаем текущие ставки и рекомендации
    response = client.request("bids", {
        "method": "get",
        "params": {
            "SelectionCriteria": {
                "AdGroupIds": [adgroup_id],
                "ServingStatuses": ["ELIGIBLE"]
            },
            "FieldNames": ["KeywordId", "Bid", "AuctionBids"]
        }
    })

    bids_to_update = []

    for bid in response.get("Bids", []):
        auction = bid.get("AuctionBids", {})
        target = auction.get(pos_key, {})

        if target:
            recommended_bid = target.get("Bid", 0)
            current_bid = bid.get("Bid", 0)

            if recommended_bid > current_bid:
                bids_to_update.append({
                    "KeywordId": bid["KeywordId"],
                    "Bid": recommended_bid
                })

    if bids_to_update:
        # Устанавливаем новые ставки (бесплатно!)
        client.request("bids", {
            "method": "set",
            "params": {
                "Bids": bids_to_update
            }
        })

    return len(bids_to_update)


# Использование
updated = optimize_bids_for_position(client, 789012, target_position=1)
print(f"Оптимизировано ставок: {updated}")
```

---

[← Keywords](./keywords.md) | [BidModifiers →](./bidmodifiers.md)

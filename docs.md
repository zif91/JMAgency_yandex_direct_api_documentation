# **API Яндекс.Директ v5 \- Полная документация**

Структурированное руководство для разработчиков по работе с API Яндекс.Директа версии 5\.

## **Содержание**

* [1\. Введение](https://www.google.com/search?q=%231-%D0%B2%D0%B2%D0%B5%D0%B4%D0%B5%D0%BD%D0%B8%D0%B5)  
* [2\. Аутентификация](https://www.google.com/search?q=%232-%D0%B0%D1%83%D1%82%D0%B5%D0%BD%D1%82%D0%B8%D1%84%D0%B8%D0%BA%D0%B0%D1%86%D0%B8%D1%8F)  
* [3\. Структура API](https://www.google.com/search?q=%233-%D1%81%D1%82%D1%80%D1%83%D0%BA%D1%82%D1%83%D1%80%D0%B0-api)  
* [4\. Справочник сервисов API](https://www.google.com/search?q=%234-%D1%81%D0%BF%D1%80%D0%B0%D0%B2%D0%BE%D1%87%D0%BD%D0%B8%D0%BA-%D1%81%D0%B5%D1%80%D0%B2%D0%B8%D1%81%D0%BE%D0%B2-api)  
  * [4.1. Campaigns](https://www.google.com/search?q=%2341-campaigns)  
  * [4.2. AdGroups](https://www.google.com/search?q=%2342-adgroups)  
  * [4.3. Ads](https://www.google.com/search?q=%2343-ads)  
  * [4.4. Keywords](https://www.google.com/search?q=%2344-keywords)  
  * [4.5. KeywordBids](https://www.google.com/search?q=%2345-keywordbids)  
  * [4.6. Reports \- Углубленное руководство](https://www.google.com/search?q=%2346-reports---%D1%83%D0%B3%D0%BB%D1%83%D0%B1%D0%BB%D0%B5%D0%BD%D0%BD%D0%BE%D0%B5-%D1%80%D1%83%D0%BA%D0%BE%D0%B2%D0%BE%D0%B4%D1%81%D1%82%D0%B2%D0%BE)  
* [5\. Лимиты и баллы](https://www.google.com/search?q=%235-%D0%BB%D0%B8%D0%BC%D0%B8%D1%82%D1%8B-%D0%B8-%D0%B1%D0%B0%D0%BB%D0%BB%D1%8B)  
* [6\. Обработка ошибок](https://www.google.com/search?q=%236-%D0%BE%D0%B1%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D0%BA%D0%B0-%D0%BE%D1%88%D0%B8%D0%B1%D0%BE%D0%BA)  
* [7\. Лучшие практики и примеры кода](https://www.google.com/search?q=%237-%D0%BB%D1%83%D1%87%D1%88%D0%B8%D0%B5-%D0%BF%D1%80%D0%B0%D0%BA%D1%82%D0%B8%D0%BA%D0%B8-%D0%B8-%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80%D1%8B-%D0%BA%D0%BE%D0%B4%D0%B0)

## **1\. Введение**

Программный интерфейс (API) Яндекс.Директа v5 предназначен для автоматизированного управления рекламными кампаниями.

### **1.1. Ключевые возможности**

* **Полное управление**: Создание, чтение, обновление и удаление всех сущностей рекламной кампании.  
* **Управление ставками и бюджетом**: Автоматизация стратегий, дневных бюджетов и корректировок.  
* **Детальная аналитика**: Получение статистики по показам, кликам, затратам и конверсиям.  
* **Интеграция**: Связь с CRM, BI-системами и внешними платформами.

### **1.2. Принципы работы**

* **Протокол**: HTTPS, метод POST.  
* **Формат данных**: JSON (рекомендуемый).  
* **Авторизация**: OAuth 2.0.  
* **Архитектура**: Модульные веб\-сервисы.

### **1.3. Базовые URL**

| Окружение | URL |
| :---- | :---- |
| **Production** | https://api.direct.yandex.com/json/v5/{service} |
| **Sandbox** | https://api-sandbox.direct.yandex.ru/json/v5/{service} |

## **2\. Аутентификация**

Для доступа к API требуется **OAuth 2.0 токен**.

### **2.1. Получение токена**

1. **Регистрация приложения**: Создайте приложение на [сервере Яндекс.OAuth](https://oauth.yandex.ru/client/new).  
2. **Запрос доступа к API**: В интерфейсе Яндекс.Директа подайте заявку на доступ.  
3. **Получение токена**: Обменяйте авторизационный код на токен доступа.

### **2.2. Авторизация запросов**

Каждый запрос должен содержать следующие HTTP-заголовки:

Authorization: Bearer {oauth\_token}  
Client-Login: {yandex\_direct\_login}  
Accept-Language: ru  
Content-Type: application/json; charset=utf-8

## **3\. Структура API**

### **3.1. Формат запроса**

{  
  "method": "get",  
  "params": {  
    "SelectionCriteria": {},  
    "FieldNames": \["Id", "Name", "Status"\]  
  }  
}

### **3.2. Формат ответа**

{  
  "result": {  
    "Campaigns": \[  
      {  
        "Id": 12345,  
        "Name": "Моя кампания",  
        "Status": "ACCEPTED"  
      }  
    \]  
  }  
}

### **3.3. Иерархия объектов**

Campaign  
└── AdGroup  
    ├── Ads  
    └── Keywords

## **4\. Справочник сервисов API**

Каждый сервис предоставляет стандартные методы: add, get, update, delete.

### **4.1. Campaigns**

Управление кампаниями.

### **4.2. AdGroups**

Управление группами объявлений.

### **4.3. Ads**

Управление объявлениями.

### **4.4. Keywords**

Управление ключевыми фразами.

### **4.5. KeywordBids**

Управление ставками.

### **4.6. Reports \- Углубленное руководство**

Сервис **Reports** предназначен для формирования и получения статистических отчетов.

#### **4.6.1. Процесс формирования отчета**

1. **Отправка запроса**: Выполните POST-запрос к сервису Reports, указав в теле JSON-структуру ReportDefinition с параметрами отчета.  
2. **Обработка ответа**:  
   * **Онлайн-режим (HTTP 200\)**: Для отчетов с небольшим объемом данных. Отчет возвращается немедленно в теле ответа.  
   * **Офлайн-режим (HTTP 201/202)**: Для отчетов с большим объемом данных.  
     * **HTTP 201 Created**: Запрос принят, отчет поставлен в очередь на формирование.  
     * **HTTP 202 Accepted**: Отчет все еще формируется. Повторите запрос через некоторое время (рекомендуемый интервал указан в заголовке retryIn).  
3. **Получение готового отчета**: Повторяйте запрос с теми же параметрами до получения ответа с кодом **HTTP 200**, который будет содержать готовый отчет в формате TSV.

#### **4.6.2. Ключевые параметры отчета (ReportDefinition)**

##### **ReportName**

* **Тип**: string  
* **Описание**: Название отчета. В офлайн-режиме должно быть уникальным для рекламодателя.  
* **Обязательный**: Да.

##### **ReportType**

* **Тип**: enum  
* **Описание**: Определяет набор доступных полей и базовую группировку данных.  
* **Обязательный**: Да.

| Тип отчета | Описание | Добавляемая группировка |
| :---- | :---- | :---- |
| ACCOUNT\_PERFORMANCE\_REPORT | Статистика по аккаунту | \- |
| CAMPAIGN\_PERFORMANCE\_REPORT | Статистика по кампаниям | CampaignId |
| ADGROUP\_PERFORMANCE\_REPORT | Статистика по группам объявлений | AdGroupId |
| AD\_PERFORMANCE\_REPORT | Статистика по объявлениям | AdId |
| CRITERIA\_PERFORMANCE\_REPORT | Статистика по условиям показа | AdGroupId, CriteriaId, CriteriaType |
| CUSTOM\_REPORT | Отчет с произвольными группировками | \- |
| SEARCH\_QUERY\_PERFORMANCE\_REPORT | Статистика по поисковым запросам | AdGroupId, Query |
| REACH\_AND\_FREQUENCY\_PERFORMANCE\_REPORT | Статистика по медийным кампаниям | CampaignId |

##### **DateRangeType**

* **Тип**: enum  
* **Описание**: Период, за который запрашивается статистика.  
* **Обязательный**: Да.

| Значение | Описание |
| :---- | :---- |
| TODAY | Текущий день |
| YESTERDAY | Вчерашний день |
| LAST\_7\_DAYS | Последние 7 дней, не включая текущий |
| LAST\_30\_DAYS | Последние 30 дней, не включая текущий |
| LAST\_90\_DAYS | Последние 90 дней, не включая текущий |
| THIS\_MONTH | Текущий календарный месяц |
| LAST\_MONTH | Прошлый календарный месяц |
| ALL\_TIME | Вся доступная статистика |
| CUSTOM\_DATE | Произвольный период (требует DateFrom, DateTo) |
| AUTO | Период с возможными изменениями статистики |

##### **FieldNames**

* **Тип**: array of string  
* **Описание**: Список полей (столбцов), которые будут включены в отчет. Набор доступных полей зависит от ReportType.  
* **Обязательный**: Да.

##### **SelectionCriteria**

* **Тип**: object  
* **Описание**: Содержит критерии отбора данных, включая даты и фильтры.  
* **Обязательный**: Да.

##### **Filter (внутри SelectionCriteria)**

* **Тип**: array of objects  
* **Описание**: Массив фильтров для отбора данных. Фильтры объединяются по логическому "И".  
  * Field: Имя поля для фильтрации.  
  * Operator: Оператор сравнения (EQUALS, IN, GREATER\_THAN и др.).  
  * Values: Массив значений для сравнения.

**Пример фильтра:**

"Filter": \[{  
    "Field": "Clicks",  
    "Operator": "GREATER\_THAN",  
    "Values": \["100"\]  
}\]

##### **IncludeVAT**

* **Тип**: enum ("YES" | "NO")  
* **Описание**: Включать ли НДС в денежные значения.  
* **Обязательный**: Да.

##### **Format**

* **Тип**: enum ("TSV")  
* **Описание**: Формат отчета. В настоящее время поддерживается только TSV.  
* **Обязательный**: Да.

#### **4.6.3. Спецификация полей**

Поля в отчетах делятся на три категории:

* **Сегмент**: Поле, используемое для группировки данных (например, CampaignId, Device).  
* **Метрика**: Числовое значение, рассчитанное для заданных группировок (например, Clicks, Cost).  
* **Атрибут**: Фиксированное значение, не создающее новой группировки (например, CampaignName в отчете по группам).

Полный список полей, их типы и совместимость с различными типами отчетов доступны в [официальной документации](https://yandex.ru/dev/direct/doc/reports/fields.html).

#### **4.6.4. Денежные значения**

* **Валюта**: Денежные значения возвращаются в валюте рекламодателя.  
* **Единицы**: По умолчанию суммы возвращаются в **микроединицах** (сумма в валюте × 1,000,000). Чтобы получать значения в основной валюте, используйте HTTP-заголовок returnMoneyInMicros: false.

#### **4.6.5. Пример запроса отчета**

{  
  "params": {  
    "ReportName": "Campaign Performance Report for Last Week",  
    "ReportType": "CAMPAIGN\_PERFORMANCE\_REPORT",  
    "DateRangeType": "LAST\_WEEK",  
    "Format": "TSV",  
    "IncludeVAT": "NO",  
    "SelectionCriteria": {  
      "Filter": \[  
        {  
          "Field": "Impressions",  
          "Operator": "GREATER\_THAN",  
          "Values": \["50"\]  
        }  
      \]  
    },  
    "FieldNames": \[  
      "Date",  
      "CampaignName",  
      "Impressions",  
      "Clicks",  
      "Ctr",  
      "Cost"  
    \],  
    "OrderBy": \[  
      {  
        "Field": "Date",  
        "SortOrder": "ASCENDING"  
      }  
    \]  
  }  
}

## **5\. Лимиты и баллы**

API использует систему баллов (Units) для управления нагрузкой.

### **5.1. Система баллов**

* **Суточный лимит**: Индивидуален для каждого рекламодателя.  
* **Контроль**: HTTP-заголовок Units в ответе показывает расход и остаток.  
  * Формат: Units: {израсходовано}/{остаток}/{лимит}

### **5.2. Стоимость операций**

| Операция | Стоимость (в баллах) |
| :---- | :---- |
| Вызов метода | Базовая стоимость |
| За каждый возвращенный объект | 1 |
| **Ошибка вызова или операции** | **20** |
| KeywordBids.set | 0 |

### **5.3. Технические лимиты**

* **Одновременные соединения**: Не более 5 на рекламодателя.  
* **Сервис Reports**: Не более 5 офлайн-отчетов в очереди.

## **6\. Обработка ошибок**

### **6.1. HTTP-коды**

| Код | Значение | Действие |
| :---- | :---- | :---- |
| 200 | OK | Обработать ответ. |
| 201 | Created | Отчет в очереди. Повторить запрос позже. |
| 202 | Accepted | Отчет формируется. Повторить запрос позже. |
| 400 | Bad Request | Исправить параметры запроса. |
| 401 | Unauthorized | Проверить/обновить токен. |
| 429 | Too Many Requests | Снизить частоту запросов. |
| 5xx | Server Error | Повторить с экспоненциальной задержкой. |

### **6.2. Коды ошибок API**

Детальные коды ошибок возвращаются в теле ответа и описаны в [официальной документации](https://yandex.ru/dev/direct/doc/ref-v5/concepts/errors-list.html).

## **7\. Лучшие практики и примеры кода**

### **7.1. Оптимизация производительности**

* **Асинхронные запросы**: Используйте asyncio и aiohttp для параллельного выполнения запросов, не превышая лимит соединений.  
* **Пакетные операции**: Группируйте однотипные операции (например, добавление 1000 ключевых фраз) в один запрос.  
* **Пагинация**: Для получения больших наборов данных используйте параметры Page.Limit и Page.Offset.  
* **Кеширование**: Кешируйте данные, которые редко изменяются (например, справочники из сервиса Dictionaries).

### **7.2. Пример кода (Менеджер отчетов)**

import requests  
import time  
import pandas as pd  
from io import StringIO

class ReportManager:  
    """Менеджер для работы с отчетами API Яндекс.Директ."""

    def \_\_init\_\_(self, token: str, login: str):  
        self.token \= token  
        self.login \= login  
        self.base\_url \= "https://api.direct.yandex.com/json/v5"

    def get\_report(self, report\_definition: dict) \-\> pd.DataFrame:  
        """  
        Запрашивает и получает отчет, обрабатывая онлайн и офлайн режимы.  
        """  
        headers \= {  
            "Authorization": f"Bearer {self.token}",  
            "Client-Login": self.login,  
            "Accept-Language": "ru",  
            "returnMoneyInMicros": "false" \# Получать суммы в рублях  
        }  
        body \= {"params": report\_definition}  
        url \= f"{self.base\_url}/reports"

        max\_retries \= 5  
        for attempt in range(max\_retries):  
            try:  
                response \= requests.post(url, json=body, headers=headers)  
                response.raise\_for\_status() \# Проверка на HTTP ошибки 4xx/5xx

                if response.status\_code \== 200:  
                    print("✅ Отчет сформирован и получен.")  
                    return self.\_parse\_tsv\_report(response.text)  
                elif response.status\_code in \[201, 202\]:  
                    retry\_in \= int(response.headers.get("retryIn", 30))  
                    print(f"📊 Отчет формируется. Ожидание {retry\_in} сек. (Попытка {attempt \+ 1}/{max\_retries})")  
                    time.sleep(retry\_in)  
                else:  
                    raise Exception(f"Неожиданный статус ответа: {response.status\_code}")

            except requests.exceptions.RequestException as e:  
                print(f"❌ Ошибка сети: {e}")  
                time.sleep(30) \# Пауза при сетевых сбоях

        raise Exception("Не удалось получить отчет после нескольких попыток.")

    def \_parse\_tsv\_report(self, tsv\_data: str) \-\> pd.DataFrame:  
        """Парсит TSV-отчет в pandas DataFrame."""  
        lines \= tsv\_data.strip().split('\\n')  
        if len(lines) \< 2:  
            return pd.DataFrame() \# Пустой отчет

        \# Пропускаем заголовок отчета (первая строка) и итоговую строку (последняя)  
        report\_content \= '\\n'.join(lines\[1:-1\])  
        df \= pd.read\_csv(StringIO(report\_content), sep='\\t')  
        return df

\# Пример использования  
if \_\_name\_\_ \== '\_\_main\_\_':  
    TOKEN \= "YOUR\_OAUTH\_TOKEN"  
    LOGIN \= "your-direct-login"

    report\_def \= {  
        "ReportName": "Campaign Performance Last 7 Days",  
        "ReportType": "CAMPAIGN\_PERFORMANCE\_REPORT",  
        "DateRangeType": "LAST\_7\_DAYS",  
        "Format": "TSV",  
        "IncludeVAT": "NO",  
        "SelectionCriteria": {},  
        "FieldNames": \["Date", "CampaignName", "Impressions", "Clicks", "Cost"\]  
    }

    try:  
        report\_manager \= ReportManager(TOKEN, LOGIN)  
        report\_df \= report\_manager.get\_report(report\_def)  
        print(report\_df.head())  
    except Exception as e:  
        print(f"Ошибка при получении отчета: {e}")


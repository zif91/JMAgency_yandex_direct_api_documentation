# Yandex Direct Multi-Account Panel

Панель управления несколькими аккаунтами Yandex Direct с AI-аудитом кампаний.

## Возможности

- **Мульти-аккаунты**: Подключение нескольких аккаунтов Yandex Direct к одному пользователю
- **AI-аудит**: Автоматический анализ кампаний с рекомендациями (использует Claude API)
- **REST API**: Полный доступ к API Yandex Direct через простой REST интерфейс
- **Веб-интерфейс**: Удобный дашборд для управления аккаунтами

## Быстрый старт

### 1. Установка

```bash
cd panel
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Настройка

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Заполните переменные:

```env
SECRET_KEY=your-secret-key-here
YANDEX_CLIENT_ID=your-yandex-client-id
YANDEX_CLIENT_SECRET=your-yandex-client-secret
REDIRECT_URI=http://localhost:5000/oauth/yandex/callback
ANTHROPIC_API_KEY=your-anthropic-api-key  # опционально, для AI-аудита
```

### 3. Инициализация базы данных

```bash
flask init-db
```

### 4. Запуск

```bash
flask run
# или
python app.py
```

Откройте http://localhost:5000

## Структура проекта

```
panel/
├── app.py              # Flask приложение
├── db.py               # База данных (SQLite)
├── yandex_api.py       # Клиент Yandex Direct API
├── audit_agent.py      # AI-агент для аудита
├── requirements.txt
├── .env.example
├── templates/          # HTML шаблоны
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── accounts.html
│   ├── audit.html
│   ├── audit_result.html
│   ├── settings.html
│   └── error.html
├── static/
│   └── style.css
└── tests/
    └── test_app.py
```

## API Endpoints

### Аутентификация

Все API запросы требуют API ключ в заголовке:

```
Authorization: Bearer YOUR_API_KEY
```

### Аккаунты

```bash
# Получить список аккаунтов
GET /api/accounts
```

### Кампании

```bash
# Получить кампании
GET /api/campaigns?account_id=ACCOUNT_ID
```

### Группы объявлений

```bash
# Получить группы по ID кампаний
POST /api/adgroups
{
    "account_id": "ACCOUNT_ID",
    "campaign_ids": [12345, 67890]
}
```

### Объявления

```bash
# Получить объявления
POST /api/ads
{
    "account_id": "ACCOUNT_ID",
    "adgroup_ids": [111, 222]
}
```

### Ключевые слова

```bash
# Получить ключевые слова
POST /api/keywords
{
    "account_id": "ACCOUNT_ID",
    "campaign_ids": [12345]
}
```

### Ставки

```bash
# Получить ставки
GET /api/bids?account_id=ACCOUNT_ID&campaign_ids=123&campaign_ids=456
```

### Отчёты

```bash
# Получить отчёт
POST /api/reports
{
    "account_id": "ACCOUNT_ID",
    "ReportName": "Campaign Performance",
    "ReportType": "CAMPAIGN_PERFORMANCE_REPORT",
    "DateRangeType": "LAST_30_DAYS",
    "Format": "TSV",
    "FieldNames": ["Date", "CampaignName", "Impressions", "Clicks", "Cost"]
}
```

### Аудит

```bash
# Запустить аудит
POST /api/audit
{
    "account_id": "ACCOUNT_ID",
    "audit_type": "full"  # full, campaigns, adgroups, ads, keywords
}

# История аудитов
GET /api/audit/history?limit=10
```

## База данных

### Таблица users

| Поле | Тип | Описание |
|------|-----|----------|
| id | TEXT | UUID пользователя |
| email | TEXT | Email (уникальный) |
| password_hash | TEXT | Хеш пароля |
| api_key | TEXT | API ключ (уникальный) |
| created_at | TEXT | Дата создания |
| updated_at | TEXT | Дата обновления |

### Таблица yandex_accounts

| Поле | Тип | Описание |
|------|-----|----------|
| id | TEXT | UUID аккаунта |
| user_id | TEXT | ID пользователя (FK) |
| account_name | TEXT | Название аккаунта |
| yandex_login | TEXT | Логин Yandex |
| yandex_token | TEXT | OAuth токен |
| is_active | INTEGER | Активен (1/0) |
| created_at | TEXT | Дата создания |
| updated_at | TEXT | Дата обновления |

### Таблица audit_history

| Поле | Тип | Описание |
|------|-----|----------|
| id | TEXT | UUID аудита |
| user_id | TEXT | ID пользователя (FK) |
| yandex_account_id | TEXT | ID аккаунта (FK) |
| audit_type | TEXT | Тип аудита |
| status | TEXT | Статус (pending, running, completed, failed) |
| result | TEXT | JSON результат |
| created_at | TEXT | Дата создания |
| completed_at | TEXT | Дата завершения |

## AI-аудит

Агент анализирует:

- **Структуру аккаунта**: пустые кампании, слишком много групп
- **Кампании**: бюджеты, статусы модерации, неактивные кампании
- **Группы объявлений**: минус-слова, структура
- **Объявления**: A/B тестирование, отклонённые объявления, сайтлинки
- **Ключевые слова**: дубликаты, типы соответствия, низкие ставки

### Уровни важности

- **Critical** - Требует немедленного внимания
- **Warning** - Нужно исправить в ближайшее время
- **Info** - Информационные замечания
- **Opportunity** - Возможности для оптимизации

## Разработка

### Запуск тестов

```bash
pytest tests/
```

### Структура кода

- `app.py` - Маршруты Flask и логика приложения
- `db.py` - Функции работы с базой данных
- `yandex_api.py` - Обёртка над Yandex Direct API v5
- `audit_agent.py` - Логика AI-аудита

## Получение OAuth ключей Yandex

1. Перейдите на https://oauth.yandex.ru/
2. Создайте новое приложение
3. Укажите Redirect URI: `http://localhost:5000/oauth/yandex/callback`
4. Запросите доступ к "Yandex Direct API"
5. Сохраните Client ID и Client Secret в `.env`

## Лицензия

MIT License

# Развертывание на Railway

## Быстрый старт

### 1. Подготовка проекта

Этот проект готов для развертывания на Railway. Все необходимые файлы уже включены:
- `Procfile` - команда запуска через Gunicorn
- `railway.json` - конфигурация Railway
- `requirements.txt` - зависимости Python
- `app.py` - основное приложение Flask

### 2. Создание проекта на Railway

1. Перейдите на https://railway.app
2. Нажмите "New Project"
3. Выберите "Deploy from GitHub repo"
4. Выберите репозиторий `JMAgency_yandex_direct_api_documentation`
5. Выберите ветку `yandex-direct-mcp-server`

### 3. Настройка переменных окружения

В настройках проекта Railway добавьте следующие переменные:

```
YANDEX_CLIENT_ID=ваш_client_id_из_яндекс_oauth
YANDEX_CLIENT_SECRET=ваш_client_secret_из_яндекс_oauth
```

**Получение Client ID и Secret:**
1. Перейдите на https://oauth.yandex.ru/client/new
2. Создайте новое приложение
3. Укажите Redirect URI: `https://your-railway-app.up.railway.app/redirect`
4. Скопируйте Client ID и Client Secret

### 4. Инициализация базы данных

Railway автоматически создаст файл `database.db` при первом запуске.

Если нужно инициализировать БД вручную:
```bash
flask init-db
```

### 5. Проверка развертывания

После успешного деплоя:
1. Откройте URL вашего приложения (например: `https://your-app.up.railway.app`)
2. Вы увидите главную страницу с кнопкой "Login with Yandex"
3. Нажмите на кнопку и авторизуйтесь через Яндекс
4. Получите свой API ключ (secret_code)

### 6. Использование API

После получения secret_code, вы можете использовать API:

```bash
# Получить кампании
curl -X GET https://your-app.up.railway.app/api/campaigns \
  -H "Authorization: Bearer YOUR_SECRET_CODE"

# Получить отчет
curl -X POST https://your-app.up.railway.app/api/reports \
  -H "Authorization: Bearer YOUR_SECRET_CODE" \
  -H "Content-Type: application/json" \
  -d '{
    "ReportName": "Test Report",
    "ReportType": "CAMPAIGN_PERFORMANCE_REPORT",
    "DateRangeType": "LAST_7_DAYS",
    "Format": "TSV",
    "IncludeVAT": "NO",
    "SelectionCriteria": {},
    "FieldNames": ["Date", "CampaignName", "Impressions", "Clicks", "Cost"]
  }'
```

## Настройка Railway

### Автоматический деплой

Railway автоматически деплоит изменения при push в выбранную ветку.

### Логи

Для просмотра логов:
1. Откройте проект в Railway Dashboard
2. Перейдите в раздел "Deployments"
3. Выберите последний деплой
4. Нажмите "View Logs"

### Переменные окружения

Railway автоматически предоставляет:
- `PORT` - порт для прослушивания (приложение настроено на его использование)
- `RAILWAY_ENVIRONMENT` - окружение (production/staging)

### Ограничения Railway Free Tier

- 500 часов выполнения в месяц
- 500 MB RAM
- 1 GB storage

## Troubleshooting

### Ошибка "Application failed to respond"

**Причина:** Приложение не слушает правильный порт

**Решение:** Убедитесь, что app.py использует `PORT` из переменных окружения (уже исправлено в коде)

### Ошибка OAuth redirect

**Причина:** Неправильный Redirect URI в настройках Яндекс.OAuth

**Решение:**
1. Перейдите в настройки приложения на https://oauth.yandex.ru
2. Обновите Redirect URI на актуальный URL Railway: `https://your-app.up.railway.app/redirect`

### База данных не инициализирована

**Причина:** Файл database.db не создан

**Решение:**
1. Подключитесь к контейнеру Railway
2. Выполните: `flask init-db`
3. Или перезапустите приложение

### Ошибка 502 на favicon.ico

Это нормально и не влияет на работу приложения. Favicon можно добавить позже.

## Мониторинг

Railway предоставляет встроенные метрики:
- CPU usage
- Memory usage
- Network traffic
- Request logs

## Масштабирование

Для увеличения производительности:
1. Увеличьте количество workers в Procfile: `--workers 4`
2. Добавьте больше памяти в настройках Railway
3. Рассмотрите использование внешней БД (PostgreSQL) вместо SQLite

## Безопасность

1. **Не коммитьте** файл `.env` с реальными credentials
2. Все переменные окружения храните в Railway Dashboard
3. Используйте HTTPS (Railway предоставляет автоматически)
4. Регулярно обновляйте зависимости: `pip list --outdated`

## Поддержка

Если возникли проблемы:
1. Проверьте логи в Railway Dashboard
2. Откройте issue на GitHub
3. Обратитесь в Railway Help Station: https://help.railway.app

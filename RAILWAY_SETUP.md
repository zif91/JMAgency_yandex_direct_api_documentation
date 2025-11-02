# Настройка проекта на Railway - Пошаговая инструкция

## Шаг 1: Обновить настройки Railway проекта

1. Перейдите на https://railway.app
2. Найдите ваш проект **reasonable-vitality**
3. Нажмите на проект, чтобы открыть его

## Шаг 2: Изменить ветку для деплоя

**ВАЖНО:** Нужно переключить проект на новую ветку с исправлениями.

1. В настройках проекта найдите раздел **Source** или **GitHub**
2. Измените ветку с `yandex-direct-mcp-server` на:
   ```
   claude/railway-deployment-011CUcFQ5QXDLjPZ2tXADKHr
   ```
3. Или используйте ветку `yandex-direct-mcp-server` (если туда будет мердж)

## Шаг 3: Настроить переменные окружения

В разделе **Variables** добавьте следующие переменные:

### Обязательные переменные:

```bash
YANDEX_CLIENT_ID=595ee7b93f2143e7a4bad73b0e7f4649
YANDEX_CLIENT_SECRET=1c9b1e275fad454fb590c6c938f2c123
```

### REDIRECT_URI

После первого деплоя Railway предоставит публичный URL (например: `https://your-app.up.railway.app`).

Добавьте переменную:
```bash
REDIRECT_URI=https://your-app.up.railway.app/redirect
```

**ВАЖНО:** После этого также обновите Redirect URI в настройках Яндекс.OAuth:
1. Перейдите на https://oauth.yandex.ru
2. Найдите приложение с ID `595ee7b93f2143e7a4bad73b0e7f4649`
3. Обновите Redirect URI на `https://your-app.up.railway.app/redirect`

## Шаг 4: Настроить команду запуска (если нужно)

Railway должен автоматически обнаружить `Procfile`, но если нет:

1. Перейдите в **Settings** → **Deploy**
2. В поле **Start Command** укажите:
   ```bash
   gunicorn app:app --bind 0.0.0.0:$PORT --timeout 300 --workers 2
   ```

## Шаг 5: Запустить деплой

1. Нажмите **Deploy** или дождитесь автоматического деплоя
2. Следите за логами в разделе **Deployments**
3. Дождитесь успешного завершения

## Шаг 6: Проверка работы

После успешного деплоя:

1. Откройте публичный URL вашего приложения
2. Вы должны увидеть главную страницу с кнопкой "Login with Yandex"
3. Нажмите на кнопку и проверьте, что OAuth работает
4. После авторизации вы получите secret_code

## Что было исправлено?

### Проблема:
```
Application failed to respond
```

### Причина:
Приложение использовало жестко закодированный порт `5000`, но Railway требует использовать переменную окружения `PORT`.

### Решение:
```python
# Было:
app.run(debug=True, port=5000)

# Стало:
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port, debug=False)
```

### Также добавлено:

1. **Автоматическая инициализация БД** - database.db создается при первом запуске
2. **Favicon route** - убирает 502 ошибки на `/favicon.ico`
3. **Gunicorn** - production-ready WSGI сервер вместо встроенного Flask
4. **Динамический REDIRECT_URI** - берется из переменных окружения
5. **Procfile и railway.json** - правильная конфигурация для Railway

## Проверка логов

Если что-то не работает:

1. Откройте проект в Railway
2. Перейдите в **Deployments**
3. Выберите последний деплой
4. Нажмите **View Logs**

Вы должны увидеть:
```
Database not found, initializing...
Database initialized successfully
[INFO] Starting gunicorn 21.2.0
[INFO] Listening at: http://0.0.0.0:XXXX
[INFO] Using worker: sync
[INFO] Booting worker with pid: XXX
```

## Troubleshooting

### Ошибка: "Database not found"
**Решение:** Приложение автоматически создаст БД при первом запуске

### Ошибка: "Invalid client_id"
**Решение:** Проверьте правильность YANDEX_CLIENT_ID в переменных окружения

### Ошибка: OAuth redirect
**Решение:**
1. Убедитесь, что REDIRECT_URI совпадает с URL в Яндекс.OAuth
2. Формат: `https://your-app.up.railway.app/redirect`

### Приложение стартует, но не отвечает
**Решение:** Проверьте, что используется правильная ветка с исправлениями

## Проверка API

После успешного деплоя проверьте API:

```bash
# Получить кампании
curl -X GET https://your-app.up.railway.app/api/campaigns \
  -H "Authorization: Bearer YOUR_SECRET_CODE"
```

Если получаете 401 - нужно сначала авторизоваться и получить secret_code.

## Следующие шаги

1. ✅ Деплой на Railway
2. ✅ Авторизация через Яндекс
3. ✅ Получение secret_code
4. Настройка MCP клиента для Jenova AI
5. Тестирование API endpoints

## Полезные ссылки

- Railway Dashboard: https://railway.app/dashboard
- Railway Docs: https://docs.railway.com
- Яндекс.OAuth: https://oauth.yandex.ru
- GitHub Repo: https://github.com/zif91/JMAgency_yandex_direct_api_documentation

---

Если возникли проблемы - проверьте файл **RAILWAY.md** для подробной информации.

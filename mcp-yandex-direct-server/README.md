## MCP сервер: Яндекс.Директ v5 аудит

Функционал:
- Доступ к отчетам (Reports), кампаниям, группам, объявлениям, ключевым словам и пр. для детальных аудитов
- OAuth-логин и привязка токена к вашему секретному коду
- Возможность ручной привязки уже полученного токена

### Установка

1) Скопируйте `.env.example` в `.env` и заполните значения:
- `YANDEX_CLIENT_ID`, `YANDEX_CLIENT_SECRET` — из кабинета Яндекс.OAuth
- `OAUTH_REDIRECT_URI` — должен совпадать с настройкой приложения (например `http://localhost:8787/oauth/callback`)
- (опц.) `TOKEN_ENCRYPTION_KEY_BASE64` — 32-байтовый ключ base64 для AES-256-GCM

2) Установка и сборка:
```
npm install
npm run build
```

### Запуск
```
npm start
```
Сервер запускается как MCP по stdio (см. `mcp.json`).

### Инструменты (tools)
- `start_oauth({ secretCode, scope?: "direct:api" })` → возвращает ссылку для авторизации, по завершении токен будет привязан к `secretCode`
- `attach_token({ secretCode, oauthToken, login? })` → вручную привязать токен (и, при желании, логин по умолчанию)
- `set_active_token({ secretCode })` → выбрать активный токен для последующих вызовов
- `list_campaigns({ secretCode?, clientLogin, selectionCriteria?, fieldNames?, page? })`
- `list_adgroups({ secretCode?, clientLogin, selectionCriteria?, fieldNames?, page? })`
- `list_ads({ secretCode?, clientLogin, selectionCriteria?, fieldNames?, page? })`
- `list_keywords({ secretCode?, clientLogin, selectionCriteria?, fieldNames?, page? })`
- `get_report({ secretCode?, clientLogin, reportDefinition, returnMoneyInMicros?, maxRetries? })` → TSV-строка
- `call_service({ secretCode?, clientLogin, service, method, params })` → универсальный вызов v5

Примечания:
- Для вызовов API обязателен заголовок `Client-Login` — передается как аргумент `clientLogin`.
- Reports реализует онлайн/офлайн режимы согласно документации v5; по `201/202` делается повтор с задержкой (`retryIn`).

### Источник спецификации
Основано на `docs.md` (справочник v5, Reports, заголовки, статусы, лимиты).
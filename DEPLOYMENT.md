# Развертывание сервера на direct.jmagency.ru

## Архитектура решения

```
┌─────────────────────────────────────────────────────────────┐
│                    Пользователь                              │
│                                                              │
│  1. Заходит на https://direct.jmagency.ru                   │
│  2. Авторизуется через Яндекс OAuth                         │
│  3. Получает API ключ (secret_code)                         │
│  4. Использует ключ в MCP клиенте (Jenova AI/Claude)       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│            Сервер: direct.jmagency.ru                       │
│                                                              │
│  ┌────────────────────────────────────────────┐            │
│  │  Flask API (app.py)                        │            │
│  │  - /login - OAuth flow                     │            │
│  │  - /redirect - получение токена            │            │
│  │  - /api/campaigns - API endpoints          │            │
│  │  - /api/adgroups, /api/ads, etc.          │            │
│  └────────────────────────────────────────────┘            │
│                    │                                         │
│                    ▼                                         │
│  ┌────────────────────────────────────────────┐            │
│  │  SQLite DB (database.db)                   │            │
│  │  - yandex_login                            │            │
│  │  - yandex_token (OAuth токен от Яндекса)  │            │
│  │  - secret_code (API ключ для MCP)         │            │
│  └────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│          Яндекс.Директ API                                  │
│          https://api.direct.yandex.com                      │
└─────────────────────────────────────────────────────────────┘
```

## Шаг 1: Регистрация приложения в Яндекс.OAuth

1. Перейдите на https://oauth.yandex.ru/client/new
2. Заполните форму:
   - **Название**: Yandex Direct MCP Server
   - **Платформы**: Веб-сервисы
   - **Redirect URI**: `https://direct.jmagency.ru/redirect`
3. В разделе "Доступы" выберите:
   - **Яндекс.Директ** → полный доступ
4. Нажмите "Создать приложение"
5. Скопируйте:
   - **ClientID** (например: `595ee7b93f2143e7a4bad73b0e7f4649`)
   - **Client secret** (например: `1c9b1e275fad454fb590c6c938f2c123`)

## Шаг 2: Подготовка сервера

### 2.1 Установка зависимостей

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и необходимых пакетов
sudo apt install -y python3 python3-pip python3-venv nginx

# Создание директории для проекта
sudo mkdir -p /var/www/yandex-direct-mcp
sudo chown $USER:$USER /var/www/yandex-direct-mcp
cd /var/www/yandex-direct-mcp
```

### 2.2 Клонирование проекта

```bash
# Клонирование ветки с Flask сервером
git clone https://github.com/zif91/JMAgency_yandex_direct_api_documentation.git .
git checkout yandex-direct-mcp-server

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
pip install gunicorn
```

### 2.3 Конфигурация

Создайте файл `.env`:

```bash
cat > .env << EOF
YANDEX_CLIENT_ID=ВАШ_CLIENT_ID_ИЗ_ШАГА_1
YANDEX_CLIENT_SECRET=ВАШ_CLIENT_SECRET_ИЗ_ШАГА_1
EOF
```

### 2.4 Инициализация базы данных

```bash
flask init-db
```

## Шаг 3: Настройка Gunicorn (WSGI сервер)

Создайте файл для запуска Gunicorn:

```bash
cat > /var/www/yandex-direct-mcp/wsgi.py << 'EOF'
from app import app

if __name__ == "__main__":
    app.run()
EOF
```

Создайте systemd service:

```bash
sudo nano /etc/systemd/system/yandex-direct-mcp.service
```

Содержимое файла:

```ini
[Unit]
Description=Yandex Direct MCP Flask API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/yandex-direct-mcp
Environment="PATH=/var/www/yandex-direct-mcp/venv/bin"
ExecStart=/var/www/yandex-direct-mcp/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:8000 wsgi:app

[Install]
WantedBy=multi-user.target
```

Запустите сервис:

```bash
sudo systemctl daemon-reload
sudo systemctl start yandex-direct-mcp
sudo systemctl enable yandex-direct-mcp
sudo systemctl status yandex-direct-mcp
```

## Шаг 4: Настройка Nginx

Создайте конфигурацию Nginx:

```bash
sudo nano /etc/nginx/sites-available/direct.jmagency.ru
```

Содержимое:

```nginx
server {
    listen 80;
    server_name direct.jmagency.ru;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    client_max_body_size 10M;
}
```

Активируйте конфигурацию:

```bash
sudo ln -s /etc/nginx/sites-available/direct.jmagency.ru /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Шаг 5: Настройка SSL с Let's Encrypt

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d direct.jmagency.ru
```

## Шаг 6: Проверка работы

1. Откройте браузер: https://direct.jmagency.ru
2. Нажмите "Login with Yandex"
3. Авторизуйтесь через Яндекс
4. Скопируйте полученный secret_code

## Для пользователей

### Как получить API ключ:

1. Перейдите на https://direct.jmagency.ru
2. Нажмите "Login with Yandex"
3. Авторизуйтесь через свой Яндекс аккаунт (с доступом к Яндекс.Директ)
4. После успешной авторизации вы получите сообщение с вашим API ключом:
   ```
   Successfully authenticated as your-login. Your secret code is: XXXxxxXXXxxx
   ```
5. Скопируйте этот ключ

### Использование в Jenova AI или Claude Desktop:

Добавьте в конфигурацию MCP:

```json
{
  "mcpServers": {
    "yandex-direct": {
      "command": "python",
      "args": ["/path/to/server.py"],
      "env": {
        "DIRECT_API_URL": "https://direct.jmagency.ru",
        "DIRECT_API_KEY": "ВАШ_API_КЛЮЧ_ПОЛУЧЕННЫЙ_НА_ШАГЕ_4"
      }
    }
  }
}
```

## Мониторинг и логи

```bash
# Просмотр логов Flask приложения
sudo journalctl -u yandex-direct-mcp -f

# Просмотр логов Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Перезапуск сервиса после изменений
sudo systemctl restart yandex-direct-mcp
```

## Обновление кода

```bash
cd /var/www/yandex-direct-mcp
git pull origin yandex-direct-mcp-server
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart yandex-direct-mcp
```

## Безопасность

1. **Backup базы данных** (содержит OAuth токены):
   ```bash
   cp /var/www/yandex-direct-mcp/database.db /var/backups/database-$(date +%F).db
   ```

2. **Ограничение доступа к файлам**:
   ```bash
   sudo chown -R www-data:www-data /var/www/yandex-direct-mcp
   sudo chmod 600 /var/www/yandex-direct-mcp/.env
   sudo chmod 600 /var/www/yandex-direct-mcp/database.db
   ```

3. **Firewall**:
   ```bash
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw allow 22/tcp
   sudo ufw enable
   ```

## Troubleshooting

### Ошибка "Invalid client_id"
- Проверьте правильность CLIENT_ID в `.env`
- Убедитесь, что в Яндекс.OAuth указан правильный Redirect URI

### Ошибка при OAuth
- Проверьте, что у приложения есть доступ к Яндекс.Директ
- Убедитесь, что пользователь имеет аккаунт в Яндекс.Директ

### API возвращает 401
- Проверьте, что secret_code правильный
- Проверьте, что токен в БД не истек

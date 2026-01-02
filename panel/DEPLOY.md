# Deployment Info

## Server Access
```
SSH: ssh jacov9bb@jacov9bb.beget.tech
```

## Production URL
```
https://direct.jmagency.ru
```

## Deploy Commands
```bash
# Connect to server
ssh jacov9bb@jacov9bb.beget.tech

# Go to project directory
cd ~/yandex-direct-panel

# Pull latest changes
git pull origin main

# Restart app (touch passenger_wsgi.py to restart)
touch passenger_wsgi.py
```

## Files to update manually (not in git)
- `.env` - environment variables (API keys)
- `database.db` - SQLite database

# Deployment Info

## Server Access
```
SSH: ssh jacov9bb@jacov9bb.beget.tech
```

## Production URL
```
https://direct.jmagency.ru
```

## Project Path on Server
```
~/direct.jmagency.ru/public_html/
```

## Deploy Commands (rsync method)
```bash
# Upload agent folder
rsync -avz panel/agent/ jacov9bb@jacov9bb.beget.tech:~/direct.jmagency.ru/public_html/agent/

# Upload templates
rsync -avz panel/templates/ jacov9bb@jacov9bb.beget.tech:~/direct.jmagency.ru/public_html/templates/

# Upload requirements
rsync -avz panel/requirements.txt jacov9bb@jacov9bb.beget.tech:~/direct.jmagency.ru/public_html/

# Restart app
ssh jacov9bb@jacov9bb.beget.tech "touch ~/direct.jmagency.ru/public_html/passenger_wsgi.py"
```

## Files to update manually (not in git)
- `.env` - environment variables (API keys)
- `database.db` - SQLite database

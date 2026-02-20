# Backend Deployment Guide

**Stack:** Django (ASGI) + Gunicorn + UvicornWorker + Nginx + Redis +
systemd\
**OS:** Ubuntu 20.04 / 22.04 / 24.04

------------------------------------------------------------------------

## 1. Server Requirements

-   Ubuntu VPS
-   Python 3.10+ (tested with 3.11)
-   Nginx
-   Redis
-   (Optional) PostgreSQL / MySQL (depends on project)
-   A domain pointing to the server (A record)

------------------------------------------------------------------------

## 2. Expected Project Structure

``` bash
/var/www/service_provider/
├── core/
├── manage.py
├── requirements.txt
├── static/
├── media/
└── env/
```

**ASGI Entry:**

``` bash
core.asgi:application
```

------------------------------------------------------------------------

## 3. Install System Packages

``` bash
sudo apt update && sudo apt upgrade -y

sudo apt install -y   python3-pip python3-venv python3-dev   nginx ufw redis-server
```

If using PostgreSQL:

``` bash
sudo apt install -y postgresql postgresql-contrib libpq-dev
```

------------------------------------------------------------------------

## 4. Upload Project & Create Virtual Environment

``` bash
sudo mkdir -p /var/www/service_provider
sudo chown -R $USER:$USER /var/www/service_provider
cd /var/www/service_provider
```

``` bash
python3 -m venv env
source env/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

------------------------------------------------------------------------

## 5. Environment Variables (.env)

Create file:

``` bash
nano /var/www/service_provider/.env
```

Example:

``` env
DJANGO_SETTINGS_MODULE=core.settings
SECRET_KEY=change-this-secret
DEBUG=0
ALLOWED_HOSTS=example.com,www.example.com
DATABASE_URL=postgres://user:password@127.0.0.1:5432/dbname
REDIS_URL=redis://127.0.0.1:6379/0
```

------------------------------------------------------------------------

## 6. Django Setup

``` bash
cd /var/www/service_provider
source env/bin/activate

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser  # optional
```

------------------------------------------------------------------------

## 7. Redis Setup

``` bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
sudo systemctl status redis-server
```

Test:

``` bash
redis-cli ping
# Should return: PONG
```

------------------------------------------------------------------------

## 8. systemd Service (Gunicorn + Uvicorn)

Create service file:

``` bash
sudo nano /etc/systemd/system/service_provider.service
```

Paste (edit **User** and paths if needed):

``` ini
[Unit]
Description=Service Provider (Django ASGI) - Gunicorn with UvicornWorker
After=network.target redis-server.service
Wants=redis-server.service

[Service]
Type=simple

User=backend_dev
Group=www-data
WorkingDirectory=/var/www/service_provider

Environment="DJANGO_SETTINGS_MODULE=core.settings"
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/var/www/service_provider/.env

ExecStart=/var/www/service_provider/env/bin/gunicorn core.asgi:application   -k uvicorn.workers.UvicornWorker   --workers 4   --threads 2   --bind 0.0.0.0:8001   --timeout 60   --graceful-timeout 30   --keep-alive 5   --max-requests 2000   --max-requests-jitter 200   --access-logfile -   --error-logfile -   --log-level info

Restart=always
RestartSec=3
LimitNOFILE=65535

StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable and start:

``` bash
sudo systemctl daemon-reload
sudo systemctl enable service_provider
sudo systemctl start service_provider
sudo systemctl status service_provider
```

Logs:

``` bash
sudo journalctl -u service_provider -f
```

------------------------------------------------------------------------

## 9. Nginx Setup (Reverse Proxy)

``` bash
sudo systemctl enable nginx
sudo systemctl start nginx
sudo ufw allow 'Nginx Full'
sudo ufw reload
```

Create config:

``` bash
sudo nano /etc/nginx/sites-available/service_provider
```

Paste (change domain and paths):

``` nginx
server {
    listen 80;
    server_name example.com www.example.com;

    client_max_body_size 50M;

    location /static/ {
        alias /var/www/service_provider/static/;
    }

    location /media/ {
        alias /var/www/service_provider/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_redirect off;
    }
}
```

Enable site:

``` bash
sudo ln -s /etc/nginx/sites-available/service_provider /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

------------------------------------------------------------------------

## 10. SSL (HTTPS) with Certbot (Recommended)

``` bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d example.com -d www.example.com
```

Test auto-renew:

``` bash
sudo certbot renew --dry-run
```

------------------------------------------------------------------------

## 11. Common Commands

Restart backend:

``` bash
sudo systemctl restart service_provider
```

Check status:

``` bash
sudo systemctl status service_provider
```

Live logs:

``` bash
sudo journalctl -u service_provider -f
```

Reload Nginx:

``` bash
sudo nginx -t
sudo systemctl reload nginx
```

------------------------------------------------------------------------

## 12. Troubleshooting

### 502 Bad Gateway

``` bash
sudo systemctl status service_provider
sudo journalctl -u service_provider -n 200
```

### Static files not loading

``` bash
python manage.py collectstatic --noinput
```

Check Nginx `alias` paths.

### Permission issues

``` bash
sudo chown -R backend_dev:www-data /var/www/service_provider
```

------------------------------------------------------------------------

## 13. Information Required from Developer

-   Environment variables list (`.env`)
-   Domain names
-   Database credentials
-   Any background workers (Celery/cron)
-   Storage configuration (local/S3/etc)

------------------------------------------------------------------------

**End of Documentation**

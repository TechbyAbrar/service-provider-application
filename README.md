# 🧠 Service Provider AI Web App – Backend API

Production-ready **Django REST API backend** for a service provider platform with AI-ready architecture, subscription management, secure authentication, and scalable deployment.

🔗 **GitHub Repository**: https://github.com/TechbyAbrar/service-provider-application.git
🎨 **Figma Design**: https://figma.com/design/ufJoTHr0YxIGtH0FP6evJQ/johnas_stefano%7C%7Cservice-provider-website
🌐 **Live Link**: *(Add your production URL here)*

---

## 📌 Overview

This project is a **scalable backend system** designed for a service provider platform where users can:

* register and manage accounts
* subscribe to services
* interact with platform features
* integrate with AI-driven workflows (future-ready)

The system follows a **modular, production-oriented architecture** with strong focus on:

* authentication flexibility
* observability (logging)
* deployment readiness
* SaaS scalability

---

## 🧠 Core Features

* 🔐 JWT Authentication (SimpleJWT)
* 👤 Custom User Model (`account.User`)
* 🔑 Multi-login backend (email / phone / username)
* 📦 Subscription System
* 💳 Stripe Payment Integration
* 📧 Email Notifications (SMTP)
* 📊 Structured Logging (access + error logs)
* ⚡ Static file serving with WhiteNoise
* 🌐 CORS-enabled API
* 📡 API documentation (drf-spectacular)
* 🧾 Custom exception handling

---

## 🏗️ Architecture Overview

Client (Web / Mobile)
↓
Frontend (Figma-based UI)
↓
Django REST API (Backend)
↓
-

| Auth Layer (Custom Backend + JWT)      |
| Subscription & Billing Module          |
| Supply Chain / Service Logic           |
| Exception Handling Layer               |
| Logging & Monitoring                   |
------------------------------------------

```
    ↓
```

PostgreSQL Database
↓
External Services:

* Stripe API
* SMTP Email Server

---

## ⚙️ Tech Stack

| Category     | Technology            |
| ------------ | --------------------- |
| Language     | Python 3.11+          |
| Framework    | Django 5.2.x          |
| API          | Django REST Framework |
| Auth         | Simple JWT            |
| Database     | PostgreSQL            |
| Static Files | WhiteNoise            |
| Logging      | Timed Rotating Logs   |
| API Docs     | drf-spectacular       |
| Payments     | Stripe API            |

---

## 📁 Project Structure

```text id="sp-struct"
core/
account/
privacy/
supplychain/
subscription/

media/
staticfiles/
logs/

manage.py
requirements.txt
README.md
```

---

## 🔐 Authentication System

Supports flexible login via:

* email
* phone
* username

### JWT Configuration

* Access Token: 15 days
* Refresh Token: 30 days
* Bearer authentication

---

## 💳 Subscription & Payment Flow

1. User selects subscription
2. Backend creates Stripe session
3. User completes payment
4. System validates via webhook
5. Access granted

---

## 📊 Logging System

Logs stored in `/logs/`:

* `access.log` → request logs
* `error.log` → error tracking

### Features

* Daily rotation
* 7-day retention
* Separate handlers for access & errors

---

## 📡 API Documentation

```text id="sp-api"
/api/schema/swagger-ui/
```

---

## 🌐 Environment Configuration

Create `.env` file:

```env id="sp-env"
SECRET_KEY=your-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com

DATABASE_URL=postgres://user:password@host:port/dbname

EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password

STRIPE_SECRET_KEY=your-secret
STRIPE_PUBLIC_KEY=your-public
STRIPE_WEBHOOK_SECRET=your-webhook
```

---

## 🚀 Installation & Setup

```bash id="sp-install"
git clone https://github.com/TechbyAbrar/service-provider-application.git
cd service-provider-application

python -m venv env
source env/bin/activate

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

---

## 🚀 Production Deployment (ASGI)

Run backend with **Gunicorn + Uvicorn workers**:

```bash id="sp-gunicorn"
gunicorn core.asgi:application \
  -k uvicorn.workers.UvicornWorker \
  --workers 4 \
  --threads 2 \
  --bind 0.0.0.0:8001 \
  --timeout 60 \
  --graceful-timeout 30 \
  --keep-alive 5 \
  --max-requests 2000 \
  --max-requests-jitter 200 \
  --access-logfile - \
  --error-logfile - \
  --log-level info
```

---

## ⚡ Redis (Optional / Future Scaling)

```bash id="sp-redis"
redis-server
```

Can be used for:

* caching
* background jobs
* scaling architecture

---

## 🧩 Systemd Service (Production)

Create service file:

```bash id="sp-service"
sudo nano /etc/systemd/system/service_provider.service
```

Then:

```bash id="sp-service2"
sudo systemctl daemon-reload
sudo systemctl enable service_provider
sudo systemctl start service_provider
sudo systemctl status service_provider
```

---

## 🌐 Nginx Reverse Proxy

Install Nginx:

```bash id="sp-nginx"
sudo apt install nginx -y
```

Create config:

```bash id="sp-nginx2"
sudo nano /etc/nginx/sites-available/service_provider
```

Key setup:

* proxy to Gunicorn (port 8001)
* serve static/media files
* enable websocket headers

Enable config:

```bash id="sp-nginx3"
sudo ln -s /etc/nginx/sites-available/service_provider /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🖼️ Screenshots

```md id="sp-img"
![Dashboard](assets/images/dashboard.png)
```

---

## 🧪 Future Improvements

* AI integration (LLM / automation)
* Background jobs (Celery)
* Redis caching layer
* Multi-tenant SaaS architecture
* Rate limiting & throttling
* Docker deployment
* Monitoring (Prometheus / Grafana)

---

## 🔐 Security Notes

* Store `SECRET_KEY` in `.env`
* Avoid `DEBUG=True` in production
* Restrict `ALLOWED_HOSTS`
* Limit CORS origins
* Use HTTPS (SSL via Nginx)

---

## 🤝 Contribution

Pull requests are welcome.

---

## 📄 License

MIT License

---

## 👨‍💻 Author

**Abrar (TechbyAbrar)**
Backend Engineer | Django | FastAPI | System Design | AI Systems

🔗 GitHub: https://github.com/TechbyAbrar

# 🏋️ IronLog — Gym Progress Tracker

Dark-themed, mobile-first gym tracker built with Django 4, Bootstrap 5, and SQLite.
Supports multiple users with full authentication.

## Features
- **Multi-user** — register/login, all data is private per user
- **Mobile-first** — bottom nav bar, card-based sets on mobile, responsive at every breakpoint
- **Workout sessions** — date, day of week, target muscle groups, notes
- **Exercise tracking** — add exercises with smart quick-add per muscle group
- **Set logging** — weight (kg/lbs), reps, notes — auto-saved on change
- **Dashboard** — stats and muscle group frequency breakdown
- **Profile page** — update email, change password

---

## Run Locally

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Open: **http://127.0.0.1:8000**

---

## Deploy to Railway

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/ironlog.git
git push -u origin main
```

### 2. Create Railway project
1. Go to https://railway.com → **New Project → Deploy from GitHub repo**
2. Select your repository

### 3. Generate domain
Settings → Networking → **Generate Domain**

### 4. Set environment variables
| Key | Value |
|-----|-------|
| `SECRET_KEY` | a long random string |
| `DEBUG` | `False` |

Railway auto-runs migrations and starts gunicorn via `railway.json`. ✅

---

## Project Structure
```
gymtracker/
├── manage.py
├── requirements.txt
├── railway.json
├── .gitignore
├── gymtracker/
│   ├── settings.py
│   └── urls.py
└── tracker/
    ├── models.py        — WorkoutSession (user FK), Exercise, SetLog
    ├── views.py         — Auth views + session CRUD + AJAX API
    ├── urls.py
    ├── migrations/
    └── templates/tracker/
        ├── base.html              — Sidebar + mobile bottom nav
        ├── login.html
        ├── register.html
        ├── profile.html
        ├── dashboard.html
        ├── session_list.html
        ├── session_detail.html    — Desktop table + mobile cards
        ├── session_form.html
        └── session_confirm_delete.html
```

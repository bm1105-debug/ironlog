# 🏋️ IronLog — Gym Progress Tracker

A dark-themed, full-featured gym workout tracker built with Django 4, Bootstrap 5, and SQLite.

## Features
- Log workout sessions with date, day of week, and target muscle groups
- Add exercises with smart quick-add suggestions per muscle group
- Track sets: weight (kg/lbs), reps, and notes — auto-saved inline
- Dashboard with stats and muscle group breakdown
- Full workout history grouped by month

---

## 🖥️ Run Locally

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Open: http://127.0.0.1:8000

---

## 🚀 Deploy to Railway

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
2. Select your repository — Railway auto-detects Django and builds

### 3. Generate a public URL
Settings → Networking → **Generate Domain**

### 4. Set environment variables
In Railway dashboard → your service → **Variables**:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | a long random secret string |
| `DEBUG` | `False` |

Railway will auto-run migrations and collectstatic on every deploy via `railway.json`.

---

## Project Structure
```
gymtracker/
├── manage.py
├── requirements.txt
├── railway.json          ← Railway deploy config
├── .gitignore
├── gymtracker/           ← Django project config
│   ├── settings.py
│   └── urls.py
└── tracker/              ← Main app
    ├── models.py         ← WorkoutSession, Exercise, SetLog
    ├── views.py          ← Page views + AJAX API
    ├── urls.py
    ├── migrations/
    └── templates/tracker/
```

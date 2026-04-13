# QUIZSCENDENCE — Getting Started

## Prerequisites
- Python 3.10+
- pip

---

## 1. Clone the repo and go to the server folder
```bash
git clone <repo-url>
cd 42_ft_transcendence/server
```

## 2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

## 3. Install dependencies
```bash
pip install -r requirements.txt
```

## 4. Set up the .env file
```bash
cp .env.example .env
```
Then open `.env` and fill in your own values. By default the project runs on **SQLite** — no database setup needed. To use PostgreSQL, uncomment `USE_POSTGRES=1` and make sure the DB credentials are correct.

## 5. Run migrations
```bash
python manage.py migrate
```

## 6. Create a superuser (for the admin panel)
```bash
python manage.py createsuperuser
```

## 7. Start the server
```bash
python manage.py runserver
```

---

## Useful URLs
| Page | URL |
|---|---|
| Admin panel | http://127.0.0.1:8000/admin/ |
| API docs (Swagger) | http://127.0.0.1:8000/api/docs/ |
| Questions API | http://127.0.0.1:8000/game/questions/ |
| Users API | http://127.0.0.1:8000/account/users/ |

---

## Notes
- Questions are managed exclusively through the **admin panel** — use the superuser account you created in step 6.
- A `UserProfile` is created automatically whenever a new user registers.
- Avatar uploads are stored in `server/media/avatars/`.

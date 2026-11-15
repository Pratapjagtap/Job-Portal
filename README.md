# Job-Portal

A Flask-based job portal application.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and set a unique `SECRET_KEY` and your database settings.
4. Set `INITIAL_ADMIN_PASSWORD` before the first run to create the admin account.
5. Start the app with `python run.py`.

The app uses MySQL by default. Set `DATABASE_URL` to use another SQLAlchemy-supported database. The sample personas use demo credentials and should only be used for local development.

## Deploy on Render

- Leave **Root Directory** blank.
- Set **Build Command** to `pip install -r requirements.txt`.
- Set **Start Command** to `gunicorn --bind 0.0.0.0:$PORT run:app`.
- Configure `SECRET_KEY`, `DATABASE_URL`, and `INITIAL_ADMIN_PASSWORD` in the Render environment.
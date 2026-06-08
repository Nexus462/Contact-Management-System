@echo off
REM ─────────────────────────────────────────────
REM Contactify — One-Command Setup Script (Windows)
REM ─────────────────────────────────────────────

echo 📦 Installing dependencies...
pip install -r requirements.txt

echo.
echo 🗄️  Running database migrations...
python manage.py makemigrations contacts
python manage.py migrate

echo.
echo ✅ Setup complete!
echo.
echo ▶️  Start the server with:
echo     python manage.py runserver
echo.
echo 🌐 Then open: http://127.0.0.1:8000
echo.
echo 👤 Optionally create a superuser for /admin:
echo     python manage.py createsuperuser

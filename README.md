# FolioCraft — Portfolio & Resume Builder
Internship task **PY-MC-005** · Django 4.x · MySQL 8 · Bootstrap-free custom responsive CSS.

## Features
- Registration, login and logout
- Profile editor with photo, bio, contact and social links
- Multiple portfolio records and public/private visibility
- Skills with proficiency levels
- Project showcase with images, tech stack, GitHub and live links
- Experience, education, certifications and testimonials
- Public shareable portfolio pages
- PDF resume generation with ReportLab
- Portfolio page-view tracking
- Django admin

## Windows installation
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```
Create the MySQL database and user (change the password):
```sql
CREATE DATABASE portfolio_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'portfolio_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON portfolio_db.* TO 'portfolio_user'@'localhost';
FLUSH PRIVILEGES;
```
Edit `.env` and set `DB_PASSWORD`, then:
```powershell
python manage.py makemigrations builder
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
Open http://127.0.0.1:8000/

## Routes
`/` home · `/register/` · `/login/` · `/dashboard/` · `/portfolio/new/` · `/portfolio/<id>/` editor · `/p/<slug>/` public portfolio · `/portfolio/<id>/resume.pdf` PDF · `/admin/`

## Important
This is a functional starter implementation; run migrations and test all workflows in your own environment before submission. Analytics currently counts public portfolio page views only, not detailed engagement. Uploaded files are stored locally in `media/`. For production, set a strong `SECRET_KEY`, `DEBUG=False`, correct `ALLOWED_HOSTS`, HTTPS, production-grade media storage and database backups. Never commit `.env`.

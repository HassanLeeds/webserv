# Remove all migrations and database
python manage.py reset_db  # Requires django-extensions
python manage.py makemigrations
python manage.py migrate

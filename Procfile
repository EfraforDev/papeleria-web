web: gunicorn Papeleria_web.wsgi --log-file -
release: python manage.py migrate && python manage.py collectstatic --noinput
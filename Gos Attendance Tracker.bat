@echo off
echo ***************
echo * Updating... *
echo ***************
git pull

echo.
echo ******************************
echo * Installing dependencies... *
echo ******************************
python -m pip install -r requirements.txt

echo.
echo *************************
echo * Migrating database... *
echo *************************
python manage.py migrate

echo.
echo **************************
echo * Running application... *
echo **************************
python manage.py runserver

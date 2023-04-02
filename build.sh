#!/usr/bin/env bash
# exit on error
set -o exit

pip install -r requirements.txt

python manage.py collectstatics --no-input
python manage.py migrate
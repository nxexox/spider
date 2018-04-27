enviroment=develop
venv=python3
settings=project.settings


install:
	[ -d $(venv) ] || virtualenv -p python3 $(venv) && make pip_install
	mkdir logs

run:
	$(venv)/bin/python manage.py runserver 0.0.0.0:8001

migrate:
	$(venv)/bin/python manage.py makemigrations
	$(venv)/bin/python manage.py migrate
	$(venv)/bin/python manage.py migrate --run-syncdb

pip_install:
	$(venv)/bin/pip install -r requirements.txt

pep8:
	# $(venv)/bin/prospector

test:
	$(venv)/bin/py.test apps/ -s

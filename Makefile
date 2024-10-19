

init.python:
	pip install pip --upgrade
	pip install poetry
	poetry install

init.airflow:
	cd airflow_dags
	export AIRFLOW_HOME=$(pwd)
	airflow standalone

init: init.python init.airflow
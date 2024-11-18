# Scalable For-You-Page

This is a demonstration of my implementation of developing an algorithm for ranking content based on their potential of positively engaging with said content. 

# Technical Details

1. Here we will use `dask` to orchestrate the data processing, model hyperparameter tuning, and model inference.
2. We will also demonstrate how to use `terraform` to define the infrastructure in the cloud.
3. We will also assume `SQL` as the database for storing the data. For organization, we will use `sqlalchemy` to interact with the database.
4. We will use `airflow` to orchestrate the data processing pipeline.

As a note, for local development, we will use `docker` to containerize the development environment. 
In the cloud, we would use native cloud services to orchestrate the data processing pipeline.
    1. A cluster to distribute the data processing (e.g. `dataproc` in GCP or `ECS` in AWS).
    2. A managed database service (e.g. `RDS` in AWS or `Cloud SQL` in GCP).
    3. A managed workflow service (e.g. `Cloud Composer` in GCP or `Managed Airflow` in AWS).


# Example Runbook

1. Start the postgres service and the object bucket storage service.
2. Execute psql commands to create the mlflow schema (i.e. `CREATE SCHEMA mlflow_schema`)
3. Initiate the mlflow server
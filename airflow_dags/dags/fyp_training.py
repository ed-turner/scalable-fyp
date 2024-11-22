
import boto3

from airflow import DAG
from airflow.providers.amazon.aws.operators.ecs import EcsRunTaskOperator

boto_session = boto3.Session()
ssm = boto_session.client("ssm")

existing_cluster_name = ssm.get_parameter(Name="/fyp/ecs/cluster_name")["Parameter"]["Value"]
existing_task_definition = ssm.get_parameter(Name="/fyp/ecs/task_definition")["Parameter"]["Value"]
log_group_name = ssm.get_parameter(Name="/fyp/ecs/log_group")["Parameter"]["Value"]
existing_cluster_subnets = ssm.get_parameter(Name="/fyp/vpc/private_subnets")["Parameter"]["Value"].split(",")

with DAG(
    "fyp_training",
    schedule_interval="@daily",
    default_args={
        "owner": "airflow",
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
    },
    catchup=False,
) as dag:

    build_train_dataset = EcsRunTaskOperator(
        dag=dag,
        task_id="build-train-dataset",
        cluster=existing_cluster_name,
        task_definition=existing_task_definition,
        overrides={
            "containerOverrides": [
                {
                    "name": "build_train_dataset",
                    "command": ["python", '-m', 'fyp.data.pipeline'],
                },
            ],
        },
        network_configuration={"awsvpcConfiguration": {"subnets": existing_cluster_subnets}},
        awslogs_group=log_group_name,
        awslogs_region="us-east-1",
        awslogs_stream_prefix=f"ecs/build_train_dataset",
    )

    train_ml = EcsRunTaskOperator(
        dag=dag,
        task_id="train-model",
        cluster=existing_cluster_name,
        task_definition=existing_task_definition,
        overrides={
            "containerOverrides": [
                {
                    "name": "train_model",
                    "command": ["python", '-m', 'fyp.ml.train'],
                },
            ],
        },
        network_configuration={"awsvpcConfiguration": {"subnets": existing_cluster_subnets}},
        awslogs_group=log_group_name,
        awslogs_region="us-east-1",
        awslogs_stream_prefix=f"ecs/train_model",
    )

    build_train_dataset >> train_ml

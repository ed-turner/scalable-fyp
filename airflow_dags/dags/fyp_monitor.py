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
    "fyp_inference",
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

    monitor_ml = EcsRunTaskOperator(
        dag=dag,
        task_id="monitor-model",
        cluster=existing_cluster_name,
        task_definition=existing_task_definition,
        overrides={
            "containerOverrides": [
                {
                    "name": "monitor_model",
                    "command": ["python", '-m', 'fyp.ml.monitor'],
                },
            ],
        },
        network_configuration={"awsvpcConfiguration": {"subnets": existing_cluster_subnets}},
        awslogs_group=log_group_name,
        awslogs_region="us-east-1",
        awslogs_stream_prefix=f"ecs/monitor_model",
    )

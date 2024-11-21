
from airflow import DAG
from airflow.providers.amazon.aws.operators.ecs import EcsRunTaskOperator

# this should be a ssm parameter
existing_cluster_name = "existing_cluster_name"

existing_task_definition = "existing_task_definition"

# this should be a ssm parameter
log_group_name = "log_group_name"

# this should be a ssm parameter
existing_cluster_subnets = ["subnet-12345678", "subnet-87654321"]

with DAG(
    "fyp_inference",
    schedule_interval=None,
    default_args={
        "owner": "airflow",
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
        "retries": 1,
    },
    catchup=False,
) as dag:

    inference_ml = EcsRunTaskOperator(
        dag=dag,
        task_id="inference-model",
        cluster=existing_cluster_name,
        task_definition=existing_task_definition,
        overrides={
            "containerOverrides": [
                {
                    "name": "inference_model",
                    "command": ["python", '-m', 'fyp.ml.inference'],
                },
            ],
        },
        network_configuration={"awsvpcConfiguration": {"subnets": existing_cluster_subnets}},
        awslogs_group=log_group_name,
        awslogs_region="us-east-1",
        awslogs_stream_prefix=f"ecs/inference_model",
    )

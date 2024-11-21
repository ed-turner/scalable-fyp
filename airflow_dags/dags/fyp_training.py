
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
    "fyp_training",
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

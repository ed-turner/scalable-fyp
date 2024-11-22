"""
This module contains the inference functions for the machine learning models.
"""
import logging
import argparse
from datetime import UTC, datetime

import numpy as np

from distributed import Client, LocalCluster

import dask.dataframe as dd

from sqlalchemy import create_engine
import mlflow

from fyp.settings import Settings
from fyp.data.db.queries import define_inference_data_query

logger = logging.getLogger()
settings = Settings()

parser = argparse.ArgumentParser()

parser.add_argument("--execution_timestamp", type=str, required=True, default=lambda: datetime.now(UTC).isoformat())

args = parser.parse_args()

engine = create_engine(settings.DB_URI)
mlflow.set_tracking_uri(settings.MLFLOW_URI)

filter_string = "name = 'xgb_ranker'"
results = mlflow.search_registered_models(filter_string=filter_string, max_results=1)

logger.info("Fetching the model")
model = mlflow.sklearn.load_model(f"models:/xgb_ranker/{results[0].latest_versions[0]}")

with LocalCluster() as cluster:
    with Client(cluster):
        ddf: dd.DataFrame = dd.read_sql_query(
        define_inference_data_query(args.execution_timestamp),
        con=settings.DB_URI,
        index_col="rn",
        params={
            "sslmode": "require",
            "options": f"-csearch_path%3D{settings.DATA_SOURCE_SCHEMA}"
        }
        )

        result_ddf = ddf.groupby("user_id").apply(
        lambda df: df.assign(rank=np.argsort(model.predict(df)))
        )

        result_ddf.to_sql(
        result_ddf,
        "fyp",
            uri=settings.DB_URI,
            schema=settings.ML_PREDICTIONS_SCHEMA,
            if_exists="replace",
            parallel=True
        )
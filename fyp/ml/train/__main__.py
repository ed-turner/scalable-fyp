"""
This module contains the training scripts for the machine learning models.
"""
import logging

import pandas as pd
from sqlalchemy import create_engine
import mlflow

from fyp.settings import Settings
from ..models.utils import train_model

logger = logging.getLogger()
settings = Settings()

engine = create_engine(settings.DB_URI)
mlflow.set_tracking_uri(settings.MLFLOW_URI)

mlflow.set_experiment("Ranking Model")

with engine.begin() as conn:
    df = pd.read_sql_table("training_data", con=conn, schema=settings.DATA_INTERNAL_RANKING_SCHEMA)


train_model(data=df.drop("label", axis=1), labels=df["label"], group_col="group")

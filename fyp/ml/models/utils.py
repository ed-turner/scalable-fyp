"""
This module contains utility functions for the machine learning models.
"""

import mlflow

import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import GroupKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from xgboost.sklearn import XGBRanker


def define_model_pipeline() -> Pipeline:
    """
    Define the model pipeline.

    :return:
    """

    # Define the column transformer.
    column_transformer = ColumnTransformer(
        transformers=[
            ('textual', TfidfVectorizer(), 'content'),
            (
                'categorical_dynamic',
                OneHotEncoder(handle_unknown='ignore'),
                [
                    'viewer_gender', 'creator_gender',
                    'viewer_ethnicity', 'creator_ethnicity',
                ]
            ),
            (
                'categorical_static_moy',
                OneHotEncoder(categories=[range(1, 13)]*4),
                [
                  'viewer_birthdate_month', 'creator_birthdate_month',
                  'viewed_at_month', 'created_at_month'
                ]
            ),
            (
                'categorical_static_hod',
                OneHotEncoder(categories=[range(24)]*2),
                [
                    'viewed_at_hour', 'created_at_hour'
                ]
            ),
            (
                'categorical_static_dow',
                OneHotEncoder(categories=[range(7)]*2),
                [
                    'viewed_at_dow', 'created_at_dow',
                ]
            ),
            (
                'numerical',
                'passthrough',
                [
                    'viewer_birthdate_year', 'creator_birthdate_year',
                ]
            )
            ]
    )

    return Pipeline(
        steps=[
            ('preprocessor', column_transformer),
            ('ranker', XGBRanker())
        ]
    )


def fit_model(data, labels, group_col: str, mlflow_uri: str, **params) -> dict[str, float]:
    """
    Fit the model.

    :param data:
    :param labels:
    :param group_col:
    :param mlflow_uri:
    :return:
    """

    groups = data[group_col]

    group_kfold = GroupKFold(n_splits=5)

    model = define_model_pipeline()
    model.set_params(**params)

    mlflow.set_tracking_uri(mlflow_uri)

    with mlflow.start_run() as run:
        scores = cross_val_score(model, data, labels, groups=groups, cv=group_kfold)

        avg_loss = np.mean(scores)
        var_loss = np.var(scores)

        mlflow.log_params(params, run_id=run.info.run_id)
        mlflow.log_metric("avg_ncdg", avg_loss, run_id=run.info.run_id)
        mlflow.log_metric("ncdg_variance", var_loss, run_id=run.info.run_id)

    return {
        'loss': -avg_loss,
        'loss_variance': var_loss
    }

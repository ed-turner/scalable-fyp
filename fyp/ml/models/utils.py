"""
This module contains utility functions for the machine learning models.
"""

import mlflow

from hyperopt import hp, STATUS_OK, STATUS_FAIL, fmin, tpe, Trials

from mlflow.models import infer_signature

import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import make_scorer, ndcg_score
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


def define_parameter_space():
    return {
        "preprocessor__textual__ngram_range_max": hp.uniform("preprocessor__textual__ngram_range_max", low=1, high=3),
        "preprocessor__textual__ngram_range_min": hp.uniform("preprocessor__textual__ngram_range_min", low=1, high=3),
        "preprocessor__textual__binary": hp.choice("preprocessor__textual__binary", [True, False]),
        "preprocessor__textual__norm": hp.choice("preprocessor__textual__norm", ['l1', 'l2', None]),
        "preprocessor__textual__use_idf": hp.choice("preprocessor__textual__use_idf", [True, False]),
        "preprocessor__textual__smooth_idf": hp.choice("preprocessor__textual__smooth_idf", [True, False]),
        "preprocessor__textual__sublinear_tf": hp.choice("preprocessor__textual__sublinear_tf", [True, False]),
        "ranker__n_estimators": hp.uniform("ranker__n_estimators", low=100, high=1000),
        "ranker__learning_rate": hp.loguniform("ranker__learning_rate", low=1e-14, high=1.0),
        "ranker__max_depth": hp.uniform("ranker__max_depth", low=0, high=20),
        "ranker__subsample": hp.uniform("ranker__subsample", 0.5, 1.0),
        "ranker__colsample_bytree": hp.uniform("ranker__colsample_bytree", 0.5, 1.0),
        "ranker__colsample_bylevel": hp.uniform("ranker__colsample_bylevel", 0.5, 1.0),
        "ranker__colsample_bynode": hp.uniform("ranker__colsample_bynode", 0.5, 1.0),
        "ranker__reg_lambda": hp.loguniform("ranker__reg_lambda", low=1e-14, high=1e14),
        "ranker__reg_alpha": hp.loguniform("ranker__reg_alpha", low=1e-14, high=1e14),
        "ranker__lambdarank_normalization": hp.choice("ranker__lambdarank_normalization", [True, False]),
        "ranker__lambdarank_pair_method": hp.choice("ranker__lambdarank_pair_method", ["mean", "topk"]),
        "ranker__lambdarank_num_pair_per_sample": hp.loguniform("ranker__lambdarank_num_pair_per_sample", low=1, high=1e14),
        "ranker__lambdarank_bias": hp.choice(
            "ranker__lambdarank_bias",
            [
                {
                    "ranker__lambdarank_unbiased": True,
                    "ranker__lambdarank_bias_norm": hp.loguniform("ranker__lambdarank_bias_norm", low=1e-14, high=1e2)
                },
                {
                    "ranker__lambdarank_unbiased": False,
                }
            ]
                                             )
    }


def format_model_parameters(params: dict) -> dict:
    """
    This will format parameters

    :param params:
    :return:
    """

    if params['preprocessor__textual__ngram_range_min'] <= params['preprocessor__textual__ngram_range_max']:
        params['preprocessor__textual__ngram_range'] = (int(params.pop('preprocessor__textual__ngram_range_min')), int(params.pop('preprocessor__textual__ngram_range_max')))
    else:
        raise ValueError("The ngram range bounds do not make sense")

    params['ranker__max_depth'] = int(params['ranker__max_depth'])
    params['ranker__n_estimators'] = int(params['ranker__n_estimators'])

    params['ranker__lambdarank_num_pair_per_sample'] = int(params['ranker__lambdarank_num_pair_per_sample'])

    ranker__lambdarank_bias = params.pop("ranker__lambdarank_bias")

    params = {**params, **ranker__lambdarank_bias}

    return params


def fit_model(data, labels, group_col: str, **params) -> dict[str, float]:
    """
    Fit the model.

    :param data:
    :param labels:
    :param group_col:
    :return:
    """

    groups = data[group_col]

    group_kfold = GroupKFold(n_splits=2)

    try:
        model = define_model_pipeline()

        params = format_model_parameters(params)

        model.set_params(**params)

        scores = cross_val_score(
            model,
            data,
            labels,
            groups=groups,
            cv=group_kfold,
            scoring=make_scorer(score_func=ndcg_score, greater_is_better=True)
        )

        avg_loss = np.mean(scores)

        return {
            'loss': -avg_loss,
            "status": STATUS_OK
        }
    except Exception as e:
        return {
            'loss': np.inf,
            'status': STATUS_FAIL,
            'attachments': {
                'error': str(e)
            }
        }


def train_model(data, labels, group_col):

    def opt(params):
        return fit_model(
            data=data,
            labels=labels,
            group_col=group_col,
            **params
        )

    trials = Trials()

    with mlflow.start_run(tags={"runType": "hyperParamOptimize"}):
        best = fmin(
            fn=opt,
            space=define_parameter_space(),
            algo=tpe.suggest,
            trials=trials,
            max_evals=100
        )

    best = format_model_parameters(best)

    with mlflow.start_run(tags={"runType": "optimalTrain"}):
        model = define_model_pipeline()

        model.set_params(**best)

        model.fit(
            data, labels, groups=data[group_col]
        )

        signature = infer_signature(data, model.predict(data, groups=data[group_col]))

        mlflow.log_params(best)

        ranker_info: mlflow.models.model.ModelInfo = mlflow.sklearn.log_model(model, "xgb_ranker", signature=signature)

        mlflow.register_model(ranker_info.model_uri, name='xgb_ranker')

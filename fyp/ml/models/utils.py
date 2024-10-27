"""
This module contains utility functions for the machine learning models.
"""

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer

from xgboost.sklearn import XGBRanker


def define_model_pipeline(genders: list[str], ethnicities: list[str]):
    """
    Define the model pipeline.

    :return:
    """

    # Define the column transformer.
    column_transformer = ColumnTransformer(
        transformers=[
            ('textual', TfidfVectorizer(), 'content'),
            ('categorical__gender', OneHotEncoder(categories=genders), ['viewer_gender', 'creator_gender']),
            ('categorical__ethnicity', OneHotEncoder(categories=ethnicities), ['viewer_ethnicity', 'creator_ethnicity'])
            ]
    )

    return Pipeline(
        steps=[
            ('preprocessor', column_transformer),
            ('ranker', XGBRanker())
        ]
    )

"""
This module contains utility functions for the data pipeline.
"""

from sqlalchemy.engine import Engine

from ..db.tables import training_data
from ..db.queries import define_training_data_query


def execute_query(engine: Engine):
    """
    Execute the query against the database.

    :param engine:
    :return:
    """

    with engine.begin() as conn:
        conn.execute(
            training_data.insert().from_select(
                [
                    'user_id', 'content_id', 'viewed_at',
                    'created_at', 'content', 'label', 'group',
                    'viewer_gender', 'viewer_birthdate', 'viewer_ethnicity',
                    'creator_gender', 'creator_birthdate', 'creator_ethnicity'
                ]
                ,
                define_training_data_query()
            )
        )

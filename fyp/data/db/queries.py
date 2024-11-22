"""
This module contains the queries against the database.
"""
from sqlalchemy import select, and_, func, case
from .tables import (users, social_media_content, social_media_content_views,
                     social_media_content_likes, social_media_content_comments)


def define_training_data_query():
    """
    Define the query to retrieve the training data from the database.
    """
    comment_data = select([
        social_media_content.c.created_at.label('commented_at'),
        social_media_content_comments.c.parent_content_id.label('content_id'),
        social_media_content.c.creator_id.label('commented_by'),
    ]).select_from(
        social_media_content
    ).join(
        social_media_content_comments,
        social_media_content.c.id == social_media_content_comments.c.content_id
    ).cte('comment_data')

    label_data = select([
        social_media_content_views.c.content_id.label('content_id'),
        social_media_content_views.c.viewed_by.label('user_id'),
        social_media_content_views.c.viewed_at,
        comment_data.c.commented_at,
        social_media_content_likes.c.liked_at,
        users.c.gender.label("viewer_gender"),
        users.c.birthdate.label("viewer_birthdate"),
        users.c.ethnicity.label("viewer_ethnicity")
    ]).select_from(
        social_media_content_views
    ).join(
        comment_data,
        and_(
            social_media_content_views.c.content_id == comment_data.c.content_id,
            social_media_content_views.c.viewed_by == comment_data.c.commented_by
        ),
        isouter=True
    ).join(
        social_media_content_likes, and_(
            social_media_content_views.c.content_id == social_media_content_likes.c.content_id,
            social_media_content_views.c.viewed_by == social_media_content_likes.c.liked_by
        ),
        isouter=True
    ).join(
        users, users.c.id == social_media_content_views.c.viewed_by
    ).cte('label_data')

    groups = select([
        label_data.c.user_id,
        func.sum(func.count()).over().label('group')
        ]
    ).select_from(
        label_data
    ).group_by(
        label_data.c.user_id
    ).cte('groups')

    query = select([
        func.row_number().over().label('rn'),
        label_data.c.content_id,
        label_data.c.user_id,
        label_data.c.viewer_gender,
        label_data.c.viewer_birthdate,
        label_data.c.viewer_ethnicity,
        users.c.gender.label("creator_gender"),
        users.c.birthdate.label("creator_birthdate"),
        users.c.ethnicity.label("creator_ethnicity"),
        social_media_content.c.content,
        social_media_content.c.created_at,
        case(
            [
                (and_(label_data.c.liked_at.isnot(None), label_data.c.commented_at.isnot(None)), 1),
                (label_data.c.liked_at.isnot(None), 2),
                (label_data.c.commented_at.isnot(None), 3),
            ],
            else_=4
        ).label('label'),
        groups.c.group
    ]
    ).select_from(
        label_data
    ).join(
        social_media_content, social_media_content.c.id == label_data.c.content_id
    ).join(
        users, users.c.id == social_media_content.c.creator_id
    ).join(
        groups, groups.c.user_id == label_data.c.user_id
    )

    return query


def define_inference_data_query(execution_timestamp: str):
    """
    Define the query to retrieve the inference data from the database.
    """
    creator_query = select([
        social_media_content.c.content,
        social_media_content.c.created_at,
        social_media_content.c.id.label('content_id'),
        users.c.id.label('user_id'),
        users.c.gender.label("creator_gender"),
        users.c.birthdate.label("creator_birthdate"),
        users.c.ethnicity.label("creator_ethnicity"),
        ]).select_from(
            social_media_content
        ).join(
            users, users.c.id == social_media_content.c.creator_id
        ).cte('creator_data')

    universe_query = select([
        social_media_content.c.id.label('content_id'),
        users.c.id.label('user_id')
    ]).select_from(
        social_media_content
    ).join(
        users, True
    ).cte('universe_data')

    viewer_query = select([
        social_media_content_views.c.viewed_at,
        social_media_content.c.id.label('content_id'),
        users.c.id.label('user_id'),
        users.c.gender.label("viewer_gender"),
        users.c.birthdate.label("viewer_birthdate"),
        users.c.ethnicity.label("viewer_ethnicity"),
        ]).select_from(
            social_media_content
        ).join(
            social_media_content_views, social_media_content_views.c.content_id == social_media_content.c.id
        ).join(
            users, users.c.id == social_media_content_views.c.viewed_by
        ).cte('viewer_data')

    query = (select([
        func.row_number().over().label('rn'),
        viewer_query.c.content_id,
        viewer_query.c.user_id,
        viewer_query.c.viewer_gender,
        viewer_query.c.viewer_birthdate,
        viewer_query.c.viewer_ethnicity,
        viewer_query.c.viewed_at,
        creator_query.c.creator_gender,
        creator_query.c.creator_birthdate,
        creator_query.c.creator_ethnicity,
        creator_query.c.content,
        creator_query.c.created_at,
        ]
    ).select_from(
        universe_query
    ).join(
      viewer_query, and_(
            viewer_query.c.content_id == universe_query.c.content_id,
            viewer_query.c.user_id == universe_query.c.user_id
        ), isouter=True
    ).join(
        creator_query, creator_query.c.content_id == viewer_query.c.content_id
    )).where(
        creator_query.c.created_at > execution_timestamp
    ).where(
        viewer_query.c.viewed_at is None
    )

    return query


def define_analysis_query(execution_timestamp: str):
    """
    Define the query to retrieve the analysis data from the database.
    """
    comment_data = select([
        social_media_content.c.created_at.label('commented_at'),
        social_media_content_comments.c.parent_content_id.label('content_id'),
        social_media_content.c.creator_id.label('commented_by'),
    ]).select_from(
        social_media_content
    ).join(
        social_media_content_comments,
        social_media_content.c.id == social_media_content_comments.c.content_id
    ).cte('comment_data')

    label_data = select([
        social_media_content_views.c.content_id.label('content_id'),
        social_media_content_views.c.viewed_by.label('user_id'),
        social_media_content_views.c.viewed_at,
        comment_data.c.commented_at,
        social_media_content_likes.c.liked_at,
    ]).select_from(
        social_media_content_views
    ).join(
        comment_data,
        and_(
            social_media_content_views.c.content_id == comment_data.c.content_id,
            social_media_content_views.c.viewed_by == comment_data.c.commented_by
        ),
        isouter=True
    ).join(
        social_media_content_likes, and_(
            social_media_content_views.c.content_id == social_media_content_likes.c.content_id,
            social_media_content_views.c.viewed_by == social_media_content_likes.c.liked_by
        ),
        isouter=True
    ).cte('label_data')

    query = select([
        func.row_number().over().label('rn'),
        label_data.c.content_id,
        label_data.c.user_id,
        case(
            [
                (and_(label_data.c.liked_at.isnot(None), label_data.c.commented_at.isnot(None)), 1),
                (label_data.c.liked_at.isnot(None), 2),
                (label_data.c.commented_at.isnot(None), 3),
            ],
            else_=4
        ).label('label')
    ]
    ).select_from(
        label_data
    ).join(
        social_media_content, social_media_content.c.id == label_data.c.content_id
    ).where(
        social_media_content.c.created_at > execution_timestamp
    )

    return select([
        query.c.user_id,
        query.c.label,
        func.count().label('count')
    ]).select_from(
        label_data
    ).group_by(
        label_data.c.user_id
    )
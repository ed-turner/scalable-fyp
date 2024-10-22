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

    query = select([
        label_data.c.content_id,
        label_data.c.user_id,
        label_data.c.viewed_at,
        label_data.c.commented_at,
        label_data.c.liked_at,
        label_data.c.viewer_gender,
        label_data.c.viewer_birthdate,
        label_data.c.viewer_ethnicity,
        users.c.gender.label("creator_gender"),
        users.c.birthdate.label("creator_birthdate"),
        users.c.ethnicity.label("creator_ethnicity"),
        social_media_content.c.creator_id,
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
    ]
    ).select_from(
        label_data
    ).join(
        social_media_content, social_media_content.c.id == label_data.c.content_id
    ).join(
        users, users.c.id == social_media_content.c.creator_id
    )

    return query

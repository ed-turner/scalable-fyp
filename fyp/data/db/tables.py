

from sqlalchemy import Table, MetaData, Column, Integer, String, DateTime, ForeignKey

metadata = MetaData()

users = Table(
    'users',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String, unique=True),
    Column('gender', String),
    Column('birthdate', DateTime),
    Column('ethnicity', String)
)


social_media_content = Table(
    'social_media_content',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('creator_id', ForeignKey('users.id')),
    Column('created_at', DateTime),
    Column('content', String)
)

social_media_content_comments = Table(
    'social_media_content_comments',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('content_id', ForeignKey('social_media_content.id')),
    Column('parent_content_id', ForeignKey('social_media_content.id'))
)

social_media_content_likes = Table(
    'social_media_content_likes',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('content_id', ForeignKey('social_media_content.id')),
    Column('liked_by', ForeignKey('users.id')),
    Column('liked_at', DateTime)
)

social_media_content_views = Table(
    'social_media_content_views',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('content_id', ForeignKey('social_media_content.id')),
    Column('viewed_by', ForeignKey('users.id')),
    Column('viewed_at', DateTime)
)

user_relates_with_user = Table(
    'user_relates_with_user',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', ForeignKey('users.id')),
    Column('other_user_id', ForeignKey('users.id')),
    Column('relates_at', DateTime),
    Column('relation_type', String)
)


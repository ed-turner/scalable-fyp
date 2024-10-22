"""
This module contains the ORM classes for the database.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    gender = Column(String)
    birthdate = Column(String)
    ethnicity = Column(String)


class SocialMediaContent(Base):
    __tablename__ = 'social_media_content'

    id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime)
    content = Column(String)


class SocialMediaContentComment(Base):
    __tablename__ = 'social_media_content_comments'

    id = Column(Integer, primary_key=True)
    content_id = Column(Integer, ForeignKey('social_media_content.id'))
    parent_content_id = Column(Integer, ForeignKey('social_media_content.id'))


class SocialMediaContentLike(Base):
    __tablename__ = 'social_media_content_likes'

    id = Column(Integer, primary_key=True)
    content_id = Column(Integer, ForeignKey('social_media_content.id'))
    liked_by = Column(Integer, ForeignKey('users.id'))
    liked_at = Column(DateTime)


class SocialMediaContentView(Base):
    __tablename__ = 'social_media_content_views'

    id = Column(Integer, primary_key=True)
    content_id = Column(Integer, ForeignKey('social_media_content.id'))
    viewed_by = Column(Integer, ForeignKey('users.id'))
    viewed_at = Column(DateTime)


class UserBlockUser(Base):
    __tablename__ = 'user_block_user'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    blocked_user_id = Column(Integer, ForeignKey('users.id'))

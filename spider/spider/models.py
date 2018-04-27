"""
Модели, для сохранения в базе данных инфы с паука.

"""
import logging

from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

import config


logger = logging.getLogger(__name__)

engine = create_engine(config.DATABASE.get('LINK', ''), echo=True)
Base = declarative_base()


class Site(Base):
    """
    Модель сайта.

    """
    __tablename__ = "site"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    domain = Column(String)
    use_ssl = Column(Boolean)

    def __init__(self, name, domain, use_ssl):
        """
        Создание модели.

        :param str name:
        :param str domain:
        :param bool use_ssl:

        """
        self.name = name
        self.domain = domain
        self.use_ssl = use_ssl


class Link(Base):
    """
    Ссылка на сайт.

    """
    __tablename__ = "link"

    id = Column(Integer, primary_key=True)
    link = Column(String)
    size = Column(Integer)

    site_id = Column(Integer, ForeignKey("site.id"))
    site = relationship("Site", backref=backref("links", order_by=id))

    def __init__(self, link, size):
        """
        Создание ссылки на сайт.

        :param str link: Ссылка без домена.
        :param int size: Размер страницы в байтах.

        """
        self.link = link
        self.size = size


# create tables
Base.metadata.create_all(engine)

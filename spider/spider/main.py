"""
Главный файл паука.

"""
import logging

from sqlalchemy.orm import sessionmaker

from pool import PoolWorkers, PollRenewableWorkers, NewPoolWorkers
import config


logger = logging.getLogger(__name__)


class App(object):
    """
    Класс приложения.

    """
    def __init__(self):
        self.pool = PoolWorkers(config.WORKERS)

    def start(self):
        pass

    def __run(self):
        pass


if __name__ == "__main__":
    App().start()


# from models import Site, Link, engine


# Session = sessionmaker(bind=engine)
# session = Session()
#
# # Create an artist
# new_site = Site("Yandex", "http://ya.ru", True)
# new_site.links = [Link("?query=opa", 300)]
#
# # add more albums
# more_links = [Link("?query=search", 350), Link("?query=query", 500), Link("?query=12313", 500)]
#
# new_site.links.extend(more_links)
#
# # Add the record to the session object
# session.add(new_site)
# # commit the record the database
# session.commit()
#
# # Add several artists
# session.add_all([Site("Google", "https://google.com", True)])
#
# session.commit()

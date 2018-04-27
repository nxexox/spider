"""
Задачи по парсингу сайтов.

"""
import logging

from urllib.parse import urlparse

import requests


logger = logging.getLogger(__name__)


def get_link_info(link):
    """
    Формирует и возвращает полезные данные из ссылки.

    :param str link: Ссылка, из которой еобходимо достать данные.

    :return: Словарь с данными по ссылке.
    :rtype: dict

    """
    try:
        parse_uri = urlparse(link)
        return {
            'domain': parse_uri.netloc,
            'use_ssl': True if parse_uri.scheme == 'https' else False
        }
    except Exception as e:
        logger.error(e, exc_info=True)

    return {}


def get_page_info(link):
    """
    Получение информации о странице.

    :param link: Информация о ссылке.

    :return: Словарь с данными по странице.
    {"content-type": str, "content-length": int, "status": int}
    :rtype: dict

    """
    try:
        response = requests.get(link)
        return {
            "content-type": response.headers.get("Content-Type", None),
            "content-length": response.headers.get("Content-Length", 0),
            "status": response.status_code
        }
    except Exception as e:
        logger.error(e, exc_info=True)

    return {}

"""
Настройки проекта.

"""

from envinroments import DefaultEnvironmentDict as __DefaultEnvironmentDict


__ENV_DICT = __DefaultEnvironmentDict()
__ENV_DICT.load()


# Кол-во воркеров для паука.
WORKERS = __ENV_DICT.get('WORKERS', 1)

# Настройки логера.


# Настройки базы данных.
DATABASE = {
    'HOST': __ENV_DICT.get('POSTGRES_HOST', '0.0.0.0'),
    'PORT': __ENV_DICT.get('POSTGRES_PORT', 5432),
    'DB': __ENV_DICT.get('POSTGRES_DB'),
    'USER': __ENV_DICT.get('POSTGRES_USER', 'postgres'),
    'PASSWORD': __ENV_DICT.get('POSTGRES_PASSWORD'),
    'LINK': 'postgresql://{HOST}:{PORT}/{DB}?user={USER}&password={PASSWORD}'.format(
        HOST=__ENV_DICT.get('POSTGRES_HOST', '0.0.0.0'),
        PORT=__ENV_DICT.get('POSTGRES_PORT', 5432),
        DB=__ENV_DICT.get('POSTGRES_DB'),
        USER=__ENV_DICT.get('POSTGRES_USER', 'postgres'),
        PASSWORD=__ENV_DICT.get('POSTGRES_PASSWORD')
    )
}

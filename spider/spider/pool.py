"""
Пул воркеров. Полное управление и контроль воркерами.

"""
import logging
import threading
from functools import partial
from multiprocessing import Pool, cpu_count, Queue, Process


logger = logging.getLogger(__name__)


class Worker(Process):
    """
    Свой процесс. Тут мы вызываем команду.

    """
    def __init__(self, queue, pk, *args, **kwargs):
        super(Worker, self).__init__(*args, **kwargs)
        self.queue = queue
        self.pk = pk

    def run(self):
        logger.info('Worker `{}` started.'.format(self.pk))
        for data in iter(self.queue.get, None):
            try:
                command, args, kwargs = data.get('command', None), data.get('args', []), data.get('kwargs', {})
                if command:
                    logger.info('Worker `{}`. Start task:`{}`, args: `{}`, kwargs: `{}`.'.format(
                        self.pk, command, args, kwargs
                    ))
                    result = command(*args, **kwargs)
                    logger.info('Worker `{}`. End task:`{}`, args: `{}`, kwargs: `{}, result: `{}`.'.format(
                        self.pk, command, args, kwargs, result
                    ))
                else:
                    logger.error('Worker `{}` error. Command not found in `{}`.'.format(self.pk, data))
            except:
                logger.error(
                    'Exception for worker `{}` command: `{}`. More information: '.format(self.pk, data), exc_info=True
                )

        logger.info('Worker `{}` finished.'.format(self.pk))


class NewPoolWorkers(object):
    """
    Ручной пул воркеров.
    Простая общая очередь на несколько воркеров.

    """
    def __init__(self, count=None):
        self.__count_workers = count if count else cpu_count() - 1
        self.__queue = Queue()
        self.__workers = {
            key + 1: Worker(self.__queue, key + 1) for key in range(count)
        }
        for key, val in self.__workers.items():
            val.start()

    def apple_async(self, target, *args, **kwargs):
        """
        Добавление задачи для асинхронного выполнения.

        :param target: Зачада.
        :type target: function

        """
        logger.info('Add task for pool. Task: `{}`, args: `{}`, kwargs: `{}`.'.format(target, args, kwargs))
        self.__queue.put({"command": target, "args": args, "kwargs": kwargs})

    def close(self):
        """
        Убиваем все воркеры и сам пул. Предварительно ждем завершения задачи.

        """
        logger.info('Poll workers shutdown started.')
        for _ in self.__workers.keys():
            self.__queue.put(None)
        for key, val in self.__workers.items():
            val.join()
            val.terminate()
        logger.info('Pool workers shutdown finished.')


class RenewableWorker(Process):
    """
    Одноразовый воркер.

    """
    def __init__(self, pk, end_callback=None, error_callback=None, *args, **kwargs):
        """
        Одноразовый воркер.

        :param int pk: ID воркера.
        :param function end_callback: Функция, выполняющаяся после успешного выполнения задачи.
        :param function error_callback: Функция, выполняющаяся после ошибки в задаче.

        """
        super(RenewableWorker, self).__init__(*args, **kwargs)
        self.pk = pk
        self.end_callback = end_callback
        self.error_callback = error_callback

    def run(self):
        logger.info('Worker `{}` start.'.format(self.pk))
        try:
            result = super(RenewableWorker, self).run()
        except Exception as e:
            logger.error('Worker `{}` exception.'.format(self.pk), exc_info=True)
            return self.error_callback(e) if self.error_callback else None

        logger.info('Worker `{}` end.'.format(self.pk))
        return self.end_callback(result) if self.end_callback else result


class PollRenewableWorkers(object):
    """
    Пул возобновляемых воркеров.
    На каждую задачу создается процесс, после выполнения задачи процесс грохается.

    """
    def __init__(self, count=None):
        self.__count_workers = count if count else cpu_count() - 1
        self.__workers = {}

    def apple_async(self, target, end_callback=None, error_callback=None, *args, **kwargs):
        """
        Добавление задачи для асинхронного выполнения.

        :param target: Зачада.
        :param end_callback: Функция, которая выполнится после успешного завершения задачи.
        :param error_callback: Функция, которая выполнится после ошибки во время задачи.
        :type target: function
        :type end_callback: function
        :type error_callback: function

        """
        process = RenewableWorker(
            self.__create_pk(),
            end_callback=end_callback,
            error_callback=error_callback,
            target=target,
            args=args,
            kwargs=kwargs
        )
        self.__workers[process.pk] = process
        self.__workers[process.pk].start()

    def close(self):
        """
        Завершает все процессы безопасно.

        """
        for key, val in self.__workers.items():
            logger.info("Worker `{}` served his own. It's time to retire.".format(key))
            val.terminate()
            val.join()
            logger.info("Worker `{}` retired. Bye Bye.".format(key))

    def __create_pk(self):
        """
        Формирует и возвращает PK воркера.

        :return: PK для нового воркера.
        :rtype: int

        """
        pks = sorted(list(self.__workers.keys()), reverse=True)
        return pks[0] + 1 if pks else 1


class PoolWorkers(object):
    """
    Пул воркеров, с которым работаем.
    Стандартный пул, без наработок.

    """
    def __init__(self, count=None):
        self.__count_workers = count if count else cpu_count() - 1
        self.__pool = Pool(self.__count_workers)

    @property
    def state(self):
        try:
            return self.__pool._state
        except Exception as e:
            logger.error(e, exc_info=True)
            return None

    def apple_async(self, target, end_callback=None, error_callback=None, *args, **kwargs):
        """
        Добавление задачи для асинхронного выполнения.

        :param target: Зачада.
        :param end_callback: Функция, которая выполнится после успешного завершения задачи.
        :param error_callback: Функция, которая выполнится после ошибки во время задачи.
        :type target: function
        :type end_callback: function
        :type error_callback: function

        """
        self.__pool.apply_async(target, args=args, kwds=kwargs, callback=end_callback, error_callback=error_callback)

    def join(self):
        """
        Ждем выполнения всех воркеров.

        """
        return self.__pool.join()

    def close(self):
        """
        Убиваем все воркеры и сам пул. Предварительно ждем завершения задачи.

        """
        self.__pool.close()


class Timer(threading.Thread):
    """
    Свой таймер, отдельным потоком. Несмотря на GIL, должно работать.

    """
    def __init__(self, handler, args=None, kwargs=None, interval=20 * 60, deffer=False):
        """
        Делаем атрибуты для таймера.

        :param handler: Функция, которую надо вызывать каждые interval секунд.
        :param args: Позиционные аргументы для функции.
        :param kwargs: Именованные аргументы для функции.
        :param interval: Интервал, через который надо вызывать handler.
        :param deffer: Отложенный запуск.
        :type handler: func
        :type args: tuple
        :type kwargs: dict
        :type interval: int
        :type deffer: bool

        """
        threading.Thread.__init__(self)
        self.__finished = threading.Event()
        self.__interval = float(interval)
        args, kwargs = args if args else (), kwargs if kwargs else {}
        self.__handler = partial(handler, *args, **kwargs)
        self.__deffer = deffer

    def set_interval(self, interval):
        """
        Изменить интервал, на который будет засыпать поток.

        """
        self.__interval = interval

    def shutdown(self):
        """
        Останавливаем поток.

        """
        self.__finished.set()

    def __run_deffer(self):
        """
        Запускает отложенный таймер. Т.е. первый раз функция выполнится через interval секунд.

        """
        while True:
            if self.__finished.isSet():
                return

            # Спим, пока не пройдет интервал или сдохнет процесс.
            self.__finished.wait(self.__interval)

            self.__handler()

    def __run_normal(self):
        """
        Запускает нормальный таймер. Т.е. первый раз функция выполнится сразу.

        """
        while True:
            if self.__finished.isSet():
                return

            self.__handler()

            # Спим, пока не пройдет интервал или сдохнет процесс.
            self.__finished.wait(self.__interval)

    def run(self):
        """
        Сам запуск задачи.

        """
        logger.info('Start timer target `{}` interval `{}`'.format(self.__handler, self.__interval))
        while True:
            try:
                if self.__deffer:
                    self.__run_deffer()
                else:
                    self.__run_normal()
            except:
                logger.error(
                    'In timer exception target `{}` interval `{}`.'.format(self.__handler, self.__interval),
                    exc_info=True
                )
                if self.__finished.isSet():
                    break
            if self.__finished.isSet():
                break

            logger.info('Timer target `{}` interval `{}` rerun.'.format(self.__handler, self.__interval))

        logger.info('End timer target `{}` interval `{}`.'.format(self.__handler, self.__interval))

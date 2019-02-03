# -*- coding: utf-8 -*-
import requests
import threading
import time
from scales import logger
from . import api
from requests.exceptions import ConnectionError


class ThreadedPOST(threading.Thread):
    '''класс для открытия потока с отправлением шкалы другому серверу'''

    def __init__(self, host_queue, data, type_of_request):
        super(ThreadedPOST, self).__init__()
        self.host_queue = host_queue
        self.data = data
        self.host = self.host_queue.get()
        self.type_of_request = type_of_request
        self._return = None

    def run(self):
        self.process(self.host, self.data, self.type_of_request)

    def process(self, host, data, type_of_request, retries=0):
        '''
        процесс отправляет GET или POST запрос серверу
        :args 
            data json from request
            type_of_request arr
                [имя запроса, действие]
                    действие: scales для шкал, count для подсчета
            retries int
                количество повторов попытки
        '''
        if retries > 2:
            logger.error('Cant connect: hostname - {}'.format(self.host))
            self._return = {self.host: None}
        else:
            try:
                if type_of_request[0] == 'POST':
                    self._return = requests.post(
                        self.host + '/scales/change_scale', data=self.data,timeout=1)
                if type_of_request[0] == 'GET':
                    if type_of_request[1] == 'scales':
                        r = requests.get(
                            self.host + '/scales/get_scales_local', timeout=1)
                    if type_of_request[1] == 'count':
                        r = requests.get(
                            self.host + '/scales/count_status_local', timeout=1)
                    self._return = r.json()
            except ConnectionError as e:
                # logger.error(type(e).__name__)
                logger.error(
                    'Error in thread: hostname: {}, error: cant connect'.format(self.host))
                retries += 1
                self.process(self.host, self.data,
                             self.type_of_request, retries)
            except Exception as e:
                logger.error(
                    'Error in thread: hostname: {}, error: {}'.format(self.host, str(e)))
                self._return = {self.host: None}

    def join(self):
        super(ThreadedPOST, self).join()
        return self._return

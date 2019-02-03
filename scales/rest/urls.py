# -*- coding: utf-8 -*-
from flask import request, jsonify, make_response, abort, render_template
from flask import current_app as app
from scales import db, models, logger
from datetime import datetime
from sqlalchemy.exc import InvalidRequestError, IntegrityError
from werkzeug.exceptions import BadRequest
import os
from flask import json
from . import api
import queue as Queue
from .thread_class import ThreadedPOST
from sqlalchemy import func

#TODO актуализацию
#TODO 74 строчку на 5/15/100 машинах
#TODO 238 строчку на 5/15/100 машинах

def threaded_ask_servers(type_of_request):
    '''
    функция для создания потоков подключения к остальным серверам
    :args
        arr тип реквеста, что хочется
            ['GET', 'scales'/'count']
            ['POST']
    '''
    host_queue = Queue.Queue()
    for host in app.config['NEIGHBOURS']:
        for ip in host.values():
            host_queue.put(''.join(ip))
    for i in range(0, host_queue.qsize()):
        conn_to_other_servers = ThreadedPOST(
            host_queue, request, type_of_request)
        conn_to_other_servers.start()
        return conn_to_other_servers.join()

def data_transform(request):
    '''
    функция чтобы работать как с данными из формы, так и с json объектами
    :args
        request data
    :return
        attr dict
    '''
    if request.json:
                var = {}
                var.update(request.json)
    elif request.data:
        var = json.loads(request.data)
    else:
        var = {'scale_name': request.form.get('scale_name'),
            'start': request.form.get('start'),
            'stop': request.form.get('stop'),
            'status': request.form.get('status')}
    return var

@api.route('/')
@api.route('/index')
def index():
    '''
    отдает клиенту index страницу с js скриптами
    '''
    return render_template('index.html')


@api.route('/scales/get_scales', methods=['GET'])
def get_scales():
    '''
    отдает все шкалы по GET запросу
    :return
        все шкалы что есть на сервере
    '''
    allScales = [get_scales_local().json, threaded_ask_servers(['GET', 'scales'])]
    # allScales.append(get_scales_local().json)
    # allScales.append(threaded_ask_servers(['GET', 'scales']))
    logger.info('requested all scales')
    return make_response(jsonify({"all scales from servers": allScales}), 200)


@api.route('/scales/get_scales_local', methods=['GET'])
def get_scales_local():
    '''
    отдает по GET запросу только шкалы, которые находятся на хосте
    '''
    scales = models.Scale.query.all()
    scalesArr = []
    for scale in scales:
        scalesArr.append(scale.as_dict())
    logger.info('requested all scales from localhost')
    return make_response(jsonify({app.config['HOST_NAME']: scalesArr}), 200)


@api.route('/scales/get_scale/<string:scale_name>', methods=['GET'])
def get_scale(scale_name):
    '''
    отдает одну шкалу
    :args 
        scale_name str
    :return
        шкала по имени
    '''
    scale = models.Scale.query.filter_by(scale_name=scale_name).first()
    if scale:
        logger.info('scale {} requested'.format(
            request.form.get('scale_name')))
        return make_response(jsonify({'scale': scale.as_dict()}), 200)
    else:
        logger.error('404 in get_scale')
        abort(404)


@api.route('/scales/create_scale', methods=['POST'])
def registrateScale():
    '''
    регистрирует новую шкалу
    :args
        json from post
    :return
        201 - успех
        400 - неверный формат данных
        500 - неудалось создать шкалу
    '''
    var = data_transform(request)
    try:
        scale = models.Scale(
            scale_name=var['scale_name'], status=0)
        db.session.add(scale)
        db.session.commit()
        logger.info('scale {} created'.format(var['scale_name']))
        return make_response(jsonify({'status': 'created'}), 201)
    except IntegrityError as e:
        logger.error(e)
        db.session.rollback()
        abort(400)
    except InvalidRequestError as e:
        logger.error(e)
        db.session.rollback()
        abort(400)
    except Exception as e:
        # logger.critical(type(e).__name__)
        logger.critical(e)
        db.session.rollback()
        abort(500)


@api.route('/scales/delete_scale', methods=['DELETE'])
def deleteScale():
    '''
    удаляет шкалу по имени
    :args
        json from delete
    :return
        200 - удалось удалить
        500 - неудалось удалить шкалу
    '''
    try:
        var = data_transform(request)
        scale = models.Scale.query.filter_by(scale_name=var['scale_name']).delete()
        db.session.commit()
        logger.info('scale {} deleted'.format(request.form.get('scale_name')))
        return make_response(jsonify({'status': True}), 200)
    except Exception as e:
        logger.critical(e)
        db.session.rollback()
        abort(500)


@api.route('/scales/change_scale', methods=['POST', 'PUT'])
def changeScale():
    '''
    функция обновления шкалы. при запросе POST просто обновляет локальную шкалу
    при запросе PUT - отсылает запрос на обновление другим хостам и обновляет локальную
    :args 
        json из POST или PUT запросов
    :return
        200 - в случае успеха
        400 - неверный формат данных
        500 - в случае ошибки базы данных
    '''
    def scale_update():
        '''
        функция отвечает за само обновление шкалы
        :return
            200 - удалось обновить
            400 - неверные данные
            500 - ошибка в обновлении данных
        '''
        try:
            # структуры ниже - для универсальной обработки как формы, так и чистых запросов
            var = data_transform(request)
            scaleToUpdate = models.Scale.query.filter_by(
                scale_name=var['scale_name']).first()
            flag = False
            if 'start' in var:
                scaleToUpdate.start = var['start']
                scaleToUpdate.status = 1
                flag = True
            if 'stop' in var:
                scaleToUpdate.stop = var['stop']
                scaleToUpdate.status = 2
                flag = True
            if 'status' in var:
                scaleToUpdate.status = var['status']
                flag = True
            if flag:
                db.session.commit()
                logger.info('scale {} changed'.format(
                    var['scale_name']))
                return make_response(jsonify({'status': True}), 202)
            else:
                logger.error('bad args in /changeScale')
                abort(400)
        except KeyError as e:
            logger.critical('no name of scale in change_scale')
            db.session.rollback()
            abort(400)
        except Exception as e:
            # logger.critical(type(e).__name__)
            logger.critical(e)
            db.session.rollback()
            abort(500)
    if request.method == 'POST':
        return scale_update()
    if request.method == 'PUT':
        threaded_ask_servers(['POST'])
        return scale_update()


@api.route('/scales/count_status', methods=['GET'])
def count_status():
    '''
    функция считает количество шкал на всех узлах по их статусу
    :return
        json внутри словарь с именем узлов и arr 
            arr [зарегестированные, запущенные, остановленные]
    '''
    allCount = [count_status_local().json,
                threaded_ask_servers(['GET', 'count'])]
    # allCount.append(count_status_local().json)
    # allCount.append(threaded_ask_servers(['GET', 'count']))
    logger.info('requested count scales from all servers')
    return make_response(jsonify({"counted scales from all servers": allCount}), 200)


@api.route('/scales/count_status_local', methods=['GET'])
def count_status_local():
    '''
    функция считает количество шкал на узле по их статусу
    :return
        json with arr 
            arr [зарегестированные, запущенные, остановленные]
    '''
    try:
        counted = db.session.query(func.count(
            models.Scale.scale_name).filter(models.Scale.status == 0), func.count(
            models.Scale.scale_name).filter(models.Scale.status == 1), func.count(
            models.Scale.scale_name).filter(models.Scale.status == 2))
        logger.info('requested count scales on localhost')
        return make_response(jsonify({app.config['HOST_NAME']: counted.first()}), 200)
    except Exception as e:
        db.session.rollback()
        logger.error('Error in count scales local: {}'.format(str(e)))
        abort(500)

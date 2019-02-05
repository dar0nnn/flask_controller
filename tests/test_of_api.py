# -*- coding: utf-8 -*-
import pytest
from scales import create_app, db
from scales.models import *
import json
import datetime

@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app('testing')
    testing_client = flask_app.test_client()
    ctx = flask_app.app_context()
    ctx.push()
    yield testing_client
    ctx.pop()


@pytest.fixture(scope='module')
def init_database():
    db.create_all()

    yield db
    db.session.close()
    db.drop_all()


def test_home_page(test_client):
    '''
    типо пинг
    '''
    response = test_client.get('/')
    assert response.status_code == 200

def test_create_scale(test_client, init_database):
    '''
    тест создания шкалы
    '''
    jsonData = {"scale_name":"qwerty_test"}
    response = test_client.post('/scales/create_scale', data=json.dumps(jsonData))
    assert response.status_code == 201
    assert {"status": "created"} == json.loads(response.data)
    response = test_client.post('/scales/create_scale')
    assert response.status_code == 400
    assert {'error': 'Bad request'} == json.loads(response.data)


def test_change_scale(test_client):
    '''
    меняем шкалу, POST и PUT запросики, разные данные
    '''
    jsonData = {"scale_name": "qwerty_test",
                "start": "2012-12-3", "stop": "2013-11-30", "status": 2}
    response = test_client.post('/scales/change_scale', data=json.dumps(jsonData))
    assert response.status_code == 202
    assert {'status': True} == json.loads(response.data)
    jsonData = {"start": "2012-12-3", "stop": "2013-11-30", "status": 2}
    response = test_client.post(
        '/scales/change_scale', data=json.dumps(jsonData))
    assert response.status_code == 400
    assert {'error': 'Bad request'} == json.loads(response.data)
    jsonData = {"scale_name": "qwerty_test",
                "start": "2012-12-4", "stop": "2013-11-23", "status": 2}
    response = test_client.put(
        '/scales/change_scale', data=json.dumps(jsonData))
    assert response.status_code == 202
    assert {'status': True} == json.loads(response.data)
    jsonData = {"start": "2012-12-3", "stop": "2013-11-30", "status": 2}
    response = test_client.put(
        '/scales/change_scale', data=json.dumps(jsonData))
    assert response.status_code == 400
    assert {'error': 'Bad request'} == json.loads(response.data)

def test_count_status(test_client):
    '''
    тест подсчета всех шкал с выключенным еще одним узлом
    '''
    response = test_client.get('scales/count_status')
    dataCheck = [{'conn center 1': [0, 0, 1]}]
    dataForCheck = list(json.loads(response.data).values())[0]
    assert response.status_code == 200
    assert True == any(item in dataForCheck for item in dataCheck)

def test_count_status_local(test_client):
    '''
    тест посчета шкал на локале
    '''
    response = test_client.get('/scales/count_status_local')
    assert response.status_code == 200
    assert {'conn center 1': [0, 0, 1]} == json.loads(response.data)

def test_get_scales(test_client):
    '''
    тест получения всех шкал с выключенным еще одним узлом
    '''
    response = test_client.get('/scales/get_scales')
    dataCheck = [{'conn center 1': [
        ["qwerty_test",  '2012-12-04 00:00:00', '2013-11-23 00:00:00', 2]]}]
    dataForCheck = list(json.loads(response.data).values())[0]
    assert response.status_code == 200
    assert True == any(item in dataForCheck for item in dataCheck)

def test_get_scales_local(test_client):
    '''
    тест получения шкал с локали
    '''
    response = test_client.get('/scales/get_scales_local')
    assert response.status_code == 200
    assert {'conn center 1': [
        ["qwerty_test",  '2012-12-04 00:00:00', '2013-11-23 00:00:00', 2]]} == json.loads(response.data)


def test_delete_scale(test_client, init_database):
    '''
    тест удаления шкалы
    '''
    jsonData = {'scale_name': 'qwerty_test'}
    response = test_client.delete('/scales/delete_scale', data=json.dumps(jsonData))
    assert response.status_code == 200
    assert {'status': True} == json.loads(response.data)




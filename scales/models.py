# -*- coding: utf-8 -*-
from scales import db
import datetime

# from sqlalchemy import Column, Integer, String, DateTime, SmallInteger

def roundTime(dt=None, roundTo=60):
   '''
   функция для округления времени
   '''
   if dt == None : dt = datetime.datetime.now()
   seconds = (dt.replace(tzinfo=None) - dt.min).seconds
   rounding = (seconds+roundTo/2) // roundTo * roundTo
   return dt + datetime.timedelta(0,rounding-seconds,-dt.microsecond)

def dateToString(atr_from_class):
    '''
    функция для json.dump что бы преобразовать дату в стринг
    :args
        атрибут класса объект
    :return
        str в случае datetime
        атрибут без изменений если не datetime
    '''
    if isinstance(atr_from_class, datetime.datetime):
        atr_from_class = roundTime(atr_from_class, roundTo=1)
        return atr_from_class.__str__()
    else:
        return atr_from_class


class Scale(db.Model):
    '''
    описание шкалы времени
    scale_name - имя шкалы
    start - время ее старта
    stop - время ее остановки
    status - статус шкалы для проверок и последующего отоброжения на схеме
    '''
    __tablename__ = 'scales'

    scale_name = db.Column(db.String(150), primary_key=True, nullable=False)
    start = db.Column(db.DateTime(), nullable=True)
    stop = db.Column(db.DateTime(), nullable=True)
    status = db.Column(db.SmallInteger(), default=0)

    def __init__(self, scale_name=None, start=None, stop=None, status=None):
        self.scale_name = scale_name
        self.start = start
        self.stop = stop
        self.status = status

    def as_dict(self):
       return [dateToString(getattr(self, c.name)) for c in self.__table__.columns]

    def __repr__(self):
        return '%r %r %r %r' % (self.scale_name, self.start, self.stop, self.status)

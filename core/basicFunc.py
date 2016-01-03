#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from collections.abc import Iterable
import random, copy
from numpy import array, sqrt, floor
from .basicVariable import *


class DataError(Exception): 
	'原始数据文件有静态检查可以发现的错误'
	pass

def randOccur(v): 
	if v == 0: 
		return False
	return v>random.randrange(100)

class Data():
	def __init__(self, data):
		for key, value in data.items(): 
			setattr(self, key, value)

def searchByProperty(dataList, propertyName, propertyValues): 
	if not isinstance(propertyValues, Iterable) or type(propertyValues) == str: 
		propertyValues = (propertyValues, )
	for data in dataList: 
		if getattr(data, propertyName) in propertyValues: 
			return data
	raise AttributeError(str(propertyValues)+' is not found')
	# return None

def searchByName(dataList, names): 
	return searchByProperty(dataList, 'name', names)

# def searchAllByProperty(dataList, propertyName, propertyValues): 
# 	resultList = []
# 	if not isinstance(propertyValues, Iterable) or type(propertyValues) == str: 
# 		propertyValues = (propertyValues, )
# 	for data in dataList: 
# 		if getattr(data, propertyName) in propertyValues: 
# 			resultList.append(data)
# 	return resultList

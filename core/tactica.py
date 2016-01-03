#! /usr/bin/env python3
# -*- coding: utf-8 -*-

__all__ = ['Tactica']

from .basicFunc import *

class Tactica(Data): 
	def __repr__(self): 
		return self.name

if __name__ == "__main__": 
	from os.path import *
	import json
	with open(join(dirname(__file__), 'dat2json', 'tactica.json'), 'r', encoding='utf8') as fp: 
		tacticaList = [Tactica(i) for i in json.load(fp)]
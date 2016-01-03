#! /usr/bin/env python3
# -*- coding: utf-8 -*-

__all__ = ['itemTypeList', 'Item']

from .basicFunc import *
from .skill import Skill

itemTypeList = ["片手", "両手", "射撃", "杖", "鞭", "爪", "盾", "鎧", "獣装", "法衣", "道具", "素材", "消耗"]

class Item(Data): 
	def __init__(self, data):
		Data.__init__(self, data)
		self.add = array((self.add["pow"], self.add["def"], self.add["spd"], self.add["mnd"]))
		self.skills = [Skill(**sk) for sk in self.attach]

	def getImg(self): 
		return (r'interface\item', self.image[0]+'.png')

if __name__ == "__main__": 
	from os.path import *
	import json
	with open(join(dirname(__file__), 'dat2json', 'item.json'), 'r', encoding='utf8') as fp: 
		itemList = [Item(i) for i in json.load(fp)]
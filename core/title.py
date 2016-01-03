#! /usr/bin/env python3
# -*- coding: utf-8 -*-

__all__ = ['Title']

from .basicFunc import *
from .skill import Skill

class Title(Data): 
	def __init__(self, data):
		Data.__init__(self, data)
		self.special = self.add["special"]
		self.add = array((self.add["pow"], self.add["def"], self.add["spd"], self.add["mnd"]))
		self.skill = Skill(**self.skill)
	def __repr__(self): 
		return self.name
	def display(self): 
		# string1 = {0:"←→", 1:"←　", 2:"　→"}[self.set]
		string1 = {0:"<-->", 1:"<-- ", 2:" -->"}[self.set]
		string2 = self.skill.display()
		ss1 = "{0}　{1:　<7}".format(string1, self.name)
		ss2 = "".join("{0: >4}".format("{0:+}".format(self.add[i])) for i in range(4))
		ss3 = "{0:　>3}　{1:　>1}　 {2: <7}".format(self.special, self.divine, string2)

		return ss1+ss2+ss3

if __name__ == "__main__": 
	from os.path import *
	import json
	with open(join(dirname(__file__), 'dat2json', 'title.json'), 'r', encoding='utf8') as fp: 
		titleList = [Title(i) for i in json.load(fp)]
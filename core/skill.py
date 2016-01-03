#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# __all__ = ['skillMaxValueDict', 'notAddableSkills', 'Skill']
__all__ = ['Skill', 'turnEndSkillDict', 'getRadiationDamage', 'getBlastDamageArray']

from collections import OrderedDict
from abc import ABCMeta

from numpy import empty

from .basicFunc import *
# skillMaxValueDict={
# 	"カブト割": 75, 
# 	"資源工面": 75, 
# 	"巨大体躯": 80, 
# 	"巨神体躯": 98, 
# 	"矮小体躯": 80, 
# 	"リカバリ": 100, 
# 	"特攻防御": 100, 
# 	"対術障壁": 100, 
# 	"対術結界": 100, 
# 	"戦術結界": 100, 
# 	"戦術障壁": 100, 
# 	"毒化攻撃": 50, 
# 	"麻痺攻撃": 2, 
# 	"自爆障壁": 100, 
# 	"自爆結界": 100
# }
# notAddableSkills = ["撃破金運"]

class SkillMeta(type): 
	def __init__(self, *args, **kwargs):
		self.__instanceDict = {}
		type.__init__(self, *args, **kwargs) 
	def __call__(self, name='', value=0): 
		if (name, value) not in self.__instanceDict: 
			self.__instanceDict[(name, value)] = type.__call__(self, name, value)
		return self.__instanceDict[(name, value)]

class Skill(metaclass=SkillMeta): 
	__slots__ = ('name', 'value')
	def __init__(self, name='', value=0):
		self.name = name
		self.value = value
	def __bool__(self): 
		return bool(self.name)
	def __repr__(self):
		return "Skill("+self.__str__()+')'
	def __str__(self): 
		if self.name: 
			if self.value == 0:
				return self.name
			else:
				return self.name+":"+str(self.value)
		else: 
			return '　'*4
	def display(self): 
		return '{: <8}'.format(str(self))
	def battleDisplay(self): 
		if self.name: 
			if self.value: 
				return '{}[{:>3}]'.format(self.name, self.value)
			else: 
				return self.name
		else: 
			return ''


class TurnEndAttribute(): 
	def __init__(self, radiation, blast, futile): 
		self.radiation = radiation
		self.blast = blast
		self.futile = futile

turnEndSkillDict = OrderedDict([
	('火', TurnEndAttribute('火炎放射', '大火炎陣', '火')), 
	('海', TurnEndAttribute('水流放射', '大水流陣', '海')), 
	('氷', TurnEndAttribute('氷撃放射', '大氷撃陣', '氷')), 
	('雷', TurnEndAttribute('雷撃放射', '大雷撃陣', '雷')), 
	('毒', TurnEndAttribute('毒気放射', '大毒気陣', '毒死')), 
	('神', TurnEndAttribute('神術放射', '大神術陣', '')), 
	('魔', TurnEndAttribute('魔術放射', '大魔術陣', ''))
])
	
class TurnEndDamage(): 
	def __init__(self): 
		for k in turnEndSkillDict: 
			setattr(self, k, 0)
	@classmethod
	def getMndEffect(cls, mnd1, mnd2): 
		return max(min(1+(mnd1-mnd2)/100/2, 1.5), 0.5)


class RadiationDamage(TurnEndDamage): 
	def __init__(self, tib, target): 
		TurnEndDamage.__init__(self)
		amplify = 1+tib.術式増幅/100
		for m in tib: 
			if m: 
				mndEffect = RadiationDamage.getMndEffect(m.status[3], target.status[3])
				for k, tea in turnEndSkillDict.items(): 
					radiation = m.getSkillSum(tea.radiation)/100*mndEffect*min(m.HP, 9999)*amplify
					exec('self.'+k+'+=radiation')


class BlastDamage(TurnEndDamage): 
	def __init__(self, m1, m2): 
		mndEffect = BlastDamage.getMndEffect(m1.status[3], m2.status[3])
		amplify = 1+m1.team.術式増幅/100
		for k, tea in turnEndSkillDict.items(): 
			blast = m1.getSkillSum(tea.blast)/100*mndEffect*min(m1.HP, 9999)*amplify
			setattr(self, k, blast)

class AbsorbDamage(TurnEndDamage): 
	pass

class ReflectDamage(TurnEndDamage): 
	pass

def getRadiationDamage(tib1, tib2): 
	target1 = tib2.targeted
	target2 = tib1.targeted
	radiationDamage1 = RadiationDamage(tib1, target1) if target1 else None
	radiationDamage2 = RadiationDamage(tib2, target2) if target2 else None
	return radiationDamage1, radiationDamage2

def getBlastDamageArray(tib1, tib2): 
	'每人对每人有一个字典，一共6*6'
	blastDamageArray1 = empty((6, 6), dtype=object)
	blastDamageArray2 = empty((6, 6), dtype=object)
	for i1, m1 in enumerate(tib1.members): 
		if m1: 
			for i2, m2 in enumerate(tib2.members): 
				if m2: 
					blastDamageArray1[i1, i2] = BlastDamage(m1, m2)
					blastDamageArray2[i2, i1] = BlastDamage(m2, m1)

	return blastDamageArray1, blastDamageArray2

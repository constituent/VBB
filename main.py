#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import json, sys, os
import copy
from itertools import chain
from os.path import *

from core import *

# 通关某难度之后，开启新功能：所有装备/称号的各族活性、指挥和弱体可以点击切换种族。还有各种特攻
# 最后的大BOSS，会复活比如9次，己方上过场的不能再上；或者血量乘10，我已经把计算物理和法术伤害及治疗时用的HP设成上限9999了
# 这样即使有几队能满结界也无所谓了
# 用钱付工资要1.5倍。再付不起工资的直接扣生命值


dataPath = join(dirname(__file__), 'data', 'json')

with open(join(dataPath, 'item.json'), 'r', encoding='utf8') as fp: 
	itemList = [Item(i) for i in json.load(fp)]
with open(join(dataPath, 'tactica.json'), 'r', encoding='utf8') as fp: 
	tacticaList = [Tactica(i) for i in json.load(fp)]
for index, tactica in enumerate(tacticaList): 
	tactica.index = index
with open(join(dataPath, 'title.json'), 'r', encoding='utf8') as fp: 
	titleList = [Title(i) for i in json.load(fp)]

itemDict = dict((key, []) for key in '片手 両手 射撃 杖 鞭 爪 盾 鎧 獣装 法衣 道具 素材'.split())
for item in itemList: 
	itemDict[{'消耗': '素材'}.get(item.type, item.type)].append(item)

# with open(join(dataPath, 'unit.json'), 'r', encoding='utf8') as fp: 
# 	unitBaseList = [UnitBase(i) for i in json.load(fp)]

def unitGenerator(): 
	for unitFile in os.listdir(join(dataPath, 'unit')): 
		with open(join(dataPath, 'unit', unitFile), 'r', encoding='utf8') as fp: 
			yield from json.load(fp)

unitBaseList = [UnitBase(i) for i in unitGenerator()]

unitBaseDict = dict((key, []) for key in '魔獣 亜人 兵卒 傭兵 聖職 妖精 造魔 悪魔 竜族 神族 倭国 不死 蟲族 勇者 女神'.split())
for index, unitBase in enumerate(unitBaseList): 
	unitBase.index = index
	unitBase.vb_id = 'm'+unitBase.image1[0][3: ]
	unitBaseDict[unitBase.type].append(unitBase)

for tactica in tacticaList: 
	tactica.titleList = []
tacticaDict = {t.name: t for t in tacticaList}
for title in titleList: 
	tactica = tacticaDict[title.arcana]
	tactica.titleList.append(title)
	title.tactica = tactica

def getBattle(background): 
	team1 = Team(0)
	for i, unitBase in enumerate(unitBaseList[: 6]): 
		unit = Unit(unitBase, level=200)
		team1.addMember(unit, i)
	# team1.addMember(Unit(unitBaseList[282], level=200, titles=(searchByName(titleList, '冬のナマズの'), 
	# 	searchByName(titleList, '斥候の')), items=(searchByName(itemList, 'ヴァルキュレイド'), 
	# 	searchByName(itemList, 'Ｓ弓矢アロー'))), 0)
		# searchByName(itemList, '武将胴丸'))), 0)
	team1.addMember(Unit(unitBaseList[8], level=200), 1)
	# team1.addMember(Unit(searchByName(unitBaseList, 'ケツアルカトル'), level=200), 1)
	team1.addMember(Unit(searchByProperty(unitBaseList, 'vb_id', 'm0281'), level=200), 1)
	
	team1.changeLeader(0)
	

	team2 = Team(0)
	# for i, unitBase in enumerate(unitBaseList[: 6]): 
	# 	unit = Unit(unitBase, level=200)
	# 	team2.addMember(unit, i)
	# team2.addMember(Unit(unitBaseList[14], level=200), 1)
	# team2[5].changeEquip(0, searchByName(itemList, 'エルヴン・ボウ'))
	# team2.addMember(Unit(searchByName(unitBaseList, 'ダンタリオン'), level=200), 1)

	# 魔神竜ウェルギウス
	# ガイアスクイーン
	# バハムート
	# ケツアルカトル
	# unit = Unit(searchByName(unitBaseList, 'ウルティマカノン'), level=300, levelLimited=False, enemyHardness=(5, 5))
	unit = Unit(searchByProperty(unitBaseList, 'vb_id', 'm2038'), level=300, levelLimited=False, enemyHardness=(5, 5))
	unit.maxHP *= 100
	team2.addMember(unit, 2)
	
	team1.fillHP(4)
	team2.fillHP(4)
	battle = Battle(team1, team2, background, MANUALBATTLE)
	# battle.tib1[0].unitInTeam.recovered = True
	# for as_ in AbnormalStatus.asStr: 
	# 	# 强行设异常，并不影响属性
	# 	setattr(battle.tib1[2].abnormalStatus, as_, 1)
	# 	setattr(battle.tib2[1].abnormalStatus, as_, 1)
	return battle

def getBattles(gameData, background): 
	team2 = Team(0)

	if gameData.teamList[9]: 
		team2 = gameData.teamList[9]
	else: 
		if gameData.moon == '光' and gameData.daylight: 
			ra = Unit(searchByName(unitBaseList, 'ラー'), level=300, levelLimited=False, enemyHardness=(5, 5))
			for i in range(6): 
				team2.addMember(copy.copy(ra), i)
			unit = Unit(searchByName(unitBaseList, 'ガイアスクイーン'), level=300, levelLimited=False, enemyHardness=(5, 5))
			unit.maxHP *= 10
			team2.addMember(unit, 3)
			team2.changeLeader(3)
		else: 
			titi = Unit(searchByName(unitBaseList, 'ティティ'), level=300, levelLimited=False, enemyHardness=(5, 5))
			for i in range(6): 
				team2.addMember(copy.copy(titi), i)
			team2.addMember(Unit(searchByName(unitBaseList, 'ガイアスクイーン'), level=300, levelLimited=False, enemyHardness=(5, 5)), 3)
			team2.changeLeader(3)
	team2.fillHP(4)

	for index, team in enumerate(gameData.teamList): 
		if team and index != 9: 
			team1 = team
			team1.fillHP(4)
			battle = Battle(team1, team2, background, MANUALBATTLE)

			yield battle

if __name__ == '__main__': 
	battle = getBattle()
	print(battle.tib1.gushaed)
	print(battle.tib2.gushaed)

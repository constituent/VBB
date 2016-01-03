#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# 懒得用enum了，之后有兴趣的话再改吧
AUTOBATTLE = 0
MANUALBATTLE = 1

DIVINES = "火水風土光闇"
DIVINE_OP_DICT = dict(zip(DIVINES, "水火土風闇光"))
attributeStr = "男女人魔神蟲器竜獣海飛氷火雷樹毒死霊騎夜超"
attributeFullnamelist = [
	'男性', 
	'女性', 
	'人間', 
	'魔族', 
	'神族', 
	'蟲族', 
	'器兵', 
	'竜族', 
	'獣族', 
	'海洋', 
	'飛行', 
	'氷霊', 
	'火霊', 
	'雷霊', 
	'樹霊', 
	'毒性', 
	'死者', 
	'霊体', 
	'騎士', 
	'夜行', 
	'超越']
attributeDict = {k: v for k, v in zip(attributeStr, attributeFullnamelist)}
attributeFullnamelist_ = attributeFullnamelist+['師団']
propertyList = ['攻撃', '防御', '速度', '知力']
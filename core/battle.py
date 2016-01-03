#! /usr/bin/env python3
# -*- coding: utf-8 -*-

__all__ = ['Background', 'Battle', 'BattleResult']

from enum import Enum

from .basicFunc import *
from .skill import *
from .team import *

class Background(): 
	def __init__(self, moon, daylight, lnd=(0, 0), 男=0, 女=0, 人=0, 魔=0, 神=0, 蟲=0, 
		器=0, 竜=0, 獣=0, 海=0, 飛=0, 氷=0, 火=0, 雷=0, 樹=0, 毒=0, 死=0, 霊=0, 騎=0, 夜=0, 超=0): 

		self.moon = moon
		self.daylight = daylight
		self.lnd = lnd
		self.男 = 男
		self.女 = 女
		self.人 = 人
		self.魔 = 魔
		self.神 = 神
		self.蟲 = 蟲
		self.器 = 器
		self.竜 = 竜
		self.獣 = 獣
		self.海 = 海
		self.飛 = 飛
		self.氷 = 氷
		self.火 = 火
		self.雷 = 雷
		self.樹 = 樹
		self.毒 = 毒
		self.死 = 死
		self.霊 = 霊
		self.騎 = 騎
		self.夜 = 夜
		self.超 = 超

BattleResult = Enum('BattleResult', ['全滅', '敗北', '勝利', '完勝', '未完'])

class Battle(): 
	def __init__(self, team1, team2, background, battleType): 
		tib1 = TeamInBattle(team1)
		tib2 = TeamInBattle(team2)
		tib1.oppositeTeam = tib2
		tib2.oppositeTeam = tib1
		tib1.battle = self
		tib2.battle = self
		self.tib1 = tib1
		self.tib2 = tib2
		self.background = background
		self.battleType = battleType
		if battleType == AUTOBATTLE: 
			self.roundCount = 1
		else: 
			self.roundCount = 5
		
		self.elapsedRound = 0

		self.refreshStatus()
		kishu1 = (tib2.奇襲戦法-tib1.奇襲警戒)//10
		if kishu1>0: 
			tib1.moveIndex(kishu1)
		kishu2 = (tib1.奇襲戦法-tib2.奇襲警戒)//10
		if kishu2>0: 
			tib2.moveIndex(kishu2)
		tib1.setFrontExist()
		tib2.setFrontExist()
		self.lnd1 = (background.lnd[0]+tib1.城壁構築, tib2.城壁崩し)
		self.lnd2 = (background.lnd[1]+tib2.城壁構築, tib1.城壁崩し)
		# 可以为负算了
		tib1.lnd = self.lnd1[0]-self.lnd1[1]
		tib2.lnd = self.lnd2[0]-self.lnd2[1]
		# tib1.lnd = max(self.lnd1[0]-self.lnd1[1], 0)
		# tib2.lnd = max(self.lnd2[0]-self.lnd2[1], 0)
		tib1.initBarrier()
		tib2.initBarrier()

		if self.battleType != AUTOBATTLE: 
			# 不妨搞一个5行动阻害的BOSS，不带行动增加的话根本无法开战
			# 所以这里不设下限了
			self.roundCount = self.roundCount+self.tib1.行動増加+self.tib2.行動増加-self.tib1.行動阻害-self.tib2.行動阻害

	def diffGusha(self): 
		gusha = self.tib1.getGusha()-self.tib2.getGusha()
		self.tib1.gushaed = gusha
		self.tib2.gushaed = -gusha

	def refreshStatus(self, targetNotDiedTeamList=None): 
		if targetNotDiedTeamList is None: 
			targetNotDiedTeamList = []
		self.diffGusha()
		self.tib1.initTeamSkill()
		self.tib2.initTeamSkill()
		self.tib1.initTeam(self.tib1 in targetNotDiedTeamList)
		self.tib2.initTeam(self.tib2 in targetNotDiedTeamList)

	def refreshAfterDeath(self, targetNotDiedTeamList=None): 
		self.refreshStatus(targetNotDiedTeamList)
		self.tib1.setFrontExist()
		self.tib2.setFrontExist()

	def turnEnd(self, lastRound): 
		tib1 = self.tib1; tib2 = self.tib2
		radiationDamage1, radiationDamage2 = getRadiationDamage(tib1, tib2)
		blastDamageArray1, blastDamageArray2 = getBlastDamageArray(tib1, tib2)

		absorbDamage1 = tib1.getAbsorbDamage(radiationDamage2, blastDamageArray2)
		absorbDamage2 = tib2.getAbsorbDamage(radiationDamage1, blastDamageArray1)
		reflectDamage1 = tib1.getReflectDamage(radiationDamage2, blastDamageArray2)
		reflectDamage2 = tib2.getReflectDamage(radiationDamage1, blastDamageArray1)

		countBefore = tib1.count()+tib2.count()
		damage_list1 = tib1.turnEnd(radiationDamage2, blastDamageArray2, reflectDamage2, absorbDamage1)
		damage_list2 = tib2.turnEnd(radiationDamage1, blastDamageArray1, reflectDamage1, absorbDamage2)
		countAfter = tib1.count()+tib2.count()

		if not lastRound and tib1 and tib2: 
			# 只要目标未死亡就不应该重设目标
			# 这里的程序还有点问题
			if countBefore == countAfter: 
				# 只可能死亡没有复活
				pass
				# tib1.setTargeted()
				# tib2.setTargeted()
			else: 
				self.refreshAfterDeath()

		return damage_list1, damage_list2

	# def run(self): 
	# 	while self.elapsedRound<self.roundCount: 
	# 		self.process()
	# 		if not self.tib1: 
	# 			return False
	# 		elif not self.tib2: 
	# 			return True

	# 	return self.tib1.sumHP()>self.tib2.sumHP()# 双方全死光时False

	def process(self): 
		actValueList = []
		for uib in self.tib1.members: 
			if uib: 
				actValueList.append((random.randint(*uib.actValue), uib))
		for uib in self.tib2.members: 
			if uib: 
				actValueList.append((random.randint(*uib.actValue), uib))
		actValueList.sort(key=lambda x: x[0], reverse=True)
		for _, uib in actValueList: 
			yield from uib.attack()
			if not (self.tib1 and self.tib2): 
				break

		yield self.turnEnd(self.elapsedRound+1 == self.roundCount)
		self.elapsedRound += 1

		if not self.tib1: 
			return BattleResult.全滅
		elif not self.tib2: 
			return BattleResult.完勝
		elif self.elapsedRound == self.roundCount: 
			if self.tib1.sumHP()>self.tib2.sumHP(): 
				return BattleResult.勝利
			else: 
				return BattleResult.敗北
		else: 
			# return None# 还没打完
			return BattleResult.未完

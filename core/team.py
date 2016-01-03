#! /usr/bin/env python3
# -*- coding: utf-8 -*-

__all__ = ['exchangeMember', 'Team', 'TeamInBattle']

from functools import reduce, partial

from numpy import zeros

from .basicFunc import *
from .skill import turnEndSkillDict, AbsorbDamage, ReflectDamage
from .unit import *

def exchangeMember(team1, index1, team2, index2): 
	uit1 = team1[index1]
	uit2 = team2[index2]

	uit1.index = index2
	if uit2: 
		uit2.index = index1
		uit2.team = team1
	team1[index1] = uit2
	team2[index2] = uit1; uit1.team = team2

	if team1 == team2: 
		if index1 == team1._leaderIndex: 
			team1._leaderIndex = index2
		elif index2 == team1._leaderIndex: 
			team1._leaderIndex = index1
	else: 
		if team2.count() == 1: 
			team2._leaderIndex = index2
		if index1 == team1._leaderIndex and uit2 is None: 
			left = team1.findFirstIndex()
			team1._leaderIndex = left
			return left

class Team(): 
	def __init__(self, index): 
		self.members = [None]*6
		self.index = index
		self._leaderIndex = None

	def __getitem__(self, key): 
		return self.members[key]

	def __setitem__(self, key, value): 
		self.members[key] = value

	def __bool__(self): 
		return any(m for m in self.members)

	def fillHP(self, value): 
		'仿VBH里，恢复当前缺少血量的百分比'
		if value not in (1, 2, 3, 4): 
			raise
		value = value*0.25
		for member in self.members: 
			if member: 
				member.fillHP(int((member.maxHP-member.HP)*value))

	@property
	def leader(self):
		return self[self._leaderIndex]

	def changeLeader(self, index): 
		if index != self._leaderIndex and self[index]: 
			old_leaderIndex = self._leaderIndex
			self._leaderIndex = index
			return old_leaderIndex

	def nextMember(self, index): 
		return self[(index+1)%6]

	def findFirstIndex(self): 
		for (index, uit) in enumerate(self.members): 
			if uit is not None: 
				return index
		return None

	def removeMember(self, index): 
		self[index] = None
		if index == self._leaderIndex: 
			left = self.findFirstIndex()
			self._leaderIndex = left

			return left

	def removeAllMembers(self): 
		for i in range(6): 
			self[i] = None
		self._leaderIndex = None

	def addMember(self, unit, index): 
		uit = UnitInTeam(unit)
		uit.team = self
		self[index] = uit
		uit.index = index
		if self.count() == 1: 
			self._leaderIndex = index

	# def exchangeMember(self, index1, index2): 
	# 	uit1 = self[index1]
	# 	uit2 = self[index2]
	# 	uit1.index = index2
	# 	if uit2: 
	# 		uit2.index = index1
	# 	self[index1] = uit2
	# 	self[index2] = uit1

	# 	# uit2可能为None，所以不能用uit2.isLeader
	# 	if self._leaderIndex == index1: 
	# 		self._leaderIndex = index2
	# 	elif self._leaderIndex == index2: 
	# 		self._leaderIndex = index1

	def count(self):
		return sum(1 for _ in self.members if _ != None)

	def refresh(self): 
		for member in members: 
			if member is not None and member.HP == 0: 
				member.HP = 1

class TeamInBattle(Team): 
	def __init__(self, team): 
		self.team = team
		self.members = [(lambda uit: UnitInBattle(uit, self) if uit is not None else None)(uit) for uit in team]
	
	def __getattr__(self, name): 
		try: 
			return getattr(self.team, name)
		except AttributeError: 
			raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, name)) from None

	def sumHP(self): 
		return sum(m.HP for m in self.members if m)

	def getGusha(self): 
		gusha = 0
		for member in self.members: 
			if member: 
				gusha = max(gusha, member.gusha)
		
		return gusha

	@property
	def gushaed(self):
		return self._gushaed
	@gushaed.setter
	def gushaed(self, value): 
		for member in self.members: 
			if member: 
				member.initSkillDict(value)
		self._gushaed = value
	
	def setFrontExist(self): 
		self.frontExist = any(self[i] for i in range(3))

	def getExistMembers(self): 
		return [member for member in self.members if member]

	def isBackColumn(self, index): 
		return index in (3, 4, 5) and self.frontExist

	def count(self): 
		return sum(1 for _ in self.members if _)

	def countDeath(self): 
		return sum(1 for _ in self.members if _ is not None and _.HP==0)

	def allOther(self, index): 
		return [m for m in self.members if m and m.index != index]

	def sameColumn(self, index): 
		a = index//3*3
		return [m for m in (self[a+(index+1)%3], self[a+(index+2)%3]) if m]

	def sameRow(self, index): 
		return [m for m in (self[(index+3)%6], ) if m]

	def changeOneMemberStatus(self, index): 
		oppositeTeam = self.oppositeTeam
		background = self.battle.background
		member = self.members[index]
		status = array(member.status, dtype='double')
		# 戦術補正値
		pass
		# 異常系補正
		as_ = member.abnormalStatus
		status -= array([as_.攻, as_.防, as_.速, as_.知])
		status *= 1-as_.呪/10
		# 地形補正値
		if not self.地形無効 and not oppositeTeam.地形無効: 
			強化 = 0; 弱化 = 0
			for t in member.tribe: 
				v = getattr(background, t)
				if v>0: 
					強化 += v
				elif v<0: 
					弱化 += v
			if as_.解: 
				強化 = 0
			if self.兵士運搬: 
				弱化 = 0
			地形 = min(max(強化+弱化, -90), 90)
			status *= 1+地形/100
		# 活性・陣形・弱体補正
		# //加護補正ステータス
		# 如果有双守护，忽略第一个的减成
		moon = background.moon
		if len(member.divine) == 1: 
			if member.divine == moon: 
				status *= 1.25
			elif member.divine == DIVINE_OP_DICT[moon]: 
				status *= 0.75
		else: 
			bMoon = False; count = 0
			for d in member.divine: 
				if d == moon: 
					count += 1
				elif d == DIVINE_OP_DICT[moon]: 
					if bMoon: 
						count -= 1
					else: 
						bMoon = True
			status *= 1+0.25*count

		if not as_.解: 
			# 活性・弱体スキル補正
			for t in member.tribe: 
				valueList = getattr(self, attributeDict[t]+'活性')
				for (i, v) in valueList: 
					if i != index: 
						status[: 3] += v
						status[3] += int(v/4)
			valueList = getattr(self, '師団活性')
			for (i, v) in valueList: 
				if i != index: 
					status[: 3] += v
					status[3] += int(v/4)

			v = self.背水の陣
			status[: 3] += v
			status[3] += int(v/4)

			status[0] += self.攻撃布陣
			status[1] += self.防御布陣
			status[2] += self.速度布陣
			status[3] += self.知力布陣

		for t in member.tribe: 
			v = getattr(oppositeTeam, attributeDict[t]+'弱体')
			status[: 3] -= v
			status[3] -= int(v/4)
		v = getattr(self, '師団弱体')
		status[: 3] -= v
		status[3] -= int(v/4)

		if not as_.解: 
			# 陣形補正値
			pass
		# 時間補正値
		v = member.getSkillSum('太陽信仰')-member.getSkillSum('夜行生物')
		if v != 0: 
			if background.daylight: 
				status *= 1+v/100
			else: 
				status *= 1-v/100

		# 防御减半
		if not (background.daylight or '夜' in member.tribe or member.haveSkill('夜戦適応') or v<0): 
			status[1] /= 2
		elif background.daylight and '夜' in member.tribe and not member.haveSkill('日中適応') and v<=0: 
			status[1] /= 2

		if not as_.解: 
			# リンク補正
			# 如果队长还活着
			if self.leader and not member.isLeader: 
				status *= 1.1

			command = 0
			for t in member.tribe: 
				valueList = getattr(self, attributeDict[t]+'指揮')
				for (i, v) in valueList: 
					if i != index: 
						command += v
			valueList = getattr(self, '師団指揮')
			for (i, v) in valueList: 
				if i != index: 
					command += v

			v = member.getSkillSum('報復の牙')
			if v>0: 
				command += self.countDeath()*v

			v = member.getSkillSum('狂奔の牙')
			if v>0: 
				command += oppositeTeam.countDeath()*v

			command = array([command]*4)
			command[0] += self.攻撃指揮
			command[1] += self.防御指揮
			command[2] += self.速度指揮
			command[3] += self.知力指揮

			status *= 1+command/100

		status[0] -= member.abnormalStatus.攻
		status[1] -= member.abnormalStatus.防
		status[2] -= member.abnormalStatus.速
		status[3] -= member.abnormalStatus.知

		status = array(status, dtype='int')
		status[status<1] = 1

		member.status = status
				
	def initMemberStatus(self): 
		for index, member in enumerate(self.members): 
			if member is not None: 
				member.status = copy.copy(member.unitInTeam.status)
			if member: 
				self.changeOneMemberStatus(index)

	def initTeam(self, notResetTargeted=False): 
		self.initMemberStatus()
		for member in self.members: 
			if member: 
				member.actValue = [member.status[2], 3*member.status[2]+10]
		if not notResetTargeted: 
			self.setTargeted()
		
	def setTargeted(self): 
		existMembers = self.getExistMembers()
		if existMembers: 
			self.targeted = min((m for m in self.members if m), key=lambda m: m.HP*int(m.status[1]))
		else: 
			self.targeted = None

	def setSealableSkills(self): 
		治療s = ['解毒治療', '解呪治療', '麻痺治療', '削減治療']
		for name in 治療s: 
			exec('self.'+name+'=False')
		for name in ['術式増幅', '対術結界']: 
			exec('self.'+name+'=0')
		for member in self.members: 
			if member and member.abnormalStatus.封 == 0: 
				haveSkill = member.haveSkill
				getSkillSum = member.getSkillSum
				
				if haveSkill('絶対治療'): 
					for name in 治療s: 
						exec('self.'+name+'=True')
				else: 
					for name in 治療s: 
						if haveSkill(name): 
							exec('self.'+name+'=True')
			
				self.術式増幅 = 1-(1-self.術式増幅)*(1-getSkillSum('術式増幅')/100)
				self.対術結界 = min(1-(1-self.対術結界)*(1-getSkillSum('対術結界')/100), 1)

	def initTeamSkill(self): 
		self.setSealableSkills()
		
		無効s = ['貫通無効', '扇形無効', '全域無効']
		otherBoolSkills = ['側面無効', '遠隔無効', '先陣の誉', '兵士運搬', '地形無効']
		for name in 無効s+otherBoolSkills: 
			exec('self.'+name+'=False')

		布陣s = [p+t for p in propertyList for t in ('布陣', '指揮')]
		otherAddableSkills = ['城壁崩し', '城壁構築', '行動増加', '行動阻害', '奇襲戦法', '奇襲警戒']+\
			[a+'弱体' for a in attributeFullnamelist_]
		for name in ['砲撃結界', '自爆結界', '資源工面', '背水の陣']+布陣s+otherAddableSkills: 
			exec('self.'+name+'=0')

		self.撃破金運 = []

		for t in ('活性', '指揮'): 
			for a in attributeFullnamelist_: 
				exec('self.'+a+t+'=[]')

		for index, member in enumerate(self.members): 
			if member: 
				haveSkill = member.haveSkill
				getSkillSum = member.getSkillSum

				if haveSkill('範囲無効'): 
					self.貫通無効 = True
					self.扇形無効 = True
					self.全域無効 = True
				else: 
					if haveSkill('十字無効'): 
						self.貫通無効 = True
						self.扇形無効 = True
					else: 
						self.貫通無効 |= haveSkill('貫通無効')
						self.扇形無効 |= haveSkill('扇形無効')
					self.全域無効 |= haveSkill('全域無効')

				for name in otherBoolSkills: 
					exec('self.'+name+'|=haveSkill("'+name+'")')

				self.砲撃結界 = min(1-(1-self.砲撃結界)*(1-getSkillSum('砲撃結界')/100), 1)
				self.自爆結界 = min(1-(1-self.自爆結界)*(1-getSkillSum('自爆結界')/100), 1)
				self.資源工面 += getSkillSum('資源工面')# 这玩意不设上限了

				if self.count() >= 4: 
					for name in 布陣s: 
						exec('self.'+name+'+=getSkillSum("'+name+'")')
				else: 
					self.背水の陣 += getSkillSum('背水の陣')

				for name in otherAddableSkills: 
					exec('self.'+name+'+=getSkillSum("'+name+'")')

				self.撃破金運 += member.getSkill('撃破金運')

				for t in ('活性', '指揮'): 
					for a in attributeFullnamelist_: 
						name = a+t
						value = eval('getSkillSum("'+name+'")')
						if value>0: 
							exec('self.'+name+'.append((index,value))')

	def moveIndex(self, kishu): 
		members = []
		for i in range(6): 
			index = (i-kishu)%6
			member = self[index]
			members.append(member)
			member.index = index
		self.members = members

	def initBarrier(self): 
		self.barrier = sum(m.getSkillSum('バリアー')*(m.level+50) for m in self.members if m)

	def getTotalDamage(self, radiationDamage2, blastDamageArray2, reflectDamage2): 
		# 反射伤害也受対術障壁等影响，并且例如火伤害对火种族无效
		# 想了想，改成反射只受対術障壁影响算了
		totalDamage1 = zeros((6, ))

		for i, m in enumerate(self.members): 
			if m: 
				# reduceRate = reduce(lambda x, y: 1-(1-x)*(1-y/100), 
				# 	(self.対術結界, m.getSkillSum('対術障壁'), m.getSkillSum('対術反射'), m.getSkillSum('対術吸収'))
				# 	, 0)
				# 対術結界 已经是0-1的值了
				reduceRate = reduce(lambda x, y: 1-(1-x)*(1-y/100), 
					(self.対術結界, m.getSkillSum('対術障壁'), m.getSkillSum('対術反射'), m.getSkillSum('対術吸収')))
				reduceRate_reflect = m.getSkillSum('対術障壁')/100

				for k, tea in turnEndSkillDict.items(): 
					# 即使tea.futile为空也没问题；tea.futile比m.tribe要短，所以这样也许性能会有些许提升
					if not any(f in m.tribe for f in tea.futile): 
						damage = 0
						
						for blastDamage in blastDamageArray2[: , i]: 
							if blastDamage: 
								damage += getattr(blastDamage, k)
						damage *= (1 if k == '毒' else (1-reduceRate))
						if m == m.team.targeted: 
							# 毒属性反正反射伤害肯定为0
							damage += getattr(radiationDamage2, k)*(1 if k == '毒' else (1-reduceRate))+\
								getattr(reflectDamage2, k)*(1-reduceRate_reflect)

						totalDamage1[i] += damage

		return totalDamage1

	def getTherapyArray(self): 
		therapyArray = zeros((6, ))
		amplify = 1+self.術式増幅
		for i, m in enumerate(self.members): 
			if m: 
				mndEffect = min(1+m.status[3]/100, 1.5)
				hp = min(m.HP, 9999)*mndEffect*amplify
				value = m.getSkillSum('自己治癒')+(m.getSkillSum('日中再生') if self.battle.background.daylight 
					else m.getSkillSum('夜間再生'))
				therapyArray[i] += hp*value/100
				therapyArray[self.targeted.index] += hp*m.getSkillSum('対象治癒')/100

				value1 = m.getSkillSum('全体治癒')/100*hp
				value2 = m.getSkillSum('魔族医療')/100*hp
				value3 = m.getSkillSum('平等治癒')/100*hp
				# 还是保证已死亡的单位加血量为0的好，虽然之后还可以判断使死亡单位不回复加血量
				if value1 or value2 or value3: 
					for j, n in enumerate(self.members): 
						if n: 
							if not '死' in n.tribe: 
								therapyArray[j] += value1
							if '死' in n.tribe or '魔' in n.tribe: 
								therapyArray[j] += value2
							therapyArray[j] += value3

		return therapyArray

	def turnEnd(self, radiationDamage2, blastDamageArray2, reflectDamage2, absorbDamage1): 
		damage_list = []
		if self: 
			totalDamage1 = self.getTotalDamage(radiationDamage2, blastDamageArray2, reflectDamage2)
			absorb_therapy_1 = sum(getattr(absorbDamage1, k) for k in turnEndSkillDict)/self.count()
			therapyArray1 = self.getTherapyArray()
			for i, m in enumerate(self.members): 
				if m: 
					taiku = min(m.getSkillSum('巨大体躯'), 80)-min(m.getSkillSum('矮小体躯'), 80)
					finalDamage1 = totalDamage1[i]+m.HP*m.abnormalStatus.毒/100
					finalDamage1 *= (1-taiku/100)*(1-min(m.getSkillSum('巨神体躯'), 98)/100)
					finalDamage1 -= absorb_therapy_1*(1 if taiku<0 else (1-taiku/100))
					# 被咀咒了照样能对术吸收，只是治疗无效
					# 治疗、对术吸收不被巨神减成
					if not m.abnormalStatus.呪: 
						finalDamage1 -= therapyArray1[i]*(1 if taiku<0 else (1-taiku/100))
					finalDamage1 = int(finalDamage1)
					damage_list.append(finalDamage1)
					m.damage_HP(finalDamage1)
					m.abnormalStatus.魅 = 0
				else: 
					damage_list.append(0)
		return damage_list

	class AF_Damage(): 
		def __init__(self, skillName, damageType): 
			self.skillName = skillName
			self.damageType = damageType
		def __call__(self, tib1, radiationDamage2, blastDamageArray2): 
			# 如果tib1死光了，会返回一个空的damageType，没有问题
			absorbDamage1 = self.damageType()
			for i1, m1 in enumerate(tib1.members): 
				if m1: 
					absorbRate = m1.getSkillSum(self.skillName)/100
					if absorbRate: 
						for blastDamage2 in blastDamageArray2[: , i1]: 
							if blastDamage2 is not None: 
								for k in turnEndSkillDict: 
									if k not in ('毒', ): 
										exec('absorbDamage1.'+k+' += absorbRate*blastDamage2.'+k)
						if m1 == m1.team.targeted: 
							for k in turnEndSkillDict: 
								if k not in ('毒', ): 
									exec('absorbDamage1.'+k+' += absorbRate*radiationDamage2.'+k)
			return absorbDamage1
		def __get__(self, instance, owner=None): 
			return partial(self, instance)

	getAbsorbDamage = AF_Damage('対術吸収', AbsorbDamage)
	getReflectDamage = AF_Damage('対術反射', ReflectDamage)

	# 好丑陋；Python3里去除了Unbound Method的概念，似乎要么现在这样写要么就需要写描述符
	# 所以还是就这样将就了吧
	# 似乎是所有函数都有__get__方法，所以写在函数里就成了方法了
	# 而函子大概没有吧
	
	# _getAbsorbDamage = AF_Damage('対術吸収', AbsorbDamage)
	# _getReflectDamage = AF_Damage('対術反射', ReflectDamage)
	# def getAbsorbDamage(self, *args, **kwargs): 
	# 	return TeamInBattle._getAbsorbDamage(self, *args, **kwargs)
	# def getReflectDamage(self, *args, **kwargs): 
	# 	return TeamInBattle._getReflectDamage(self, *args, **kwargs)

#! /usr/bin/env python3
# -*- coding: utf-8 -*-

__all__ = ['UnitBase', 'Unit', 'UnitInTeam', 'UnitInBattle', 'AbnormalStatus']

from enum import IntEnum
from .basicFunc import *
from .skill import Skill

def decomposeRecipe(number): 
	binaryFormat = '{0:0>41b}'.format(number)
	return [i for i, b in enumerate(binaryFormat) if b == '1']

class UnitBase(Data): 
	typeList = ["亜人", "魔獣", "妖精", "倭国", "悪魔", "不死", "造魔", "竜族", "蟲族", "兵卒", "傭兵", "聖職", "神族", "ユニーク"]
	GROWTHLIST = ['SS']+list('SABCDE')
	MAX_LEVEL = {"SS": 160, "S":150, "A":140, "B":130, "C":120, "D":110, "E":100}
	MAX_RARE = {"SS": 7, "S":6, "A":5, "B":4, "C":3, "D":2, "E":1}
	MAX_RARE_R = {value: key for (key, value) in MAX_RARE.items()}
	MAX_RARE_R[8] = "SS"; MAX_RARE_R[0] = "E"
	jobList = ['ブレイダー', 'ランサー', 'シューター', 'キャスター', 'ガーダー', 'デストロイヤー']
	jobStr = 'BLSCGD'
	jobDict = dict(zip(jobStr, jobList))
	moonAttrDict = {'火': [  4, -2,  3,  0,  2, -1],
		'水': [ -2,  4,  0,  3, -1,  2],
		'風': [  2, -1,  4, -2,  3,  0],
		'土': [ -1,  2, -2,  4,  0,  3],
		'光': [  3,  0,  2, -1,  4, -2],
		'闇': [  0,  3, -1,  2, -2,  4]
	}
	# formationList = ['猛攻', '特攻', '鶴翼', '城壁', '波状', '輪形', '早駆', '法撃', '射撃']
	def __init__(self, data): 
		Data.__init__(self, data)
		self.type = (lambda type:type if type!=0 else "ユニーク")(self.type)

		self.leaderSkills = [Skill(**i) for i in self.leaderSkill]
		self.skills = [Skill(**i) for i in self.skill]

		self.base1_hp = self.base1['hp']
		self.base2_hp = self.base2['hp']
		self.base1 = array([self.base1['pow'], self.base1['def'], self.base1['spd'], self.base1['mnd']])
		self.base2 = array([self.base2['pow'], self.base2['def'], self.base2['spd'], self.base2['mnd']])

		# self.checkTypo()

	def getDivine(self, titles): 
		divine = self.divine
		for title in titles: 
			if title is not None: 
				if title.divine:
					divine = title.divine
		return divine

	def getMoonEffect(self, employType, titles, moon, daylight): 
		pay = 3 if employType == 2 else self.pay
		divine = self.getDivine(titles)
		score = max(self.moonAttrDict[d][DIVINES.index(moon)] for d in divine)
		if (daylight and pay == 1) or (not daylight and pay == 2): 
			score += 2
		elif pay == 3: 
			score += 1
		score = min(max(score, 0), 4)
		return list(MoonEffect)[score]

	def checkTypo(self): 
		tribe = ''.join(sorted(list(self.tribe), key=attributeStr.find))
		for i in range(len(tribe)-2): 
			if tribe[i] == tribe[i+1]: 
				raise DataError('duplicated tribe of '+self.name)

		# if self.base1_hp+10 != self.base2_hp: 
		# 	print(self.name)
		# 还有技能不能重复等等，懒得弄了
		if self.open is None: 
			print(self.name)

	@property
	def maxLevel(self):
		return self.MAX_LEVEL[self.growth]
	@property
	def maxExp(self):
		return self.calExp(self.maxLevel)
	@property
	def maxRare(self):
		return self.MAX_RARE[self.growth]
	@property
	def recipeIndexList(self):
		if self.recipe: 
			return decomposeRecipe(self.recipe)
		else: 
			return []
	@classmethod
	def calLevel(cls, exp):
		return int(sqrt(exp/10)+1)
	@classmethod
	def calExp(cls, level):
		return 10*(level-1)**2

	def get_bf(self): 
		return (r'graphics\unit', self.image1[0]+'.png')

	def get_uw(self): 
		return (r'interface\icon', self.image1[1]+'.png')

	def get_fc(self): 
		return (r'interface\icon', self.image1[2]+'.png')

	def get_bc_mini1(self): 
		return (r'interface\icon', self.image1[6]+'.png')

MoonEffect = IntEnum('MoonEffect', 'worst bad normal good best', start=0)

class Unit(): 
	# // 難易度別敵ユニット強化定数(+)
	#难度加算：
	ENEMYHARDNESS_P = array([[-5,-5,-5,-5,-10], 
		[ 0, 0, 0, 0,  0], 
		[ 0, 0, 0, 0,  0], 
		[ 5, 5, 2, 1,  0], 
		[10,10, 4, 1,  0], 
		[20,20, 6, 2,  0]])
	#难度乘算：
	ENEMYHARDNESS_M = array([[0.50,0.50,0.50,0.50,0.50], 
		[0.50,0.50,0.50,0.50,0.50], 
		[1.00,1.00,1.00,1.00,1.00], 
		[1.10,1.10,1.10,1.10,1.00], 
		[1.15,1.15,1.15,1.15,1.00], 
		[1.20,1.20,1.20,1.20,1.00]])
	#发狂加算：
	ENEMYBERSERK_P = array([[   0,   0,   0,   0,   0], 
		[  10,  10,   4,   1,   0], 
		[  20,  20,   4,   1,   0], 
		[  30,  30,   8,   2,   0], 
		[  40,  40,   8,   2,   0], 
		[  50,  50,  12,   3,   0]])
	#发狂乘算：
	ENEMYBERSERK_M = array([[1.00,1.00,1.00,1.00,1.00], 
		[1.10,1.10,1.10,1.10,1.00], 
		[1.20,1.20,1.20,1.20,1.00], 
		[1.30,1.30,1.30,1.30,1.00], 
		[1.40,1.40,1.40,1.40,1.00], 
		[1.50,1.50,1.50,1.50,1.00]])
	moonEffectAttributeDict = {}
	moonEffectAttributeDict[MoonEffect.best] = array((4, 4, 4, 1))
	moonEffectAttributeDict[MoonEffect.good] = array((2, 2, 2, 0))
	moonEffectAttributeDict[MoonEffect.normal] = array((0, 0, 0, 0))
	moonEffectAttributeDict[MoonEffect.bad] = array((-4, -4, -4, -2))
	moonEffectAttributeDict[MoonEffect.worst] = array((-8, -8, -8, -4))
	def __init__(self, unitBase, employType=1, moonEffect=MoonEffect.normal, titles=(None, None), level=1, items=(None, None), exp=0, 
		valor=25, levelLimited:"其实就是非敌方单位的意思"=True, enemyHardness:"普通难度，发狂0"=(2, 0)): 
		# 很多代码都是可以去掉的，算了懒得改了
		self.unitBase = unitBase
		self.inTeam = False
		if level != 1 and exp == 0:
			exp = UnitBase.calExp(level)
		elif level == 1 and exp != 0:
			level = UnitBase.calLevel(exp)
		elif (exp != 0 or level != 1) and UnitBase.calLevel(exp) != level:
			raise

		self.name = self.unitBase.name
		self.tribe = self.unitBase.tribe
		self.job = self.unitBase.job
		if levelLimited: 
			level = min(level, unitBase.maxLevel)
			exp = min(exp, unitBase.maxExp)
		self.levelLimited = levelLimited
		self.divine = self.unitBase.divine
		self.special = self.unitBase.special
		self._skills = copy.copy(self.unitBase.skills)
		self.titleText = ""
		for title in titles: 
			if title is not None: 
				self.titleText += title.name
				if title.divine:
					self.divine = title.divine
				if title.special:
					self.special += title.special
				self._skills.append(title.skill)
			else: 
				self._skills.append(Skill())	

		self._skills += [Skill()]*4
		self.items = [None, None]
		self._changeEquip(0, items[0])
		self._changeEquip(1, items[1])
		
		self._HP = 1; self.employType = employType
		self.level = level; self.exp = exp; self.valor = valor; self.loyalty = valor
		self.items = list(items); self.titles = titles; self.moonEffect = moonEffect
		self.enemyHardness = enemyHardness

		if employType == 1: 
			self.pay = unitBase.pay
			self._skills += self.unitBase.leaderSkills
		else: 
			self.pay = 3
			self._skills += [Skill()]*2
		
		self.setMaxHP()
		self.setStatus()

	def __repr__(self): 
		return self.unitBase.name

	def getSkills(self): 
		return self._skills
		
	@property
	def HP(self):
		return self._HP

	@HP.setter
	def HP(self, value): 
		self._HP = min(max(value, 0), self.maxHP)

	def fillHP(self, value=None): 
		if value is None: 
			value = self.maxHP-self.HP
		self.HP += value
		return value

	def changeEquip(self, index, item): 
		self._changeEquip(index, item)
		self.items[index] = item
		self.setStatus()

	def _changeEquip(self, index, item): 
		indice = [[10, 12], [12, 14]][index]
		if item is not None: 
			self._skills[indice[0]: indice[1]] = item.skills
		else: 
			self._skills[indice[0]: indice[1]] = [Skill(), Skill()]

	def setMaxHP(self): 
		base_hp = self.unitBase.base1_hp if self.employType == 1 else self.unitBase.base2_hp
		maxHP = int((base_hp+self.ENEMYHARDNESS_P[self.enemyHardness[0], 4]+
			self.ENEMYBERSERK_P[self.enemyHardness[1], 4])*(1+(self.level-1)/4))
		self.maxHP = int(maxHP*self.ENEMYHARDNESS_M[self.enemyHardness[0], 4]*self.ENEMYBERSERK_M[self.enemyHardness[1], 4])
	
	def setStatus(self): 
		base = self.unitBase.base1 if self.employType == 1 else self.unitBase.base2
		# 实际上计算属性值并不是使用leastExp，而是当前实际exp，即同一level的同一单位属性也可能不同……
		base = array(base, dtype='double')+self.ENEMYHARDNESS_P[self.enemyHardness[0], :4]+\
			self.ENEMYBERSERK_P[self.enemyHardness[1], :4]
		base += self.moonEffectAttributeDict[self.moonEffect]
		valorBonus = (self.valor-25)/2/sqrt(self.unitBase.cost)
		base[0] += valorBonus; base[1] += valorBonus
		for title in self.titles: 
			if title is not None: 
				base += title.add
		base = floor(base)# _FLC返回值为int；简直莫名其妙
		base[base<1] = 1

		exp = self.exp
		base = floor(base*(1+sqrt(exp)/500)+sqrt(exp)/25)
		base = base*self.ENEMYHARDNESS_M[self.enemyHardness[0], :4]*self.ENEMYBERSERK_M[self.enemyHardness[1], :4]
		base = floor(base); base[base<1] = 1

		for item in self.items: 
			if item is not None: 
				base += item.add
		base[base<1] = 1
		base = array(base, dtype='int')

		self.status = base

class UnitInTeam(Unit): 
	def __init__(self, unit): 
		self.unit = unit
		unit.inTeam = True
		self.team = None
		self.index = None
		self.recovered = False

	@property
	def isLeader(self): 
		return self == self.team.leader

	@property
	def HP(self):
		return self.unit.HP
	@HP.setter
	def HP(self, value): 
		self.unit.HP = value

	def __getattr__(self, name): 
		try: 
			return getattr(self.unit, name)
		except AttributeError: 
			raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, name)) from None

	def _getGusha(self): 
		ei = 16 if self.isLeader and self.employType == 1 else 14
		values = []
		for i in range(ei): 
			skill = self._skills[i]
			if skill.name == '愚者の嘘': 
				values.append(skill.value)

		return sum(values)

	def nextMember(self): 
		return self.team.nextMember(self.index)

class UnitInBattle(UnitInTeam): 
	def __init__(self, unitInTeam, tib, keepMaxHP=False): 
		# keepMaxHP是为了发动recovery时回更多血，高难度敌人专用
		self.unitInTeam = unitInTeam
		self.team = tib
		self.abnormalStatus = AbnormalStatus()
		# self.status = copy.copy(self.unitInTeam.status)# 可以不要这句
		if keepMaxHP or self.unitInTeam.HP == 0: 
			self.maxHP = self.unitInTeam.maxHP
		else: 
			self.maxHP = self.unitInTeam.HP
		self.index = self.unitInTeam.index
		self._gusha = None

	@property
	def gusha(self): 
		if self._gusha == None: 
			self._gusha = self._getGusha()
		return self._gusha

	@property
	def HP(self):
		return self.unitInTeam.HP

	@HP.setter
	def HP(self, value): 
		self.unitInTeam.HP = min(value, self.maxHP)
		if (self.unitInTeam.HP == 0 and self.haveSkill('リカバリ') and self.unitInTeam.recovered == False 
			and not (self.abnormalStatus.呪 or self.abnormalStatus.封)): 
			self.unitInTeam.HP = int(self.maxHP*min(self.getSkillSum('リカバリ')/100, 1))
			self.unitInTeam.recovered = True
			self.HP_recovered = self.unitInTeam.HP
		else: 
			self.HP_recovered = 0

	def __getattr__(self, name): 
		try: 
			return getattr(self.unitInTeam, name)
		except AttributeError: 
			raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, name)) from None

	def __bool__(self): 
		return self.HP>0

	def changeStatus(self): 
		self.team.changeOneMemberStatus(self.index)

	def initSkillDict(self, gushaed): 
		self.skillDict = {}
		si = 0 if gushaed >= 0 else -gushaed
		ei = 16 if self.isLeader else 14
		for i in range(si, ei): 
			skill = self._skills[i]
			if skill: 
				self.skillDict.setdefault(skill.name, []).append(skill.value)
	
	def getSkill(self, skillName): 
		return self.skillDict.get(skillName, [])
	def getSkillSum(self, skillName): 
		return sum(self.getSkill(skillName))
	def haveSkill(self, *skills): 
		return any(skill in self.skillDict for skill in skills)

	def isBackColumn(self): 
		return self.team.isBackColumn(self.index)

	def damage_HP(self, damage): 
		# 返回自爆伤害
		# 如果是turnEnd伤害，调用者直接丢弃返回值
		# 被自爆炸死也一样
		boom = 0
		barrier = self.team.barrier
		if damage>0 and barrier>0: 
			barrier -= damage
			if barrier<0: 
				if -barrier>self.HP: 
					# 和VBH里一样，HP和barrier之和
					boom = self.HP+self.team.barrier
				self.HP += barrier
				self.team.barrier = 0
			else: 
				self.team.barrier = barrier
		else: 
			if damage>self.HP: 
				boom = self.HP
			self.HP -= damage
		return boom

	def oneCharge(self, dummy_): 
		'''
		一次攻击
		'''
		def getDummyList(self, dummy): 
			targetTeam = dummy.team
			dummyList = [dummy]
			if self.haveSkill('全域攻撃') and not targetTeam.全域無効: 
				dummyList += targetTeam.allOther(dummy.index)
				if len(dummyList)>1: 
					selfEffectSet.add('全域攻撃')
			else: 
				if self.haveSkill('扇形攻撃') and not targetTeam.扇形無効: 
					sameColumn = targetTeam.sameColumn(dummy.index)
					dummyList += sameColumn
					if len(sameColumn)>0: 
						selfEffectSet.add('扇形攻撃')
				if self.haveSkill('貫通攻撃') and not targetTeam.貫通無効: 
					sameRow = targetTeam.sameRow(dummy.index)
					dummyList += sameRow
					if len(sameRow)>0: 
						selfEffectSet.add('貫通攻撃')

			return dummyList

		def isCritical(a, d): 
			cr = 5+sqrt(a.status[2])*3-sqrt(d.status[2])
			cr += a.getSkillSum('必殺増加')-d.getSkillSum('必殺耐性')
			max_cr = 75 if a.haveSkill('必殺増加') else 50
			cr = max(min(cr, max_cr), 5)
			return randOccur(cr)
		
		def getParry(self, dummy, cr, aType): 
			parry = False
			if aType == 1 or not self.haveSkill('次元斬撃'): # 反击或无次元时不能无视格挡
				if cr: 
					if randOccur(50): # 暴击时一半概率无视格挡
						parry = randOccur(dummy.getSkillSum('パリング')+dummy.getSkillSum('次元斬撃'))
				else: 
					parry = randOccur(dummy.getSkillSum('パリング')+dummy.getSkillSum('次元斬撃'))
			return parry

		def setmifu(self, dummy, selfEffectSet, dummyEffectSet): 
			# 先计算封印和魅了，因为可能会封印掉异常治疗技能
			# 如果是范围攻击复数异常，先全封印和魅了掉
			def setSeal(dummy, value): 
				if not dummy.abnormalStatus.封 and value: 
					# 从未被封印到被封印
					# 只有这种情况需要改变值
					dummy.abnormalStatus.封 = 1
					dummy.team.setSealableSkills()

			if not '超' in dummy.tribe: 
				haveSeal = self.haveSkill('封印攻撃'); haveCharm = self.haveSkill('性的魅了')
				have_a = dummy.haveSkill('異常耐性'); have_b = dummy.haveSkill('勇猛果敢')
				if (haveSeal or haveCharm): 
					if have_a: 
						dummyEffectSet.add('異常耐性')
					elif have_b: 
						dummyEffectSet.add('勇猛果敢')
					else: 
						targetTeam = dummy.team
						if haveSeal: 
							selfEffectSet.add('封印攻撃')
							setSeal(dummy, 1)
						if '火' not in dummy.tribe and haveCharm: 
							selfEffectSet.add('性的魅了')
							if ('男' in self.tribe and '女' in dummy.tribe) or ('女' in self.tribe and '男' in dummy.tribe): 
								if dummy.abnormalStatus.魅 == 0: 
									dummy.abnormalStatus.魅 = 1
									if not (targetTeam.麻痺治療 or '雷' in dummy.tribe): 
										dummy.abnormalStatus.麻 = 2
								elif dummy.abnormalStatus.魅 == 1: 
									dummy.abnormalStatus.魅 = 2
									setSeal(dummy, 1)
							elif not (targetTeam.麻痺治療 or '雷' in dummy.tribe): 
								dummy.abnormalStatus.麻 += 1

		def setOtherAbnormalStatus(self, dummy, selfEffectSet, dummyEffectSet): 
			def setCurse(dummy, value): 
				if not dummy.abnormalStatus.呪 and value: 
					dummy.abnormalStatus.呪 = 1
					return True
				else: 
					return False

			def setFree(dummy, value): 
				if not dummy.abnormalStatus.解 and value: 
					dummy.abnormalStatus.解 = 1
					return True
				else: 
					return False

			IGNOREZETTAI = True
			targetTeam = dummy.team
			needReset = False; status = dummy.status
			if not '超' in dummy.tribe: 
				sumRainbow = self.getSkillSum('虹の毒撃')
				sumPoison = self.getSkillSum('毒化攻撃')
				sumParalyze = self.getSkillSum('麻痺攻撃')
				haveCurse = self.haveSkill('呪の一撃')
				haveFree = self.haveSkill('解除攻撃')
				sumAtk = self.getSkillSum('攻撃削減')
				sumDef = self.getSkillSum('防御削減')
				sumSpd = self.getSkillSum('速度削減')
				sumMnd = self.getSkillSum('知力削減')

				have_a = dummy.haveSkill('異常耐性')
				if (sumRainbow or sumPoison or sumParalyze or haveCurse or haveFree or sumAtk or sumDef or sumSpd or sumMnd): 
					if have_a: 
						dummyEffectSet.add('異常耐性')
					else: 
						if sumRainbow: 
							# 无视治疗
							if not ((not IGNOREZETTAI and targetTeam.解毒治療) or '死' in dummy.tribe or '毒' in dummy.tribe): 
								selfEffectSet.add('毒化攻撃')
								dummy.abnormalStatus.毒 += sumRainbow
							if not ((not IGNOREZETTAI and targetTeam.麻痺治療) or '雷' in dummy.tribe): 
								selfEffectSet.add('麻痺攻撃')
								dummy.abnormalStatus.麻 = 2
							if not ((not IGNOREZETTAI and targetTeam.解呪治療) or '神' in dummy.tribe or '霊' in dummy.tribe): 
								selfEffectSet.add('呪の一撃')
								needReset |= setCurse(dummy, 1)
							if not (not IGNOREZETTAI and targetTeam.削減治療): 
								selfEffectSet |= {'攻撃削減', '防御削減', '速度削減', '知力削減'}
								dummy.abnormalStatus.攻 += sumRainbow
								dummy.abnormalStatus.防 += sumRainbow
								dummy.abnormalStatus.速 += sumRainbow
								dummy.abnormalStatus.知 += sumRainbow
								status -= sumRainbow
								status[status<1] = 1

						if not (targetTeam.解毒治療 or '死' in dummy.tribe or '毒' in dummy.tribe) and sumPoison: 
							selfEffectSet.add('毒化攻撃')
							dummy.abnormalStatus.毒 += sumPoison
						if not (targetTeam.麻痺治療 or '雷' in dummy.tribe) and sumParalyze: 
							selfEffectSet.add('麻痺攻撃')
							dummy.abnormalStatus.麻 += self.sumParalyze
						
						if not (targetTeam.解呪治療 or '神' in dummy.tribe or '霊' in dummy.tribe) and haveCurse: 
							selfEffectSet.add('呪の一撃')
							needReset |= setCurse(dummy, 1)
						if not targetTeam.削減治療: 
							if haveFree: 
								selfEffectSet.add('解除攻撃')
								needReset |= setFree(dummy, 1)

							if sumAtk: 
								status[0] -= sumAtk
								dummy.abnormalStatus.攻 += sumAtk
								selfEffectSet.add('攻撃削減')

							if sumDef: 
								status[1] -= sumDef
								dummy.abnormalStatus.防 += sumDef
								selfEffectSet.add('防御削減')

							if sumSpd: 
								status[2] -= sumSpd
								dummy.abnormalStatus.速 += sumSpd
								selfEffectSet.add('速度削減')

							if sumMnd: 
								status[3] -= sumMnd
								dummy.abnormalStatus.知 += sumMnd
								selfEffectSet.add('知力削減')

							status[status<1] = 1

			if needReset: 
				dummy.changeStatus()

		def calBaika(self, dummy, aType, selfEffectSet, dummyEffectSet, bNotMainDummy): 
			def calSpecial(a, d): 
				def countSpecial(t, a): 
					count = sum(1 for s in a.special if t == s or s == '全')
					count += a.getSkillSum(attributeDict[t]+'特攻')+a.getSkillSum('全種特攻')
					return count

				result = sum(countSpecial(t, a) for t in d.tribe)
				temp = min(d.getSkillSum('特攻防御'), 100)/100
				if not (aType == 0 and bNotMainDummy) and temp>0: 
					dummyEffectSet.add('特攻防御')
				result = result*(1-temp)
				if not (aType == 0 and bNotMainDummy) and result>0: 
					if aType == 0: 
						effectInOneCharge.tokkoubaika1 = result
					else: 
						effectInOneCharge.tokkoubaika2 = result
				return result

			special = calSpecial(self, dummy)
			if aType == 1: 
				temp = self.getSkillSum('反撃倍加')
				if temp>0: 
					effectInOneCharge.hangekibaika = temp
				special += temp

			return 1+special

		def getDamage(self, dummy, cr, taiku, aType, baika, selfEffectSet, dummyEffectSet, bNotMainDummy): 
			def jobSpecial(a, d, jobStr): 
				return jobStr[(jobStr.index(d.job)+1)%6] == a.job
			def sqrt_(lnd): 
				if lnd<0: 
					return -sqrt(-lnd)
				else: 
					return sqrt(lnd)

			atk_ = self.status[0]; def_ = dummy.status[1]
			if aType == 0: 
				def_ *= 1-min(self.getSkillSum('次元斬撃'), 75)/100
				def_ *= 1-min(self.getSkillSum('カブト割'), 75)/100
			if cr and self.haveSkill('致命必殺'): 
				selfEffectSet.add('致命必殺')
				def_ *= 0.75
			def_ = max(def_, 1)
			damage = (2*atk_+5)*sqrt(min(self.HP, 9999))/max(def_+1+sqrt_(dummy.team.lnd), 1)/({0: 1, 1: 3}[aType])
			if cr: 
				damage *= 1.5
				if self.haveSkill('致命必殺'): 
					temp = dummy.getSkillSum('致命耐性')
					if not (aType == 0 and bNotMainDummy) and temp: 
						dummyEffectSet.add('致命耐性')
					# 如果致命耐性大于致命必杀，不显示致命必杀？感觉并无必要
					damage *= 1+(max(self.getSkillSum('致命必殺')-temp, 0))/100

			damage *= baika

			if jobSpecial(self, dummy, UnitBase.jobStr): 
				if not (aType == 0 and bNotMainDummy): 
					selfEffectSet.add('兵種特攻')
				damage *= 1.5

			if dummy.haveSkill('専守防衛'): # 如果程序正确，这里不需要判断aType
				dummyEffectSet.add('専守防衛')
				damage /= 2

			damage *= 1-taiku/100
			temp = dummy.getSkillSum('巨神体躯')
			if not (aType == 0 and bNotMainDummy) and temp: 
				dummyEffectSet.add('巨神体躯')
			damage *= 1-min(temp, 98)/100

			# 接下来的顺序，battleMain.ks里的是：龙鳞吸血自爆全力反击耐性
			# 先不说自爆，吸血应该在全力之后（当然VBH里吸血量与伤害量无关倒无所谓）
			# 如果反耐在龙鳞之前，范马本身75龙鳞50反耐，再给25反耐的话，触发龙鳞时相当于给了75龙鳞
			# 不触发龙鳞时减少受到的伤害，也比给此时完全没意义的龙鳞好
			# 但要有高龙鳞高反耐才行，并且还要有输出，所以也不算很bug，决定先反耐再龙鳞
			# 先龙鳞再吸血，注意吸血不要直接减在伤害上
			# 最终决定：反击耐性龙鳞全力吸血

			if aType == 1: 
				temp = dummy.getSkillSum('反撃耐性')
				if temp: 
					dummyEffectSet.add('反撃耐性')
					damage *= 1-min(temp, 80)/100

			return damage

		effectInOneCharge = EffectInOneCharge()
		selfEffectSet = effectInOneCharge.selfEffectSet
		dummyEffectSet = effectInOneCharge.dummyEffectSet

		if self.haveSkill('次元斬撃'): 
			selfEffectSet.add('次元斬撃')
		if self.haveSkill('カブト割'): 
			selfEffectSet.add('カブト割')
		if self.haveSkill('全力攻撃'): 
			selfEffectSet.add('全力攻撃')
		if self.haveSkill('吸血攻撃'): 
			selfEffectSet.add('吸血攻撃')
		if self.haveSkill('側面攻撃') and not dummy_.team.側面無効: 
			selfEffectSet.add('側面攻撃')
			

		remote = self.haveSkill('次元斬撃') or (self.haveSkill('遠隔攻撃') and not dummy_.team.遠隔無効)
		if remote: 
			selfEffectSet.add('遠隔攻撃')
		dummyList = getDummyList(self, dummy_)
		if len(dummyList)>1 and self.haveSkill('複数異常'): 
			if self.haveSkill(*(EffectInOneCharge.asList)): 
				selfEffectSet.add('複数異常')

		evadeList = []
		for bNotMainDummy, dummy in enumerate(dummyList): 
			if remote: 
				evade = randOccur( max(dummy.getSkillSum('イベイド')-self.getSkillSum('側面攻撃'), 
					1 if dummy.haveSkill('イベイド') else 0) )
			else: 
				evade = False

			if not bNotMainDummy and evade: 
				dummyEffectSet.add('イベイド')

			# 优先闪避，因为能闪异常状态

			if not evade and (not bNotMainDummy or self.haveSkill('複数異常')): 
				setmifu(self, dummy, selfEffectSet, dummyEffectSet)
			if not bNotMainDummy and dummy.haveSkill('反撃異常'): 
				dummyEffectSet.add('反撃異常')
				setmifu(dummy, self, dummyEffectSet, selfEffectSet)

			evadeList.append(evade)

		damageList = []; boomList = []
		taiku2 = min(self.getSkillSum('巨大体躯'), 80)-min(self.getSkillSum('矮小体躯'), 80)
		if taiku2>0: 
			selfEffectSet.add('巨大体躯')
		for bNotMainDummy, (dummy, evade) in enumerate(zip(dummyList, evadeList)): 
			if not evade and (not bNotMainDummy or self.haveSkill('複数異常')): 
				setOtherAbnormalStatus(self, dummy, selfEffectSet, dummyEffectSet)
			if not bNotMainDummy and dummy.haveSkill('反撃異常'): 
				setOtherAbnormalStatus(dummy, self, dummyEffectSet, selfEffectSet)

			damageCoefficient = 0.5 if bNotMainDummy else 1
			
			taiku1 = min(dummy.getSkillSum('巨大体躯'), 80)-min(dummy.getSkillSum('矮小体躯'), 80)
			if not bNotMainDummy and taiku1>0: 
				dummyEffectSet.add('巨大体躯')

			waishou1 = (taiku1<0 and randOccur(-taiku1)) if not evade else False
			waishou2 = (taiku2<0 and randOccur(-taiku2)) if not bNotMainDummy else False

			if not bNotMainDummy and waishou1>0: 
				dummyEffectSet.add('矮小体躯')
			if waishou2>0: 
				selfEffectSet.add('矮小体躯')

			# 即使回避了，还是要无意义地暴击
			cr1 = isCritical(self, dummy)
			cr2 = isCritical(dummy, self) if not bNotMainDummy else False
			if cr1: 
				selfEffectSet.add('クリティカル')
				if self.haveSkill('必殺増加'): 
					selfEffectSet.add('必殺増加')
			elif not bNotMainDummy and dummy.haveSkill('必殺耐性'): 
				dummyEffectSet.add('必殺耐性')

			if not bNotMainDummy: 
				if cr2: 
					dummyEffectSet.add('クリティカル')
					if dummy.haveSkill('必殺増加'): 
						dummyEffectSet.add('必殺増加')
				elif self.haveSkill('必殺耐性'): # 只看主目标反击时有无暴击
					selfEffectSet.add('必殺耐性')


			parry1 = getParry(self, dummy, cr1, 0) if not (evade or waishou1) else False
			parry2 = getParry(dummy, self, cr2, 1) if not (waishou2 or bNotMainDummy) else False

			if not bNotMainDummy and parry1: 
				dummyEffectSet.add('パリング')
			if parry2: 
				selfEffectSet.add('パリング')

			baika1 = calBaika(self, dummy, 0, selfEffectSet, dummyEffectSet, bNotMainDummy)
			if not bNotMainDummy: 
				baika2 = calBaika(dummy, self, 1, dummyEffectSet, selfEffectSet, bNotMainDummy)
			else: 
				baika2 = 1

			damage1 = 0 if evade or waishou1 or parry1 else getDamage(self, dummy, cr1, taiku1, 0, baika1, 
				selfEffectSet, dummyEffectSet, bNotMainDummy)*damageCoefficient
			damage2 = 0 if bNotMainDummy or waishou2 or parry2 or dummy.abnormalStatus.魅 else getDamage(
				dummy, self, cr2, taiku2, 1, baika2, dummyEffectSet, selfEffectSet, bNotMainDummy)

			# 这里的次元其实没意义因为次元必然damage2==0
			if not (self.haveSkill('次元斬撃', '竜族特攻', '全種特攻') or '竜' in self.special
				or '全' in self.special) and damage2*dummy.getSkillSum('竜鱗守護')/100 > damage1: 
				竜鱗1 = True
				# 非主目标理论上不可能发动龙鳞，
				dummyEffectSet.add('竜鱗守護')
			else: 
				竜鱗1 = False
			if not (dummy.haveSkill('次元斬撃', '竜族特攻', '全種特攻') or '竜' in dummy.special
				or '全' in dummy.special) and damage1*self.getSkillSum('竜鱗守護')/100 > damage2: 
				竜鱗2 = True
				if not bNotMainDummy: 
					selfEffectSet.add('竜鱗守護')
			else: 
				竜鱗2 = False

			if 竜鱗1: damage1 = 0
			if 竜鱗2: damage2 = 0
			# 远隔不破龙鳞
			if remote: 
				damage2 = 0

			temp = 1+self.getSkillSum('全力攻撃')/100
			damage1 *= temp; damage2 *= temp

			# 即使复数异常，也只能吸主目标
			# 最多吸目标当前血量
			bloodsuck1 = int(min(damage1*self.getSkillSum('吸血攻撃')/100, dummy.HP)) if not bNotMainDummy else 0
			# 反正非主目标的反击伤害为0，就这样不改了
			bloodsuck2 = 0
			if not bNotMainDummy and dummy.haveSkill('反撃異常') and dummy.haveSkill('吸血攻撃'): 
				dummyEffectSet.add('吸血攻撃')
				bloodsuck2 = int(min(damage2*dummy.getSkillSum('吸血攻撃')/100, self.HP))
				effectInOneCharge.bloodsuck2 = bloodsuck2

			damage1 = int(damage1); damage2 = int(damage2)
			damageList.append(damage1)

			if not bNotMainDummy: 
				counterDamage = damage2; effectInOneCharge.counterDamage = counterDamage
				bloodsuck = bloodsuck1; effectInOneCharge.bloodsuck = bloodsuck
				baika = baika1

			boom = dummy.damage_HP(damage1-bloodsuck2)
			if boom and not bNotMainDummy and dummy.haveSkill('自決自爆'): 
				dummyEffectSet.add('自爆決行')

			boomList.append(boom*dummy.getSkillSum('自決自爆')/100*baika2)

		effectInOneCharge.damageList = damageList
			
		# 被咀咒了也能吸血
		tempSum = sum(boomList)
		if tempSum: 
			temp = self.getSkillSum('自爆障壁')+self.getSkillSum('巨神体躯')
			if temp: 
				selfEffectSet.add('自爆耐性')
			if self.team.自爆結界: 
				selfEffectSet.add('自爆耐性')
			boom1 = int(tempSum*(0.5 if self.haveSkill('遠隔攻撃', '次元斬撃') or '火' in self.tribe 
				or '超' in self.tribe else 1)*(1-min(temp, 100)/100)*(1-self.team.自爆結界))
		else: 
			boom1 = 0

		tempBoom = self.damage_HP(counterDamage-bloodsuck)*self.getSkillSum('自決自爆')/100
		if tempBoom: 
			selfEffectSet.add('自爆決行')
			temp = dummy_.getSkillSum('自爆障壁')+dummy_.getSkillSum('巨神体躯')
			if temp: 
				dummyEffectSet.add('自爆耐性')
			if dummy_.team.自爆結界: 
				dummyEffectSet.add('自爆耐性')
			boom2 = int(tempBoom*baika1*(0.5 if '火' in dummy_.tribe or '超' in dummy_.tribe else 1)*(
				1-min(temp, 100)/100)*(1-dummy_.team.自爆結界))
		else: 
			boom2 = 0

		effectInOneCharge.boom1 = boom1
		effectInOneCharge.boom2 = boom2

		# 先物理攻击伤害，该复活就复活
		# 再自爆伤害，刚复活也可能被爆死
		# 也可能是自爆导致的复活
		# 复活导致的HP恢复的值不一定是最终残余HP

		self.damage_HP(boom1)
		dummy_.damage_HP(boom2)

		# 任一单位死亡，则从愚者开始全部重新初始化
		# 不过目标没死那队的目标不变
		if self.HP == 0 or any(m.HP == 0 for m in dummyList): 
			targetNotDiedTeamList = []
			if self.team.targeted.HP != 0: 
				targetNotDiedTeamList.append(self.team)
			if dummy_.team.targeted.HP != 0: 
				targetNotDiedTeamList.append(dummy_.team)
			self.team.battle.refreshAfterDeath(targetNotDiedTeamList)

		return effectInOneCharge, dummyList

	def attack(self): 
		background = self.team.battle.background
		oppositeTeam = self.team.oppositeTeam

		attackCount = 1+self.getSkillSum('追加攻撃')
		if self.team.battle.battleType == AUTOBATTLE: 
			attackCount += self.getSkillSum('行動増加')
			attackCount += self.getSkillSum('行動阻害')

		for ac in range(attackCount): 
			if self.HP == 0 or self.haveSkill('専守防衛'): 
				break
			elif self.abnormalStatus.魅 == 1: 
				break
			elif self.abnormalStatus.魅 == 2: 
				targetTeam = self.team
				attackSelf = True
			elif self.abnormalStatus.麻 == 2: 
				self.abnormalStatus.麻 = 0
				continue
			else: 
				targetTeam = oppositeTeam
				attackSelf = False
			
			target = targetTeam.targeted
			avoidDefend = True
			if not self.haveSkill('次元斬撃') and (not self.haveSkill('側面攻撃') or targetTeam.側面無効): 
				temp = self.haveSkill('遠隔攻撃') and not targetTeam.遠隔無効
				if not temp or ( not background.daylight and not ('夜' in self.tribe or self.haveSkill('夜戦適応')) ): 
					avoidDefend = False

			if target.isBackColumn() and not avoidDefend: 
				index = target.index-3
				target = targetTeam[index]
				while not target: 
					index = (index+1)%3
					target = targetTeam[index]

			targetDecided = False
			dummy = target.nextMember()
			if dummy: 
				if target.haveSkill('標的後逸'): 
					targetDecided = True
					dummyDeciding = '標的後逸'
				else: 
					if dummy.haveSkill('前進防御') and dummy.abnormalStatus.魅 == 0: 
						if dummy.abnormalStatus.麻 == 2: 
							dummy.abnormalStatus.麻 = 0
						else: 
							targetDecided = True
							dummyDeciding = '前進防御'
			if not targetDecided: 
				for i in range(target.index): 
					dummy = targetTeam[i]
					if dummy and dummy.haveSkill('防御布陣') and dummy.abnormalStatus.魅 == 0: 
						if dummy.abnormalStatus.麻 == 2: 
							dummy.abnormalStatus.麻 = 0
						else: 
							targetDecided = True
							dummyDeciding = '防御布陣'
							break
			if not targetDecided: 
				dummy = target
				dummyDeciding = None

			beforeHP_attacker = self.HP; beforeHP_attackee = dummy.HP
			beforeStatus_attacker = self.status.copy()
			beforeStatus_attackee = dummy.status.copy()
			recovered = [self.recovered, dummy.recovered]
			effectInOneCharge, dummyList = self.oneCharge(dummy)
			effectInOneCharge.recovered = [not recovered[0] and self.recovered, not recovered[1] and dummy.recovered]
			if effectInOneCharge.recovered[0]: 
				effectInOneCharge.recover_HP_attacker = self.HP_recovered
			effectInOneCharge.recover_HP_attackee_list = [dummy.HP_recovered for dummy in dummyList]
			effectInOneCharge.dummyDeciding = dummyDeciding
			effectInOneCharge.attackCount = ac
			effectInOneCharge.beforeHP_attacker = beforeHP_attacker
			effectInOneCharge.beforeHP_attackee = beforeHP_attackee
			effectInOneCharge.beforeStatus_attacker = beforeStatus_attacker
			effectInOneCharge.beforeStatus_attackee = beforeStatus_attackee
			effectInOneCharge.update()

			selfTeam = self.team == self.team.battle.tib1
			yield self, dummy, dummyList, effectInOneCharge, attackSelf, selfTeam
			
			if not (self.team and oppositeTeam): 
				break

class EffectInOneCharge(): 
	asList = '''虹の毒撃
封印攻撃
性的魅了
毒化攻撃
麻痺攻撃
呪の一撃
攻撃削減
防御削減
速度削減
知力削減
解除攻撃'''.split('\n')
	
	# 必殺増加、異常耐性、勇猛果敢这三个找不到图
	attackerEffectList = ['''\
複数異常
性的魅了
封印攻撃
毒化攻撃
麻痺攻撃
呪の一撃
解除攻撃
攻撃削減
防御削減
速度削減
知力削減
吸血攻撃
全域攻撃
扇形攻撃
貫通攻撃
兵種特攻
次元斬撃
遠隔攻撃
側面攻撃
カブト割
クリティカル
致命必殺
全力攻撃
反撃耐性
自爆決行'''.split('\n'), 
'''巨神体躯
巨大体躯
矮小体躯
パリング
必殺耐性
致命耐性
特攻防御
竜鱗守護
自爆耐性'''.split('\n')]
	defenderEffectList = ['''\
反撃異常
性的魅了
封印攻撃
毒化攻撃
麻痺攻撃
呪の一撃
解除攻撃
攻撃削減
防御削減
速度削減
知力削減
吸血攻撃
兵種特攻
クリティカル
致命必殺
自爆決行'''.split('\n'), 
'''巨神体躯
巨大体躯
矮小体躯
イベイド
パリング
必殺耐性
致命耐性
特攻防御
竜鱗守護
自爆耐性
専守防衛'''.split('\n')]
	
	def __init__(self): 
		self.bloodsuck2 = 0# 主目标的反击吸血
		self.bloodsuck = 0# 攻击者对主目标的吸血
		self.counterDamage = 0# 主目标的反击伤害
		self.damageList = None# 攻击者造成的伤害列表
		self.boom1 = 0# 所有被攻击者自爆伤害之和
		self.boom2 = 0# 攻击者自爆对主目标伤害
		self.recover_HP_attacker = 0# 攻击者复活恢复HP
		self.recover_HP_attackee_list = None# 被攻击者复活恢复HP

		self.tokkoubaika1 = 0
		self.tokkoubaika2 = 0
		self.hangekibaika = 0
		self.selfEffectSet = set()
		self.dummyEffectSet = set()
	def update(self): 
		if '反撃異常' in self.dummyEffectSet: 
			if not any(as_ in self.dummyEffectSet for as_ in self.asList+['吸血攻撃']): 
				self.dummyEffectSet.remove('反撃異常')
		
		def modifyTokkoubaika(tokkoubaika): 
			if tokkoubaika-int(tokkoubaika) == 0: 
				tokkoubaika = int(tokkoubaika)
			else: 
				tokkoubaika = int(tokkoubaika*10)/10
			return tokkoubaika
		self.tokkoubaika1 = modifyTokkoubaika(self.tokkoubaika1)
		self.tokkoubaika2 = modifyTokkoubaika(self.tokkoubaika2)

		self.selfEffectList_atk = sorted(set(self.attackerEffectList[0]) & self.selfEffectSet, key=self.attackerEffectList[0].index)
		self.selfEffectList_def = sorted(set(self.attackerEffectList[1]) & self.selfEffectSet, key=self.attackerEffectList[1].index)

		self.dummyEffectList_atk = sorted(set(self.defenderEffectList[0]) & self.dummyEffectSet, key=self.defenderEffectList[0].index)
		self.dummyEffectList_def = sorted(set(self.defenderEffectList[1]) & self.dummyEffectSet, key=self.defenderEffectList[1].index)

class AbnormalStatus(): 
	asStr = '毒麻呪魅封解攻防速知'
	maxValueDict = {"毒": 50, "麻": 2, "呪": 1, "魅": 2, "封": 1, "解": 1, "攻": None, "防": None, "速": None, "知": None}
	def __init__(self, 毒=0, 麻=0, 呪=0, 魅=0, 封=0, 解=0, 攻=0, 防=0, 速=0, 知=0): 
		self._毒 = 毒
		self._麻 = 麻
		self._呪 = 呪
		self._魅 = 魅
		self._封 = 封
		self._解 = 解
		self._攻 = 攻
		self._防 = 防
		self._速 = 速
		self._知 = 知

	for k, v in maxValueDict.items(): 
		exec('''\
@property
def {k}(self):
	return self._{k}'''.format(k=k))
		if v is not None: 
			exec('''\
@{k}.setter
def {k}(self, value): 
	self._{k} = min(value, {v})'''.format(k=k, v=v))
		else: 
			exec('''\
@{k}.setter
def {k}(self, value): 
	self._{k} = value'''.format(k=k, v=v))

if __name__ == "__main__": 
	from os.path import *
	import json
	with open(join(dirname(__file__), 'dat2json', 'unit.json'), 'r', encoding='utf8') as fp: 
		unitBaseList = [UnitBase(i) for i in json.load(fp)]

	ass = AbnormalStatus()
	ass.毒 += 30
	print(ass.毒)
	ass.毒 += 30
	print(ass.毒)
	ass.麻 += 30
	print(ass.麻)
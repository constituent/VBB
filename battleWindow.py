#! /usr/bin/env python3
# -*- coding: utf-8 -*-

__all__ = ['BattleWindow']

from functools import partial

from numpy import array

from core import BattleResult
from vb import *
from unitPos import *

def get_bf_pos(index, bSelf): 
	'index: 0-5'
	x, y = divmod(index, 3)
	if bSelf: 
		return array([800+200*x, 160*y-90])
	else: 
		return array([195-200*x, 160*y-90])

def get_uw_pos(index, bSelf): 
	'index: 0-5'
	x, y = divmod(index, 3)
	if bSelf: 
		return array([875+200*x, 550+55*y])
	else: 
		return array([205-200*x, 550+55*y])

def get_job(unitBase, isLeader): 
	if isLeader: 
		temp = 'job_{}L.png'.format(unitBase.job)
	else: 
		temp = 'job_{}.png'.format(unitBase.job)
	return (r'interface\btl_ui', temp)

def drawUnit(image, ub_image, vb_id, flipVertically, basepos, bZoom): 
	# 翻译自PluginBattleFunc.ks中layerUnitInfo函数
	# 三处用到，全揉在一起了所以很乱，不过懒得改了

	ub_size = ub_image.get_size()
	if ub_size[0] == 1200: 
		size = array(array(ub_size)*0.35, dtype=int)
	else: # 有560和800两种: 
		size = array(array(ub_size)*0.7, dtype=int)

	gx, gy = (personXYe_dict if flipVertically else personXYp_dict).get(vb_id, (0, 0))
	if flipVertically: 
		x = -48-gx; y = -25-gy; rx = 25; ry = 0
		if ub_size[0] == 1200: 
			x += 35
			y += 50
	else: 
		x = -80+gx; y = -25+gy; rx = 0; ry = 0

	rect_ = Rect((basepos[0]+x+rx, basepos[1]+y+ry), size)
	if bZoom is None: 
		if ub_size[0] == 1200: 
			size = ub_size
			rect = Rect((basepos[0]+x+rx, basepos[1]+y+ry), size)
			rect.center = rect_.center
		else: 
			size = ub_size
			rect = Rect((basepos[0]+x+rx, basepos[1]+y+ry), size)
	else: 
		if not bZoom and ub_size[0] == 1200: 
			size = array(array(ub_size)*0.7, dtype=int)
			rect = Rect((basepos[0]+x+rx, basepos[1]+y+ry), size)
			rect.center = rect_.center
		else: 
			rect = rect_

	image.blit(pg.transform.smoothscale(ub_image, size), rect)

class UnitDetail(MyDirtySprite): 
	title_font = pg.freetype.Font("msgothic.ttc", 15)
	name_font = pg.freetype.Font("msgothic.ttc", 18)
	attr_font = pg.freetype.Font("msgothic.ttc", 18)
	attrColors = [(255, 0, 0), (255, 186, 0), (0, 255, 192), (0, 174, 255)]
	skill_font = pg.freetype.Font("msgothic.ttc", 15)
	hp_font = pg.freetype.Font("msgothic.ttc", 12)

	as_icon_dict = {'毒': 'poison', 
		'呪': 'curse', 
		'魅': 'charm', 
		'封': 'seal', 
		'解': 'lifting'}
	def get_as_icon(name): 
		return loadImg((r'interface\btl_ui', 'icon_'+name+'.png'))
	for k, v in as_icon_dict.items(): 
		as_icon_dict[k] = get_as_icon(v)
	as_icon_dict['麻'] = [get_as_icon('paralyze'), get_as_icon('paralyze2')]
	as_icon_dict['減'] = get_as_icon('cut')
	
	def update(self, uib, flipVertically, pos): 
		image = loadImg((r'interface\btl_ui', 'pnl_unitInfo.png')).copy()
		drawUnit(image, loadImg(uib.unitBase.get_bf(), flipVertically), uib.unitBase.vb_id, flipVertically, (0, 0), True)
		image.blit(combineImg([moon_dict[d] for d in uib.divine]), (10, 5))
		self.title_font.render_to(image, (45, 5), uib.titleText, (209, 202, 193))
		image.blit(loadImg(get_job(uib.unitBase, False)), (10, 25))
		self.name_font.render_to(image, (33, 23), uib.name, (190, 167, 144))
		if uib.isLeader: 
			image.blit(loadImg((r'interface\btl_ui', 'icon_leader.png')), (10, 48))

		asList = []
		for as_ in AbnormalStatus.asStr: 
			v = getattr(uib.abnormalStatus, as_)
			if v != 0: 
				if as_ == '麻': 
					asList.append(self.as_icon_dict['麻'][v-1])
				elif as_ not in self.as_icon_dict: 
					asList.append(self.as_icon_dict['減'])
					break
				else: 
					asList.append(self.as_icon_dict[as_])
		if asList: 
			image.blit(combineImg(asList, interval=2), (15, 80))

		image.blit(combineImg([
			self.attr_font.render(s.format(uib.status[i]), self.attrColors[i])[0] for (s, i) 
			in zip([s+'[{:>4}]' for s in ('攻撃', '防御', '速度', '知力')], range(4))
			], 1, interval=2), (3, 208))

		gusha = uib.team.gushaed
		haveLeaderSkill = uib.isLeader and uib.employType == 1
		skillSurfaceList = []
		for i, skill in enumerate(uib.getSkills()): 
			if skill: 
				if i<-gusha: 
					color = (98, 98, 98)
				else: 
					if i<10: 
						color = (213, 213, 213)
					elif i<14: 
						color = (197, 162, 195)
					elif haveLeaderSkill: 
						color = (197, 82, 82)
					else: 
						break
				if skill.name == 'リカバリ' and uib.unitInTeam.recovered: 
					color = (98, 98, 98)
				skillSurfaceList.append(self.skill_font.render(skill.battleDisplay(), color)[0])
				# skillSurfaceList.append(self.skill_font.render(skill.battleDisplay(), color, style=pg.freetype.STYLE_STRONG)[0])
				# 用STYLE_STRONG的话改善不大，还会导致对齐出问题
				# 可以去找找有没有单独的font模块，或者pillow有没有字体处理功能
		skillSurfaceList.reverse()
		skillSurface = combineImg(skillSurfaceList, 1, interval=1)
		image.blit(skillSurface, (195, 288-skillSurface.get_height()))

		if uib.employType == 2: 
			image.blit(loadImg((r'interface\btl_ui', 'icon_brainwash.png')), (125, 273))

		# ###################################################
		self.attr_font.render_to(image, (10, 299), 'Lv:'+str(uib.level), (226, 226, 226))
		
		image.blit(combineImg([self.attr_font.render('成長:', (226, 226, 226))[0], 
			self.attr_font.render(uib.unitBase.growth, (231, 110, 98))[0]], interval=2), (10, 323))

		pg.draw.rect(image, (151, 227, 173), (70, 310, 200, 6))
		w = int((1-uib.HP/uib.maxHP)*200)
		if w>0: 
			pg.draw.rect(image, (250, 21, 23), (70, 310, w, 6))

		sdfdf = [self.hp_font.render('HP: ', (226, 226, 226))[0], 
			self.hp_font.render(str(uib.maxHP), (63, 188, 63))[0], 
			self.hp_font.render('/', (226, 226, 226))[0], 
			self.hp_font.render(str(uib.maxHP), (63, 188, 63))[0]
		]
		if uib.HP != uib.maxHP: 
			sdfdf[1] = self.hp_font.render(str(uib.HP), (231, 110, 98))[0]
		image.blit(combineImg(sdfdf), (70, 299))

		self.attr_font.render_to(image, (180, 323), 'Ex:'+str(uib.exp), (226, 226, 226))
		image.blit(combineImg([self.skill_font.render('属性:', (226, 226, 226))[0], 
			self.skill_font.render(uib.tribe, (205, 205, 14))[0]], interval=2), (10, 348))
		image.blit(combineImg([self.skill_font.render('特攻:', (226, 226, 226))[0], 
			self.skill_font.render(uib.special, (171, 96, 96))[0]], interval=2), (155, 348))

		equip = uib.unitBase.equip
		# 不能装备则为空字符串
		if equip[0]: 
			image.blit(loadImg((r'interface\btl_ui', 'item_icon{}.png'.format(equip[0]))), (10, 368))
			image.blit(loadImg((r'interface\btl_ui', 'item_icon{}.png'.format(equip[1]))), (10, 388))
		if uib.items[0]: 
			self.title_font.render_to(image, (30, 368), uib.items[0].name, (226, 226, 226))
		if uib.items[1]: 
			self.title_font.render_to(image, (30, 388), uib.items[1].name, (226, 226, 226))


		self.attr_font.render_to(image, (7, 448), '治療: '+str(uib.unitBase.cost), (176, 176, 152))

		self.image = image
		self.rect = self.image.get_rect(topleft=(490, 12))

class Unit_uw(RectWidget): 
	attrColors = [(255, 0, 0), (255, 186, 0), (0, 255, 192), (0, 174, 255)]
	hint_font = pg.freetype.Font("msgothic.ttc", 12)
	dead_mask = pg.Surface((200, 55), SRCALPHA, 32)
	dead_mask.fill((0, 0, 0, 120))
	def __init__(self, uib, pos, screen, unitList, window): 
		RectWidget.__init__(self, Rect(pos, (200, 55)), window, screen)
		self.uib = uib
		self.belong_unitList = unitList
	def getAttrPos(): 
		attrPos = [3]
		a = 5; b = 28
		while True: 
			attrPos.append(attrPos[-1]+a)
			if len(attrPos) == 8: 
				break
			attrPos.append(attrPos[-2]+b)
		return array(attrPos)

	attrPos1 = getAttrPos()
	attrPos2 = attrPos1+85

	class NormalState(RectWidget.DefaultState): 
		def mouse_off(self, widget): 
			if not isinstance(widget, Unit_uw): 
				self.window.unitDetail.visible = 0
			if self.hintShowing: 
				self.hintShowing = False
				self.window.hintArea.visible = 0
				# hintArea.dirty = 1#实践证明设置visible之后不必设dirty
		def showHint(self): 
			uib = self.uib
			font = self.hint_font
			str_List = [(' Lv. {} {}'+('★' if uib.isLeader else '')+' ').format(uib.level, uib.name), 
				' HP: {}/{} (行動値: {}～{}) '.format(uib.HP, uib.maxHP, *uib.actValue), 
				' 攻:{} 防:{} 速:{} 知:{} '.format(*uib.status)
			]
			asList = []
			for as_ in AbnormalStatus.asStr: 
				v = getattr(uib.abnormalStatus, as_)
				if v != 0: 
					asList.append((as_, v))
			for asl in (asList[: 5], asList[5: ]): 
				if asl: 
					str_List.append(' '+' '.join('{}:{:>2}'.format(*a) for a in asl)+' ')

			hintArea = self.window.hintArea
			hintArea.update(str_List, font)
			hintArea.visible = 1
			self.hintShowing = True

	class AttackingState(RectWidget.DefaultState): 
		pass
	AttackingState.mouse_off = NormalState.mouse_off
	AttackingState.showHint = NormalState.showHint
	
class Unit_uw_self(Unit_uw): 
	def show(self, screen=None): 
		if screen is None: 
			screen = self.screen
		uib = self.uib; pos = self.pos
		attrPos1 = Unit_uw.attrPos1

		screen.blit(loadImg(uib.unitBase.get_uw()), pos)
		pg.draw.rect(screen, (250, 21, 23), (pos[0]+3, pos[1]+2, 196, 6))# 红
		pg.draw.rect(screen, (62, 176, 93), (pos[0]+3, pos[1]+2, int(uib.HP/uib.maxHP*196), 6))# 绿

		color = (64, 248, 172) if uib.HP == uib.maxHP else (249, 65, 64)
		screen.blit(combineImg([my_font.render(str(min(uib.HP, 9999)), color)[0], 
			my_font.render('/'+str(min(uib.maxHP, 9999)), (64, 248, 172))[0]]), pos+array([20, 10]))

		for i in range(4): 
			pg.draw.rect(screen, self.attrColors[i], (pos[0]+attrPos1[2*i], pos[1]+29, 2, 7))
			attr_font.render_to(screen, pos+array([attrPos1[2*i+1], 27]), str(uib.status[i]), self.attrColors[i])

		name_font.render_to(screen, pos+array([6, 38]), uib.name, (245, 243, 241))

		screen.blit(loadImg(get_job(uib.unitBase, uib.isLeader)), pos+array([2, 11]))

		if uib.HP == 0: 
			screen.blit(self.dead_mask, self.rect)

	class NormalState(Unit_uw.NormalState): 
		default = True
		def mouse_on(self, last_widget): 
			unitDetail = self.window.unitDetail
			unitDetail.update(self.uib, False, (-80, -32))
			unitDetail.visible = 1
	class AttackingState(Unit_uw.AttackingState): 
		pass
	AttackingState.mouse_on = NormalState.mouse_on
		
class Unit_uw_enemy(Unit_uw): 
	def show(self, screen=None): 
		if screen is None: 
			screen = self.screen
		uib = self.uib; pos = self.pos
		attrPos2 = Unit_uw.attrPos2

		screen.blit(loadImg(uib.unitBase.get_uw(), True), pos)
		pg.draw.rect(screen, (62, 176, 93), (pos[0]+3, pos[1]+2, 196, 6))# 绿
		w = int((1-uib.HP/uib.maxHP)*196)
		if w>0: 
			pg.draw.rect(screen, (250, 21, 23), (pos[0]+3, pos[1]+2, w, 6))# 红

		
		color = (64, 248, 172) if uib.HP == uib.maxHP else (249, 65, 64)
		hp_surface = combineImg([my_font.render(str(min(uib.HP, 9999)), color)[0], 
			my_font.render('/'+str(min(uib.maxHP, 9999)), (64, 248, 172))[0]])
		screen.blit(hp_surface, pos+array([180-hp_surface.get_width(), 10]))

		for i in range(4): 
			pg.draw.rect(screen, self.attrColors[i], (pos[0]+attrPos2[2*i], pos[1]+29, 2, 7))
			attr_font.render_to(screen, pos+array([attrPos2[2*i+1], 27]), str(uib.status[i]), self.attrColors[i])

		name_surface, rect = name_font.render(uib.name, (245, 243, 241))
		screen.blit(name_surface, (pos[0]+194-rect.width, pos[1]+38))

		screen.blit(loadImg(get_job(uib.unitBase, uib.isLeader), True), pos+array([182, 11]))

		if uib.HP == 0: 
			screen.blit(self.dead_mask, self.rect)

	class NormalState(Unit_uw.NormalState): 
		default = True
		def mouse_on(self, last_widget): 
			unitDetail = self.window.unitDetail
			unitDetail.update(self.uib, True, (-20, -32))
			unitDetail.visible = 1
		def leftClick(self): 
			i = self.belong_unitList.targetedIndex
			if i != self.uib.index: 
				self.belong_unitList.targetedIndex = self.uib.index
				self.window.ts_enemy.pos = self.belong_unitList.targeted.pos
				self.uib.team.targeted = self.uib
				self.belong_unitList[i].show()

	class AttackingState(Unit_uw.AttackingState): 
		pass
	AttackingState.mouse_on = NormalState.mouse_on

class UnitList(): 
	def __init__(self, screen, tib, Unit, bSelf, window): 
		self.unitList = []
		self.targetedIndex = tib.targeted.index
		for i, uib in enumerate(tib): 
			if uib is not None: 
				pos = get_uw_pos(i, bSelf)
				self.unitList.append(Unit(uib, pos, screen, self, window))
			else: 
				self.unitList.append(None)
	@property
	def targeted(self): 
		return self.unitList[self.targetedIndex]
	def __getitem__(self, index): 
		return self.unitList[index]

class TargetSprite(DirtySprite): 
	targetL_List = splitImg(loadImg((r'interface\btl_ui', 'btl_targetL_a.png')), 5)
	targetR_List = splitImg(loadImg((r'interface\btl_ui', 'btl_targetR_a.png')), 5)
	def __init__(self, bSelf, pos): 
		DirtySprite.__init__(self)
		self.target_List = self.targetR_List if bSelf else self.targetL_List
		self.pos = pos
		# self.dirty = 2 # 这样其实就行了，但姑且自己来控制
		self.lastIndex = 100# 随便的一个数，只要别小于6
		self.update(0)
	@property
	def pos(self):
		return self._pos
	@pos.setter
	def pos(self, value): 
		self._pos = value
		self.posChanged = True
		self.dirty = 1
	
	def setImage(self, timePassedTotal): 
		index = timePassedTotal%1000//100
		if index == self.lastIndex or (index < 6 and self.lastIndex < 6): 
			pass
		else: 
			self.dirty = 1
			if index<6: 
				self.image = self.target_List[0]
			else: 
				self.image = self.target_List[index-5]

		self.lastIndex = index
		
	def update(self, timePassedTotal): 
		self.setImage(timePassedTotal)
		if self.posChanged: 
			self.rect = self.image.get_rect(topleft=self.pos)
			self.posChanged = False

btl_plate = loadImg(r'interface\btl_ui\btl_plate00.png')
my_font = pg.freetype.Font("msgothic.ttc", 18)
attr_font = pg.freetype.Font("msgothic.ttc", 10)
name_font = pg.freetype.Font("msgothic.ttc", 15)
signs = splitImg(loadImg((r'interface\btl_ui', 'btl_sign.png')), 3)# 加减乘号

def drawBarrier(screen, battle): 
	my_font.render_to(screen, (664, 671), str(battle.tib1.barrier), (64, 248, 172))
	barrier_surface, rect = my_font.render(str(battle.tib2.barrier), (64, 248, 172))
	screen.blit(barrier_surface, (618-rect.width, 671))

def drawSumHPBar(screen, battle): 
	pg.draw.rect(screen, (0, 0, 186), (601, 657, 100, 10))
	pg.draw.rect(screen, (238, 0, 0), (601, 657, int((battle.tib2.sumHP()/(battle.tib1.sumHP()+battle.tib2.sumHP()))*100), 10))

def drawRound(screen, battle): 
	my_font.render_to(screen, (612, 630), '{}/{}'.format(battle.roundCount-battle.elapsedRound, 
		battle.roundCount), (64, 248, 172))

as_dict = {'毒': 'poison', 
	'麻': 'paralyze', 
	'呪': 'curse', 
	'魅': 'charm', 
	'封': 'seal', 
	'解': 'lifting'
}

def draw_bf_as(img, uib): 
	# 反色等等蒙板懒得搞了
	for k in AbnormalStatus.asStr: 
		if getattr(uib.abnormalStatus, k) != 0: 
			try: 
				v = as_dict[k]
			except KeyError: 
				v = 'Weaken'
				break
			finally: 
				img.blit(loadImg((r'graphics\unit', 'aIcon_'+v+'.png')), (0, 0))

class FullWidget(Widget): 
	def __init__(self, window): 
		Widget.__init__(self, window)
	class NormalState(Widget.DefaultState): 
		pass
	class TeamEffectState(Widget.DefaultState): 
		def rightClick(self): 
			self.window.state = self.window.NormalState
	class AttackingState(Widget.DefaultState): 
		height32_list = ['カブト割', '側面攻撃', '全力攻撃', '全域攻撃', '反撃耐性', '吸血攻撃', 
			'呪の一撃', '封印攻撃', '扇形攻撃', '攻撃削減', '次元斬撃', '毒化攻撃', '知力削減', 
			'自爆決行', '致命必殺', '複数異常', '解除攻撃', '貫通攻撃', '追加攻撃', '速度削減', 
			'遠隔攻撃', '防御削減', '性的魅了', '麻痺攻撃']

		height42_list = ['イベイド', 'クリティカル', 'バリアー', 'パリング', 'リカバリ', '兵種特攻', 
			'前進防御', '反撃倍加', '反撃異常', '専守防衛', '巨大体躯', '巨神体躯', 
			'必殺耐性', '標的後逸', '特攻倍加', '特攻防御', '矮小体躯', '竜鱗守護', '自爆耐性', 
			'致命耐性', '防御陣形', 'Ｃクリ', 'Ｃパリ']
		# 182,42
		# 125,32
		# aa 42攻 aa 32攻
		# aa aa 32防 42防
		# 32攻: (1100, 275)
		# 32防：(780, 468)
		# 42攻: (400, 275)
		# 42防：(1080, 468)
		addition_number_list = splitImg(loadImg(r'interface\btl_ui\btl_Number0-9damage.png'), 10, sliceWidth=21)
		dot_img = pg.Surface((4, 31), SRCALPHA, 32)
		pg.draw.circle(dot_img, (255, 0, 0), (2, 25), 2)
		addition_number_list.append(dot_img)
		damage_number_list = splitImg(loadImg(r'interface\btl_ui\btl_Number0-9white.png'), 10, sliceWidth=21)
		recovery_number_list = splitImg(loadImg(r'interface\btl_ui\btl_Number0-9recovery.png'), 10, sliceWidth=21)
		damageFrame = loadImg(r'interface\btl_ui\btl_NunberBack_damage.png')
		normalFrame = loadImg(r'interface\btl_ui\btl_NunberBack_normal.png')
		counterFrame = loadImg(r'interface\btl_ui\btl_NunberBack_tired.png')

		screen_width = 1280
		self_pos_list = [[1100, 275], [780, 468], [400, 275], [1080, 468]]
		dummy_pos_list = [[1280-1100-125, 275], [1280-780-125, 468], [1280-400-182, 275], [1280-1080-182, 468]]
		num_left_pos_list = [(280, 214), (330, 175), (230, 180), (280, 350)]
		num_right_pos_list = [(1000, 214), (950, 175), (1050, 180), (1000, 350)]
		@staticmethod
		def getEffectImg(effectName, isAttacker=None): 
			if not isAttacker and effectName=='クリティカル': 
				effectName = 'Ｃクリ'
			elif isAttacker and effectName=='パリング': 
				effectName = 'Ｃパリ'
			if effectName=='兵種特攻': 
				effectName = '兵種特攻A' if isAttacker else '兵種特攻D'

			return loadImg(r'interface\btl_ui\pnl_{}.png'.format({'性的魅了': '魅了攻撃', 
				'防御布陣': '防御陣形'}.get(effectName, effectName)))
		@classmethod
		def getImgList(cls, effectList, isAttacker): 
			effectNameList_32 = [cls.getEffectImg(s, isAttacker) for s in effectList if s in cls.height32_list]
			effectNameList_42 = [cls.getEffectImg(s, isAttacker) for s in effectList if s in cls.height42_list]

			return effectNameList_32, effectNameList_42

		def leftClick(self): 
			window = self.window
			# 这里有大量重复代码，最后重构一下
			# 感觉可以另开一个线程乃至进程来算
			try: 
				temp = next(window.attackingGenerator)
			except StopIteration as e: 
				if e.value == BattleResult.未完: 
					window.set_bgd_normal()
					window.screen.blit(window.bgd, (0,0))
					window.bgd_teamEffect = None
					window.selfUnitList.targetedIndex = window.battle.tib1.targeted.index
					window.ts_self.pos = window.selfUnitList.targeted.pos
					window.enemyUnitList.targetedIndex = window.battle.tib2.targeted.index
					window.ts_enemy.pos = window.enemyUnitList.targeted.pos
					window.state = window.NormalState
				elif e.value is not None: 
					self.window.returnValue = e.value
			else: 
				if len(temp) == 2: 
					# 懒得显示复活的HP恢复了
					damage_list1, damage_list2 = temp
					if damage_list1: 
						for i, damage in enumerate(damage_list1): 
							if damage: 
								pos = get_uw_pos(i, True)
								if damage>0: 
									img = combineNumberImg(self.state.addition_number_list, damage)
								else: 
									img = combineNumberImg(self.state.recovery_number_list, -damage)
								window.bgd_attacking.blit(img, (pos[0]+50, pos[1]+20))
					if damage_list2: 
						for i, damage in enumerate(damage_list2): 
							if damage: 
								pos = get_uw_pos(i, False)
								if damage>0: 
									img = combineNumberImg(self.state.addition_number_list, damage)
								else: 
									img = combineNumberImg(self.state.recovery_number_list, -damage)
								rect = img.get_rect()
								rect.topright = (pos[0]+200-50, pos[1]+20)
								window.bgd_attacking.blit(img, rect.topleft)
				else: 
					attacker, attackee, attackeeList, effectInOneCharge, attackSelf, selfTeam = temp

					self_atk_list_32, self_atk_list_42 = self.state.getImgList(effectInOneCharge.selfEffectList_atk, True)
					self_def_list_32, self_def_list_42 = self.state.getImgList(effectInOneCharge.selfEffectList_def, True)
					dummy_atk_list_32, dummy_atk_list_42 = self.state.getImgList(effectInOneCharge.dummyEffectList_atk, False)
					dummy_def_list_32, dummy_def_list_42 = self.state.getImgList(effectInOneCharge.dummyEffectList_def, False)

					if effectInOneCharge.attackCount>0: 
						addition_attack_img = self.state.getEffectImg('追加攻撃').copy()
						addition_attack_img.blit(combineNumberImg(self.state.addition_number_list, effectInOneCharge.attackCount+1), 
							(100, 0))
						self_atk_list_32.append(addition_attack_img)

					if effectInOneCharge.tokkoubaika1>0: 
						tokkou_img1 = pg.Surface((195, 42), SRCALPHA, 32)
						tokkou_img1.blit(self.state.getEffectImg('特攻倍加'), (0, 0))
						tokkou_img1.blit(combineNumberImg(self.state.addition_number_list, effectInOneCharge.tokkoubaika1+1), 
							(145, 5))
						self_atk_list_42.append(tokkou_img1)

					if effectInOneCharge.tokkoubaika2>0: 
						tokkou_img2 = pg.Surface((195, 42), SRCALPHA, 32)
						tokkou_img2.blit(self.state.getEffectImg('特攻倍加'), (0, 0))
						tokkou_img2.blit(combineNumberImg(self.state.addition_number_list, effectInOneCharge.tokkoubaika2+1), 
							(145, 5))
						dummy_atk_list_42.append(tokkou_img2)

					if effectInOneCharge.hangekibaika>0: 
						hangeki_img = pg.Surface((195, 42), SRCALPHA, 32)
						hangeki_img.blit(self.state.getEffectImg('反撃倍加'), (0, 0))
						hangeki_img.blit(combineNumberImg(self.state.addition_number_list, effectInOneCharge.hangekibaika+1), 
							(145, 5))
						dummy_atk_list_42.append(hangeki_img)

					if effectInOneCharge.recovered[0]: 
						self_def_list_42.insert(0, self.state.getEffectImg('リカバリ'))
					if effectInOneCharge.recovered[1]: 
						dummy_def_list_42.insert(0, self.state.getEffectImg('リカバリ'))

					if effectInOneCharge.dummyDeciding: 
						dummy_def_list_42.insert(0, self.state.getEffectImg(effectInOneCharge.dummyDeciding))

					self_atk_32, self_atk_42 = combineImg(self_atk_list_32, 1), combineImg(self_atk_list_42, 1)
					self_def_32, self_def_42 = combineImg(self_def_list_32, 1), combineImg(self_def_list_42, 1)
					dummy_atk_32, dummy_atk_42 = combineImg(dummy_atk_list_32, 1), combineImg(dummy_atk_list_42, 1)
					dummy_def_32, dummy_def_42 = combineImg(dummy_def_list_32, 1), combineImg(dummy_def_list_42, 1)
					
					window.set_bgd_attacking(attacker, attackee, attackeeList, effectInOneCharge, attackSelf, selfTeam)

					if selfTeam: 
						pos_list = [self.state.self_pos_list, self.state.dummy_pos_list]
					else: 
						pos_list = [self.state.dummy_pos_list, self.state.self_pos_list]
					for index, img in enumerate([self_atk_32, self_def_32, self_atk_42, self_def_42]): 
						if img: 
							rect = img.get_rect()
							rect.bottomleft = pos_list[0][index]
							window.bgd_attacking.blit(img, rect.topleft)
					for index, img in enumerate([dummy_atk_32, dummy_def_32, dummy_atk_42, dummy_def_42]): 
						if img: 
							rect = img.get_rect()
							rect.bottomleft = pos_list[1][index]
							window.bgd_attacking.blit(img, rect.topleft)

					# blit numbers
					num_left_pos_list = self.state.num_left_pos_list
					num_right_pos_list = self.state.num_right_pos_list

					num_damage1_img_list = [combineNumberImg(self.state.damage_number_list, xx) for xx in effectInOneCharge.damageList]
					num_damage2_img = combineNumberImg(self.state.damage_number_list, effectInOneCharge.counterDamage)

					if selfTeam: 
						left_damage_list = num_damage1_img_list
						right_damage = num_damage2_img
						leftSize_list = [left_damage.get_size() for left_damage in left_damage_list]
						rightSize = right_damage.get_size()
						leftFrame_list = [pg.transform.smoothscale(self.state.damageFrame, (leftSize[0]+20, leftSize[1]+10)) 
							for leftSize in leftSize_list]
						for leftFrame, left_damage in zip(leftFrame_list, left_damage_list): 
							leftFrame.blit(left_damage, (10, 5))
						rightFrame = pg.transform.smoothscale(self.state.counterFrame, (rightSize[0]+20, rightSize[1]+10))
						rightFrame.blit(right_damage, (10, 5))

						left_bloodsuck = combineNumberImg(self.state.recovery_number_list, 
							effectInOneCharge.bloodsuck2) if effectInOneCharge.bloodsuck2 else None
						right_bloodsuck = combineNumberImg(self.state.recovery_number_list, 
							effectInOneCharge.bloodsuck) if effectInOneCharge.bloodsuck else None

						leftBoom = combineNumberImg(self.state.addition_number_list, 
							effectInOneCharge.boom2) if effectInOneCharge.boom2 else None
						rightBoom = combineNumberImg(self.state.addition_number_list, 
							effectInOneCharge.boom1) if effectInOneCharge.boom1 else None

						leftRecovery_list = [(combineNumberImg(self.state.recovery_number_list, 
							recover_HP_attackee) if recover_HP_attackee else None) for 
							recover_HP_attackee in effectInOneCharge.recover_HP_attackee_list]
						rightRecovery_list = [combineNumberImg(self.state.recovery_number_list, 
							effectInOneCharge.recover_HP_attacker) if effectInOneCharge.recovered[0] else None]

					else: 
						right_damage_list = num_damage1_img_list
						left_damage = num_damage2_img
						leftSize = left_damage.get_size()
						rightSize_list = [right_damage.get_size() for right_damage in right_damage_list]
						rightFrame_list = [pg.transform.smoothscale(self.state.damageFrame, (rightSize[0]+20, rightSize[1]+10)) 
							for rightSize in rightSize_list]
						for rightFrame, right_damage in zip(rightFrame_list, right_damage_list): 
							rightFrame.blit(right_damage, (10, 5))
						leftFrame = pg.transform.smoothscale(self.state.counterFrame, (leftSize[0]+20, leftSize[1]+10))
						leftFrame.blit(left_damage, (10, 5))

						left_bloodsuck = combineNumberImg(self.state.recovery_number_list, 
							effectInOneCharge.bloodsuck) if effectInOneCharge.bloodsuck else None
						right_bloodsuck = combineNumberImg(self.state.recovery_number_list, 
							effectInOneCharge.bloodsuck2) if effectInOneCharge.bloodsuck2 else None

						leftBoom = combineNumberImg(self.state.addition_number_list, 
							effectInOneCharge.boom1) if effectInOneCharge.boom1 else None
						rightBoom = combineNumberImg(self.state.addition_number_list, 
							effectInOneCharge.boom2) if effectInOneCharge.boom2 else None

						leftRecovery_list = [combineNumberImg(self.state.recovery_number_list, 
							effectInOneCharge.recover_HP_attacker) if effectInOneCharge.recovered[0] else None]
						rightRecovery_list = [(combineNumberImg(self.state.recovery_number_list, 
							recover_HP_attackee) if recover_HP_attackee else None) for 
							recover_HP_attackee in effectInOneCharge.recover_HP_attackee_list]

					if len(attackeeList) == 1: 
						if selfTeam: 
							leftFrame = leftFrame_list[0]
						else: 
							rightFrame = rightFrame_list[0]
						left_rect = leftFrame.get_rect()
						left_rect.midtop = num_left_pos_list[0]
						right_rect = rightFrame.get_rect()
						right_rect.midtop = num_right_pos_list[0]
						window.bgd_attacking.blit(leftFrame, left_rect.topleft)
						window.bgd_attacking.blit(rightFrame, right_rect.topleft)
					else: 
						# 吸血和受到的自爆伤害就照非范围攻击时显示算了，懒得弄
						if selfTeam: 
							right_rect = rightFrame.get_rect()
							right_rect.midtop = num_right_pos_list[0]
							window.bgd_attacking.blit(rightFrame, right_rect.topleft)
							for attackee, leftFrame in zip(attackeeList, leftFrame_list): 
								bf_pos = get_bf_pos(attackee.index, False)
								left_rect = leftFrame.get_rect()
								left_rect.midtop = (bf_pos[0]+120, bf_pos[1]+170)
								window.bgd_attacking.blit(leftFrame, left_rect.topleft)

						else: 
							left_rect = leftFrame.get_rect()
							left_rect.midtop = num_left_pos_list[0]
							window.bgd_attacking.blit(leftFrame, left_rect.topleft)
							for attackee, rightFrame in zip(attackeeList, rightFrame_list): 
								bf_pos = get_bf_pos(attackee.index, True)
								right_rect = rightFrame.get_rect()
								right_rect.midtop = (bf_pos[0]+253, bf_pos[1]+170)# array([373, 302])
								window.bgd_attacking.blit(rightFrame, right_rect.topleft)

					if left_bloodsuck: 
						left_bloodsuck_size = left_bloodsuck.get_size()
						left_bloodsuck_frame = pg.transform.smoothscale(self.state.normalFrame, 
							(left_bloodsuck_size[0]+20, left_bloodsuck_size[1]+10))
						left_bloodsuck_frame.blit(left_bloodsuck, (10, 5))
						left_bloodsuck_rect = left_bloodsuck_frame.get_rect()
						left_bloodsuck_rect.midtop = num_left_pos_list[1]
						window.bgd_attacking.blit(left_bloodsuck_frame, left_bloodsuck_rect.topleft)
					if right_bloodsuck: 
						right_bloodsuck_size = right_bloodsuck.get_size()
						right_bloodsuck_frame = pg.transform.smoothscale(self.state.normalFrame, 
							(right_bloodsuck_size[0]+20, right_bloodsuck_size[1]+10))
						right_bloodsuck_frame.blit(right_bloodsuck, (10, 5))
						right_bloodsuck_rect = right_bloodsuck_frame.get_rect()
						right_bloodsuck_rect.midtop = num_right_pos_list[1]
						window.bgd_attacking.blit(right_bloodsuck_frame, right_bloodsuck_rect.topleft)

					if leftBoom: 
						leftBoom_rect = leftBoom.get_rect()
						leftBoom_rect.midtop = num_left_pos_list[2]
						window.bgd_attacking.blit(leftBoom, leftBoom_rect.topleft)
					if rightBoom: 
						rightBoom_rect = rightBoom.get_rect()
						rightBoom_rect.midtop = num_right_pos_list[2]
						window.bgd_attacking.blit(rightBoom, rightBoom_rect.topleft)

					if len(leftRecovery_list) == 1: 
						leftRecovery = leftRecovery_list[0]
						if leftRecovery: 
							leftRecovery_rect = leftRecovery.get_rect()
							leftRecovery_rect.midtop = num_left_pos_list[3]
							window.bgd_attacking.blit(leftRecovery, leftRecovery_rect.topleft)
					else: 
						for attackee, leftRecovery in zip(attackeeList, leftRecovery_list): 
							if leftRecovery: 
								bf_pos = get_bf_pos(attackee.index, False)
								left_rect = leftRecovery.get_rect()
								left_rect.midtop = (bf_pos[0]+200, bf_pos[1]+170+80)
								window.bgd_attacking.blit(leftRecovery, left_rect.topleft)
					if len(rightRecovery_list) == 1: 
						rightRecovery = rightRecovery_list[0]
						if rightRecovery: 
							rightRecovery_rect = rightRecovery.get_rect()
							rightRecovery_rect.midtop = num_right_pos_list[3]
							window.bgd_attacking.blit(rightRecovery, rightRecovery_rect.topleft)
					else: 
						for attackee, rightRecovery in zip(attackeeList, rightRecovery_list): 
							if rightRecovery: 
								bf_pos = get_bf_pos(attackee.index, True)
								right_rect = rightRecovery.get_rect()
								right_rect.midtop = (bf_pos[0]+173, bf_pos[1]+132+80)
								window.bgd_attacking.blit(rightRecovery, right_rect.topleft)

					# end blit numbers

				window.screen.blit(window.bgd, (0,0))

				if window.battle.tib1 and window.battle.tib2: 
					window.selfUnitList.targetedIndex = window.battle.tib1.targeted.index
					window.ts_self.pos = window.selfUnitList.targeted.pos
					window.enemyUnitList.targetedIndex = window.battle.tib2.targeted.index
					window.ts_enemy.pos = window.enemyUnitList.targeted.pos

class BattleWindow(VB_Window): 
	attrColors = [(255, 0, 0), (255, 186, 0), (0, 255, 192), (0, 174, 255)]
	class NormalState(VB_Window.NormalState): 
		default = True
		def processOther(self): 
			if self.noEventTime>1000: 
				widget = self.widgetList.findArea(pg.mouse.get_pos())
				if not widget.hintShowing: 
					widget.showHint()

			self.ts_self.update(self.timePassedTotal)
			self.ts_enemy.update(self.timePassedTotal)

			self.group.clear(self.screen, self.bgd)
			changes = self.group.draw(self.screen)
			# 如果用pg.display.update(changes)会导致别的地方例如按钮的变化不显示
	class TeamEffectState(VB_Window.FreezeState): 
		def __setup__(self): 
			VB_Window.FreezeState.__setup__(self)
			self.fullWidget.state = self.fullWidget.TeamEffectState
		def __clear__(self): 
			VB_Window.FreezeState.__clear__(self)
			self.fullWidget.state = self.fullWidget.NormalState
		def processEvent(self): 
			for event in self.processBaseEvent(): 
				if event.type == KEYDOWN: 
					if event.key == K_ESCAPE: 
						self.state = self.NormalState
					elif (event.key == K_F4 and event.mod&KMOD_ALT): 
						self.state = self.TerminateState
	class AttackingState(VB_Window.GameState): 
		def __setup__(self): 
			VB_Window.GameState.__setup__(self)
			self.fullWidget.state = self.fullWidget.AttackingState
			for widget in self.widgetList: 
				widget.state = widget.AttackingState

		def __clear__(self): 
			VB_Window.GameState.__clear__(self)
			self.fullWidget.state = self.fullWidget.NormalState
			for widget in self.widgetList: 
				widget.state = widget.NormalState
		def processEvent(self): 
			for event in self.processBaseEvent(): 
				if event.type == KEYDOWN: 
					if event.key == K_ESCAPE or (event.key == K_F4 and event.mod&KMOD_ALT): 
						self.state = self.TerminateState
	AttackingState.processOther = NormalState.processOther

	def __init__(self, screen, battle, gameData): 
		self.fullWidget = FullWidget(self)
		VB_Window.__init__(self, screen, gameData)
		self.battle = battle
		self.background = loadImg(r'event\cg_ye_24c.bmp')
		self.selfUnitList = UnitList(screen, battle.tib1, Unit_uw_self, True, self)
		self.enemyUnitList = UnitList(screen, battle.tib2, Unit_uw_enemy, False, self)
		self.battleResult = None

		self.group = LayeredDirty()
		self.hintArea = HintArea(screen)
		self.unitDetail = UnitDetail(screen)
		self.ts_self = TargetSprite(True, self.selfUnitList.targeted.pos)
		self.ts_enemy = TargetSprite(False, self.enemyUnitList.targeted.pos)
		self.group.add(self.hintArea, self.unitDetail, self.ts_self, self.ts_enemy)
		self.group.change_layer(self.hintArea, 1)

		self.bt0 = VB_Button((r'interface\btl_ui', 'btn_bt00.png'), (516, 550), self, screen, False)
		self.bt1 = VB_Button((r'interface\btl_ui', 'btn_bt01.png'), (566, 540), self, screen)
		self.bt2 = VB_Button((r'interface\btl_ui', 'btn_bt02.png'), (566, 595), self, screen)
		self.bt3 = VB_Button((r'interface\btl_ui', 'btn_bt03.png'), (616, 530), self, screen, False)
		self.bt4 = VB_Button((r'interface\btl_ui', 'btn_bt04.png'), (666, 540), self, screen, False)
		self.bt5 = VB_Button((r'interface\btl_ui', 'btn_bt05.png'), (616, 595), self, screen)
		self.bt6 = VB_Button((r'interface\btl_ui', 'btn_bt06.png'), (666, 595), self, screen, False)
		self.bt7 = VB_Button((r'interface\btl_ui', 'btn_bt07.png'), (716, 550), self, screen)
		self.bt_close = VB_Button((r'interface\btl_ui', 'slg_bt_back.png'), (888, 12), self, screen)

		def directWin(): 
			self.returnValue = BattleResult.勝利
		def escape(): 
			self.returnValue = BattleResult.敗北

		self.bt0.leftClick = directWin
		self.bt1.leftClick = escape
		self.bt5.leftClick = partial(self.switch_state, self.TeamEffectState)
		def startAttacking(): 
			self.state = self.AttackingState
			self.attackingGenerator = self.battle.process()
			self.fullWidget.leftClick()

		self.bt7.leftClick = startAttacking# partial(self.switch_state, self.AttackingState)

		self.widgetList_normal = WidgetList(self, [self.bt0, self.bt1, self.bt2, self.bt3, self.bt4, self.bt5, 
			self.bt6, self.bt7]+self.selfUnitList.unitList+self.enemyUnitList.unitList)

		self.teamEffectPlate = loadImg((r'interface\btl_ui', 'ui_btl_plate04.png'))
		self.bt_close.leftClick = partial(self.switch_state, self.NormalState)
		self.widgetList_tep = WidgetList(self, [self.bt_close])

		self.widgetList_as = WidgetList(self, self.selfUnitList.unitList+self.enemyUnitList.unitList)

		self._bgd_normal = None
		self._bgd_teamEffect = None
		self._bgd_attacking = self.background
		self.bgd_dict = {self.NormalState: 'bgd_normal', 
			self.TeamEffectState: 'bgd_teamEffect', 
			self.AttackingState: 'bgd_attacking', 
			self.TerminateState: 'bgd_exit'}
		self.widgetList_dict = {self.NormalState: 'widgetList_normal', 
			self.TeamEffectState: 'widgetList_tep', 
			self.AttackingState: 'widgetList_as', 
			self.TerminateState: 'widgetList_dlg'}

		self.bFullScreen = False

	def draw_btl(self, bgd): 
		battle = self.battle
		bgd.blit(btl_plate, (0,0))
		for i, uib in enumerate(battle.tib1): 
			if uib is not None: 
				self.selfUnitList[i].show(bgd)

		for i, uib in enumerate(battle.tib2): 
			if uib is not None: 
				self.enemyUnitList[i].show(bgd)

		def lnd_color(lnd): 
			color=(64, 248, 172) if lnd >= 0 else (248, 64, 172)
			return (str(lnd), color)

		my_font.render_to(bgd, (664, 688), *lnd_color(battle.tib1.lnd))

		lnd_surface, rect = my_font.render(*lnd_color(battle.tib2.lnd))
		bgd.blit(lnd_surface, (618-rect.width, 688))
		drawBarrier(bgd, battle)
		drawSumHPBar(bgd, battle)
		drawRound(bgd, battle)
		bgd.blit(moon_dict[battle.background.moon], (683, 633))
		bgd.blit(daylight_img_list[1-battle.background.daylight], (699, 633))
		for i in range(8): 
			exec('self.bt'+str(i)+'.show(bgd)')

		if battle.tib2.gushaed<0: 
			bgd.blit(splitImg(loadImg((r'interface\btl_ui', 'ste_.bmp')), 29)[24], (372, 508))
			bgd.blit(signs[2], (381, 533))
			bgd.blit(splitImg(loadImg((r'interface\btl_ui', 'btl_Number0-9sp.png')), 11)[-battle.tib2.gushaed], (391, 533))
		elif battle.tib1.gushaed<0: 
			bgd.blit(splitImg(loadImg((r'interface\btl_ui', 'ste_.bmp')), 29)[24], (876, 508))
			bgd.blit(signs[2], (885, 533))
			bgd.blit(splitImg(loadImg((r'interface\btl_ui', 'btl_Number0-9sp.png')), 11)[-battle.tib1.gushaed], (895, 533))

	@classmethod
	def draw_unit_normal(cls, bgd, uib, i, bSelf, attackSelf=False): 
		bf_pos = get_bf_pos(i, bSelf)

		img = loadImg(uib.unitBase.get_bf(), bSelf if attackSelf else not bSelf).copy()
		draw_bf_as(img, uib)

		drawUnit(bgd, img, uib.unitBase.vb_id, not bSelf, bf_pos, False)

	def set_bgd_normal(self): 
		bgd = self.background.copy()
		battle = self.battle
		for i, uib in enumerate(battle.tib1): 
			if uib: 
				self.draw_unit_normal(bgd, uib, i, True)
				
		for i, uib in enumerate(battle.tib2): 
			if uib: 
				self.draw_unit_normal(bgd, uib, i, False)

		self.draw_btl(bgd)
		self._bgd_normal = bgd

	def set_bgd_teamEffect(self): 
		bgd_teamEffect = self.bgd_normal.copy()
		bgd_teamEffect.blit(self.teamEffectPlate, (362, 5))
		self.bt_close.show(bgd_teamEffect)
		for i, uib in enumerate(self.battle.tib1): 
			if uib: 
				bgd_teamEffect.blit(loadImg(uib.unitBase.get_bc_mini1()), (685+31*i, 30))
		for i, uib in enumerate(self.battle.tib2): 
			if uib: 
				bgd_teamEffect.blit(loadImg(uib.unitBase.get_bc_mini1(), True), (570-31*i, 30))

		teamEffectFont = pg.freetype.Font("msgothic.ttc", 20)

		background = self.battle.background
		teamEffectFont.render_to(bgd_teamEffect, (602, 35), 
			'時刻：'+'夜昼'[int(background.daylight)], (255, 255, 255))

		attributeList = []
		for attribute in attributeStr: 
			value = getattr(background, attribute)
			if value != 0: 
				attributeList.append((attribute, value))

		for i, (attribute, value) in enumerate(attributeList): 
			color = (136, 133, 204) if value>0 else (238, 167, 163)
			teamEffectFont.render_to(bgd_teamEffect, (388+40*i, 440), attribute, color)
			surface, rect = teamEffectFont.render('{:+}'.format(value), color)
			rect.midtop = (396+40*i, 460)
			bgd_teamEffect.blit(surface, rect.topleft)

		def filterZero(tib, skillNames): 
			skillList = []
			for skillName in skillNames: 
				value = getattr(tib, skillName)
				if value != 0: 
					skillList.append((skillName, value))
			return skillList

		for (tib, pos) in zip((self.battle.tib1, self.battle.tib2), ((650, 80), (380, 80))): 
			otherTeamSkills = filterZero(tib, ('城壁崩し', '城壁構築', '奇襲戦法', '奇襲警戒', '資源工面'))

			weakenSkills = filterZero(tib, (a+'弱体' for a in attributeFullnamelist_))
			strengthenSkills = filterZero(tib, 
				[p+t for p in propertyList for t in ('布陣', '指揮')]+['背水の陣'])
			for t in ('活性', '指揮'): 
				for a in attributeFullnamelist_: 
					skillName = a+t
					value = getattr(tib, skillName)
					if value: 
						strengthenSkills.append((skillName, sum(v[1] for v in value)))

			teamSkills_value = filterZero(tib, ['砲撃結界', '自爆結界', '対術結界', '術式増幅'])
			teamSkills_bool = [skillName for skillName in ['貫通無効', '扇形無効', '全域無効', '側面無効', '遠隔無効', 
				'解毒治療', '解呪治療', '麻痺治療', '削減治療', '兵士運搬', '地形無効'] if getattr(tib, skillName)]

			teamSkillSurface = ([teamEffectFont.render('{}:{:>3}'.format(*s), (255, 255, 255))[0] for s in otherTeamSkills]+
				[teamEffectFont.render('{}:{:>3}'.format(*s), (207, 123, 118))[0] for s in weakenSkills]+
				[teamEffectFont.render('{}:{:>3}'.format(*s), (130, 207, 118))[0] for s in strengthenSkills]+
				[teamEffectFont.render('{}:{:>3}'.format(n, int(100*v)), (163, 163, 254))[0] for (n, v) in teamSkills_value]+
				[teamEffectFont.render(s, (163, 163, 254))[0] for s in teamSkills_bool])

			for i, tss in enumerate([teamSkillSurface[: 17], teamSkillSurface[17: ]]): 
				if tss: 
					bgd_teamEffect.blit(combineImg(tss, axis=1), (pos[0]+i*130, pos[1]))

		self._bgd_teamEffect = bgd_teamEffect

	@property
	def bgd_teamEffect(self):
		if self._bgd_teamEffect is None: 
			self.set_bgd_teamEffect()
		return self._bgd_teamEffect

	@bgd_teamEffect.setter
	def bgd_teamEffect(self, value): 
		self._bgd_teamEffect = value

	def set_bgd_attacking(self, attacker, attackee, attackeeList, effectInOneCharge, attackSelf, selfTeam): 
		def fillPanel(btl_panel, uib1, uib2, beforeHP1, beforeHP2, beforeStatus1, beforeStatus2): 
			attr_font = pg.freetype.Font("msgothic.ttc", 12)
			name_font = pg.freetype.Font("msgothic.ttc", 18)
			hp_font = pg.freetype.Font("msgothic.ttc", 15)

			pos = [((495, 64), (495, 82), (495, 100), (495, 118)), 
				((191, 64), (191, 82), (191, 100), (191, 118))]
			for i, (uib, beforeStatus) in enumerate(zip([uib1, uib2], [beforeStatus1, beforeStatus2])): 
				for j in range(4): 
					attr_font.render_to(btl_panel, pos[i][j], str(beforeStatus[j]), self.attrColors[j])
				name_font.render_to(btl_panel, [(429, 137), (126, 137)][i], uib.name, [(207, 207, 111), (244, 122, 120)][selfTeam-i])
				hp_font.render_to(btl_panel, [(429, 115), (239, 115)][i], str([beforeHP1, beforeHP2][i]), (64, 253, 176))

		bgd = self.background.copy()

		damageList = effectInOneCharge.damageList

		# img1是自己这边画的单位，img2是敌人那边画的单位
		if selfTeam: 
			uib1 = attacker; uib2 = attackee
			img1 = loadImg(attacker.unitBase.get_bf()).copy()
			draw_bf_as(img1, attacker)
			btl_panel = loadImg(r'interface\btl_ui\btl_panelBattleR.png').copy()
			fillPanel(btl_panel, attacker, attackee, effectInOneCharge.beforeHP_attacker, effectInOneCharge.beforeHP_attackee, 
				effectInOneCharge.beforeStatus_attacker, effectInOneCharge.beforeStatus_attackee)
		else: 
			uib1 = attackee; uib2 = attacker
			img2 = loadImg(attacker.unitBase.get_bf(), True).copy()
			draw_bf_as(img2, attacker)
			btl_panel = loadImg(r'interface\btl_ui\btl_panelBattleL.png').copy()
			fillPanel(btl_panel, attackee, attacker, effectInOneCharge.beforeHP_attackee, effectInOneCharge.beforeHP_attacker, 
				effectInOneCharge.beforeStatus_attackee, effectInOneCharge.beforeStatus_attacker)
		
		if effectInOneCharge.dummyDeciding: 
			target = attackee.team.targeted
			img3 = loadImg(target.unitBase.get_bf(), not attackSelf if selfTeam else attackSelf).copy()
			draw_bf_as(img3, target)
		else: 
			img3 = None

		pos1 = (650, 50); pos2 = (100, 50)
		if len(damageList) == 1: 
			if selfTeam: 
				img2 = loadImg(attackee.unitBase.get_bf(), not attackSelf).copy()
				draw_bf_as(img2, attackee)
			else: 
				img1 = loadImg(attackee.unitBase.get_bf(), attackSelf).copy()
				draw_bf_as(img1, attackee)

			if img3: 
				if selfTeam: 
					pos3 = (pos2[0]-100, pos2[1])
				else: 
					pos3 = (pos1[0]+100, pos1[1])
				drawUnit(bgd, img3, target.unitBase.vb_id, not selfTeam, pos3, None)
			drawUnit(bgd, img1, uib1.unitBase.vb_id, False, pos1, None)
			drawUnit(bgd, img2, uib2.unitBase.vb_id, True, pos2, None)
		else: 
			for index, attackee in enumerate(attackeeList): 
				self.draw_unit_normal(bgd, attackee, attackee.index, not selfTeam, attackSelf)
			if selfTeam: 
				drawUnit(bgd, img1, uib1.unitBase.vb_id, False, pos1, None)
			else: 
				drawUnit(bgd, img2, uib2.unitBase.vb_id, True, pos2, None)

		self.draw_btl(bgd)
		bgd.blit(btl_panel, (280, -40))
		self._bgd_attacking = bgd

	@property
	def bgd_attacking(self):
		return self._bgd_attacking

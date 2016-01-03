#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import pickle
from functools import partial, wraps
from contextlib import contextmanager

from core.basicVariable import *
from core import UnitBase, Unit, AbnormalStatus, Team, exchangeMember

from basicWindow import *

job_dict = {}
temp = splitImg(loadImg((r'interface\slg_ui', 'rORG_chip01.png')), len(UnitBase.jobStr))
for i, v in enumerate(UnitBase.jobStr): 
	job_dict[v] = temp[i]

daylight_img_list = splitImg(loadImg((r'interface\slg_ui', 'root_chip01.png')), 2)

moon_dict = {}
temp = splitImg(loadImg((r'interface\slg_ui', 'rORG_chip03.png')), len(DIVINES))
for i, v in enumerate(DIVINES): 
	moon_dict[v] = temp[i]

resource_list = splitImg(loadImg((r'interface\btl_ui', 'icon04x4.png')), 4)

medal_list = splitImg(loadImg((r'interface\slg_ui', 'draft_chipt000.png')), 41)

class VB_Button(RectButton): 
	def __init__(self, picPath, pos, window, screen, available=True, parent=None): 
		self.ori_img = loadImg(picPath)
		RectButton.__init__(self, splitImg(self.ori_img, 3), pos, window, screen, parent=None)
		self.index = 1 if self.available else 0
		self.imgList[1] = self.imgList[0]
		self.mouse_on_index = 2
		self.mouse_off_index = 1

class Root_Button(RectButton): 
	def __init__(self, picPath, pos, window, screen, available=True, parent=None): 
		self.ori_img = loadImg(picPath)
		RectButton.__init__(self, splitImg(self.ori_img, 3), pos, window, screen, parent=None)
		self.index = 0
		self.mouse_on_index = 2
		self.mouse_off_index = 0

class VB_Window(MouseEvents): 
	class NormalState(MouseEvents.GameState): 
		default = True
		def __setup__(self): 
			MouseEvents.GameState.__setup__(self)
		def processEvent(self): 
			for event in self.processBaseEvent(): 
				if event.type == KEYDOWN: 
					if event.key == K_ESCAPE or (event.key == K_F4 and event.mod&KMOD_ALT): 
						self.state = self.TerminateState
					elif event.key == K_F2: 
						print('save')
						with open(join(dirname(__file__), 'save.dat'), 'wb') as fout: 
							# print(type(self.gameData))
							# print(self.gameData.moon)
							# print(self.gameData.daylight)
							# print(self.gameData.teamList)
							pickle.dump(self.gameData, fout)
					elif event.key == K_F3: 
						print('load')
						with open(join(dirname(__file__), 'save.dat'), 'rb') as fin: 
							self.gameData = pickle.load(fin)
						self.returnValue = WindowType.HireUnitWindow
		
	class TerminateState(MouseEvents.TerminateState): 
		def __setup__(self): 
			MouseEvents.FreezeState.__setup__(self)

	_notReturn = object()

	def __init__(self, screen, gameData): 
		MouseEvents.__init__(self, screen)
		self.returnValue = self._notReturn
		self.gameData = gameData
		self.moon = gameData.moon
		self.daylight = gameData.daylight

		self.dlog = loadImg((r'interface\sys_ui', 'ui_dlog_bt.png'))
		self.bt_yes = VB_Button((r'interface\sys_ui', 'ui_dlog_bt_yes.png'), (463, 495), self, screen)
		self.bt_no = VB_Button((r'interface\sys_ui', 'ui_dlog_bt_no.png'), (640, 495), self, screen)
		self.bt_yes.leftClick = partial(self.terminate)
		# self.bt_no.leftClick = partial(self.switch_state, self.lastState)
		self.bt_no.leftClick = lambda: self.switch_state(self.lastState)
		self.widgetList_dlg = WidgetList(self, [self.bt_yes, self.bt_no])

		self.bgd_dict = {self.TerminateState: 'bgd_exit'}
		self.widgetList_dict = {self.TerminateState: 'widgetList_dlg'}

	def set_root_pnl(self, screen): 
		def next_turn(): 
			self.gameData.moon, self.gameData.daylight = next_moon_daylight(self.gameData.moon, self.gameData.daylight)
			self.returnValue = WindowType.HireUnitWindow
		def switch_organize(): 
			self.returnValue = WindowType.OrganizeTeamWindow
		def switch_hire(): 
			self.returnValue = WindowType.HireUnitWindow
		def switch_battle(): 
			if any(team for team in self.gameData.teamList): 
				self.returnValue = WindowType.BattleWindow
		def switch_item(): 
			self.returnValue = WindowType.ItemWindow

		self.bt_nextTurn = VB_Button((r'interface\slg_ui', 'root_bt30.png'), (835, 690), self, screen)
		self.bt_campaign = Root_Button((r'interface\slg_ui', 'root_bt20.png'), (980, 670), self, screen)
		self.bt_organizeTeam = Root_Button((r'interface\slg_ui', 'root_bt21.png'), (1030, 670), self, screen)
		self.bt_item = Root_Button((r'interface\slg_ui', 'root_bt22.png'), (1080, 670), self, screen)
		self.bt_hire = Root_Button((r'interface\slg_ui', 'root_bt23.png'), (1130, 670), self, screen)

		self.bt_nextTurn.leftClick = next_turn
		self.bt_organizeTeam.leftClick = switch_organize
		self.bt_item.leftClick = switch_item
		self.bt_hire.leftClick = switch_hire
		self.bt_campaign.leftClick = switch_battle

	def draw_root_pnl(self, bgd): 
		i = DIVINES.index(self.moon)
		bgd.blit(moon_dict[self.moon], (591+16*i, 697))
		bgd.blit(daylight_img_list[1-self.daylight], (567, 697))

		for bt in [self.bt_nextTurn, self.bt_campaign, self.bt_organizeTeam, self.bt_item, self.bt_hire]: 
			bt.show(bgd)

	@property
	def widgetList(self): 
		return getattr(self, self.widgetList_dict[self.state])

	@property
	def bgd(self): 
		return getattr(self, self.bgd_dict[self.state])

	@property
	def bgd_normal(self): 
		if self._bgd_normal is None: 
			self.set_bgd_normal()
		return self._bgd_normal

	def freeze_dlg(self, text, pos): 
		bgd_freeze = getattr(self, self.bgd_dict[self.lastState]).copy()
		bgd_freeze.blit(self.dlog, (340, 124))
		pg.freetype.Font("msgothic.ttc", 30).render_to(bgd_freeze, pos, text, (255, 255, 255))
		self.bt_yes.show(bgd_freeze)
		self.bt_no.show(bgd_freeze)

		return bgd_freeze

	def set_bgd_exit(self): 
		self._bgd_exit = self.freeze_dlg('終了しますか？', (550, 255))

	@property
	def bgd_exit(self):
		self.set_bgd_exit()
		return self._bgd_exit

	def run(self): 
		clock = pg.time.Clock()
		self.timePassedTotal = 0
		self.screen.blit(self.bgd, (0,0))
		self.noEventTime = 0
		_notReturn = self._notReturn
		while self.returnValue is _notReturn: 
			passedTime = clock.tick(30)
			self.noEventTime += passedTime
			self.timePassedTotal += passedTime
			self.timePassedTotal = self.timePassedTotal%100000# 以免万一溢出了
			
			self.processEvent()
			self.processOther()
			pg.display.update()

		return self.returnValue

WindowType = Enum('WindowType', 'HireUnitWindow OrganizeTeamWindow BattleWindow ItemWindow')

class GameData(): 
	'''所有游戏数据，即存档需要保存的'''
	def __init__(self, moon, daylight, itemList): 
		self.moon = moon
		self.daylight = daylight
		self.hiredUnitList = []
		self.teamList = [Team(i) for i in range(99)]

		self.item_possession = {item: item.limit for item in itemList}
		self.item_equipped = {item: 0 for item in itemList}
		# 还有难度、模式等等
	def item_left(self, item): 
		return self.item_possession[item]-self.item_equipped[item]

DEFAULT_BGM = get_bgm_path('default.ogg')

@contextmanager
def play_bgm(bgm_file_path): 
	if bgm_file_path is not None: 
		if not isfile(bgm_file_path): 
			bgm_file_path = DEFAULT_BGM
		with open(bgm_file_path, 'rb') as f: 
			pg.mixer.music.load(f)
			pg.mixer.music.play(-1)
			yield
			pg.mixer.music.stop()
	else: 
		yield

def moon_daylight_iterator(): 
	for moon in DIVINES: 
		for daylight in (True, False): 
			yield moon, daylight
moon_daylight_list = list(moon_daylight_iterator())
moon_daylight_dict = {item: index for (index, item) in enumerate(moon_daylight_list)}
moon_daylight_dict_reversed = {v: k for k, v in moon_daylight_dict.items()}
def next_moon_daylight(moon, daylight): 
	return moon_daylight_dict_reversed[(moon_daylight_dict[moon, daylight]+1)%12]

class UnitDetailMixin(): 
	cost_font = pg.freetype.Font("msgothic.ttc", 16)
	name_font = pg.freetype.Font("msgothic.ttc", 20)
	lv_font = name_font
	unitDetailRect = Rect((0, 0), (1280, 200))
	attrColors = [(255, 0, 0), (255, 186, 0), (0, 255, 192), (0, 174, 255)]
	def _drawDetail(self, unit): 
		ub = unit.unitBase
		bgd = self.window.bgd

		bgd.blit(loadImg(ub.get_fc()), (205, 20))
		self.cost_font.render_to(bgd, (366, 10), unit.titleText, (255, 255, 255))
		self.name_font.render_to(bgd, (365, 30), ub.name, (255, 163, 0))
		bgd.blit(job_dict[ub.job], (365, 62))
		self.lv_font.render_to(bgd, (385, 62), 'Lv:'+str(unit.level), (255, 255, 255))
		self.lv_font.render_to(bgd, (365, 86), 'HP:{}/{}'.format(unit.HP, unit.maxHP), (255, 255, 255))
		pg.draw.rect(bgd, (250, 21, 23), ((365, 105), (180, 3)))
		if unit.HP>0: 
			pg.draw.rect(bgd, (151, 227, 173), ((365, 105), (int(unit.HP/unit.maxHP*180), 3)))
		equip = ub.equip
		# VBG的神兽啥的没装备
		if equip[0]: 
			bgd.blit(loadImg((r'interface\btl_ui', 'item_icon{}.png'.format(equip[0]))), (365, 110))
			bgd.blit(loadImg((r'interface\btl_ui', 'item_icon{}.png'.format(equip[1]))), (365, 130))
		for equip, pos in zip(unit.items, [(385, 110), (385, 130)]): 
			if equip: 
				self.cost_font.render_to(bgd, pos, equip.name, (255, 255, 255))


		tempList = ['経験値:'+str(unit.exp), '成長  :'+ub.growth, '治療費:'+str(ub.cost)]
		tempList = [self.cost_font.render(item, (255, 255, 255))[0] for item in tempList]
		temp = self.cost_font.render('報酬', (255, 255, 255))[0]
		tempList.append(combineImg((temp, resource_list[unit.pay-1])))
		bgd.blit(combineImg(tempList, 1, interval=4), (565, 10))

		tempList = []
		for i, (st, color) in enumerate(zip(['攻撃', '防御', '速度', '知力'], self.attrColors)): 
			tempList.append(self.cost_font.render('{}:{:3}'.format(st, unit.status[i]), color)[0])
		temp = self.cost_font.render('加護:', (255, 255, 255))[0]
		tempList.append(combineImg([temp, *(moon_dict[d] for d in unit.divine)]))
		tempList.append(self.cost_font.render('種族:'+unit.tribe, (255, 255, 255))[0])
		for i, t in enumerate([unit.special[: 6], unit.special[6: ]]): 
			tempList.append(self.cost_font.render({0: '特攻:', 1: '　　 '}[i]+t, (255, 255, 255))[0])
		bgd.blit(combineImg(tempList, 1, interval=3), (700, 30))

		if unit.employType == 2: 
			bgd.blit(loadImg((r'interface\btl_ui', 'icon_brainwash.png')), (790, 180))

		skills = unit.getSkills()
		bgd.blit(combineImg([self.cost_font.render(str(skill), (255, 255, 255))[0] for 
			skill in skills[: 8]], 1, interval=3), (850, 30))
		tempList = []
		for skill in skills[8: 10]: 
			tempList.append(self.cost_font.render(str(skill), (1, 243, 182))[0])
		for skill in skills[10: 14]: 
			tempList.append(self.cost_font.render(str(skill), (197, 162, 195))[0])
		for skill in skills[14: ]: 
			tempList.append(self.cost_font.render(str(skill), (231, 165, 4))[0])
		bgd.blit(combineImg(tempList, 1, interval=3), (970, 30))

class VScrollBar(RectWidget): 
	class Active(RectWidget.DefaultState): 
		def mouseCatch(self): 
			pos_h = pg.mouse.get_pos()[1]
			if self.showingStart<=pos_h<self.showingEnd: 
				self.catchPos = pos_h
			else: 
				# 点击空白处自行滚动懒得写了
				self.catchPos = pos_h
		def mouseDrag(self): 
			# 如果快速拖动还有一些小问题，不管了
			pos_h = pg.mouse.get_pos()[1]
			lineHeight = int(self.height/max(len(self.parent.itemLine_list), 6))
			count = int((pos_h-self.catchPos)/(lineHeight))
			if count>0: 
				self.parent.wheelDown(count)
				self.catchPos = pos_h
			elif count<0: 
				self.parent.wheelUp(-count)
				self.catchPos = pos_h
		def leftClick(self): 
			pos_h = pg.mouse.get_pos()[1]
			if pos_h>=self.showingEnd: 
				self.parent.wheelDown()
			elif pos_h<self.showingStart: 
				self.parent.wheelUp()
		def show(self, screen=None): 
			if screen is None: 
				screen = self.screen
			screen.blit(self.window.bgd_base.subsurface(self.rect), self.rect)

			height = self.showHeight
			pos_h = self.pos[1]+int((self.height-height)/(len(self.parent.itemLine_list)
				-len(self.parent))*self.parent.startLine)

			rect = Rect((self.pos[0], pos_h), (self.width, height))
			screen.fill(self.color, rect)
			self.showingStart = pos_h
			self.showingEnd = pos_h+height

	class Inactive(RectWidget.DefaultState): 
		default = True
		def show(self, screen=None): 
			if screen is None: 
				screen = self.screen
			screen.blit(self.window.bgd_base.subsurface(self.rect), self.rect)
	def __init__(self, color, rect, window, screen, parent): 
		RectWidget.__init__(self, rect, window, screen, parent)
		self.color = color
	def setState(self): 
		if self.parent.itemLine_list: 
			self.showHeight = int(min(len(self.parent)/len(self.parent.itemLine_list), 1)*self.height)
		else: 
			self.showHeight = self.height
		
		if self.showHeight == self.height: 
			self.state = self.Inactive
		else: 
			self.state = self.Active

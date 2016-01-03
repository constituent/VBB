#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import copy

from vb import *
from unitPanel import *

AllUnitArea = AllUnitArea_

class FullWidget(Widget): 
	def __init__(self, window): 
		Widget.__init__(self, window)
	def mouseDrop(self, dragging): 
		# 可以优化
		self.window.screen.blit(self.window.bgd, (0, 0))

class UnitArea(UnitArea_): 
	@property
	def available(self): 
		return not self.unit.inTeam

	def show(self, screen=None): 
		if screen is None: 
			screen = self.screen
		if self.unit is None: 
			screen.fill((0, 0, 0), self.rect)
		else: 
			screen.blit(self.getImg(), self.pos)
			if not self.available: 
				screen.blit(self.mask_surface, self.rect)
	
	def mouseDrag(self): 
		if self.unit and self.available: 
			img = loadImg(self.unit.unitBase.get_bc_mini1())
			self.screen.blit(self.window.bgd, (0, 0))
			self.screen.blit(img, pg.mouse.get_pos())

	def leftDoubleClick(self): 
		if self.unit and self.available: 
			self.window.unitArea_to_dismiss = self
			self.window.state = self.window.DismissState

class TeamIndexArea(RectWidget): 
	teamIndex_font = pg.freetype.Font("msgothic.ttc", 20)
	imgList = splitImg(loadImg(r'interface\slg_ui\rORG_btNo00.png'), 3)
	def __init__(self, rect, window, screen, parent): 
		RectWidget.__init__(self, rect, window, screen, parent)
		self.teamIndex_pos = (self.pos[0]+7, self.pos[1]+7)
		self.img_index = 0
	def show(self, screen=None): 
		if screen is None: 
			screen = self.screen
		if self.parent.team: 
			screen.blit(self.imgList[self.img_index], self.rect)
		else: 
			blit_sameRect(screen, self.window.bgd_base, self.rect)
		self.teamIndex_font.render_to(screen, self.teamIndex_pos, '{:>2}'.format(self.parent.team.index+1), (255, 255, 255))
	def mouse_on(self, last_widget): 
		if self.parent.team: 
			self.img_index = 2
			self.show()
	def mouse_off(self, widget): 
		if self.parent.team: 
			self.img_index = 0
			self.show()
	def mouseDrag(self): 
		if self.parent.team: 
			img = self.window.bgd.subsurface(self.parent.mainRect)
			self.screen.blit(self.window.bgd, (0, 0))

			widget = self.window.widgetList.findArea(pg.mouse.get_pos())
			if isinstance(widget.parent, TeamLine): 
				widget = widget.parent
			if isinstance(widget, TeamLine): 
				self.screen.blit(widget.mask_surface, widget.rect)

			self.screen.blit(img, pg.mouse.get_pos())

	def leftDoubleClick(self): 
		if self.parent.team: 
			self.window.teamLine_to_disband = self.parent
			self.window.state = self.window.DisbandState

class TeamArea(RectWidget, UnitDetailMixin): 
	'''
	师团区域中的一个小格子，宽30，高32（最顶两像素表示是否是队长）
	好多名字都取得容易混淆，懒得改了～～
	'''
	def __init__(self, window, index, screen, parent): 
		self.index = index
		i, j = index
		pos = (495+30*j, 228+35*i)
		rect = Rect(pos, (30, 32))
		self.leaderRect = Rect(pos, (30, 2))
		self.mainRect = Rect((pos[0], pos[1]+2), (30, 30))
		RectWidget.__init__(self, rect, window, screen, parent)
		self.uit = None
	def __bool__(self): 
		return self.uit is not None
	def showLeader(self, screen=None): 
		if screen is None: 
			screen = self.screen
		if self.uit.isLeader: 
			screen.fill((255, 255, 0), self.leaderRect)
		else: 
			blit_sameRect(screen, self.window.bgd_base, self.leaderRect)
	def show(self, screen=None): 
		if screen is None: 
			screen = self.screen
		if self.uit is None: 
			blit_sameRect(self.window.bgd, self.window.bgd_base, self.rect)
		else: 
			ub = self.uit.unitBase
			img = loadImg(ub.get_bc_mini1())
			screen.blit(img, (self.pos[0], self.pos[1]+2))
			self.showLeader(screen)

	def mouse_on(self, last_widget): 
		if self.uit is None: 
			return
		pg.draw.rect(self.screen, (255, 0, 0), self.mainRect, 1)
		self.drawDetail()

	def mouse_off(self, widget): 
		self.clearDetail()
		self.screen.blit(self.window.bgd.subsurface(self.rect), self.rect)

	def drawDetail(self): 
		self._drawDetail(self.uit.unit)
		blit_sameRect(self.screen, self.window.bgd, self.unitDetailRect)
		# self.screen.blit(self.window.bgd, (0, 0))

	def clearDetail(self): 
		if self.uit: 
			blit_sameRect(self.window.bgd, self.window.bgd_base, self.unitDetailRect)
			blit_sameRect(self.screen, self.window.bgd, self.unitDetailRect)
			# self.screen.blit(self.window.bgd, (0, 0))

	def mouseDrag(self): 
		if self.uit: 
			img = loadImg(self.uit.unitBase.get_bc_mini1())
			self.screen.blit(self.window.bgd, (0, 0))
			self.screen.blit(img, pg.mouse.get_pos())

	def mouseDrop(self, dragging): 
		if isinstance(dragging, UnitArea) and dragging and dragging.available: 
			self.leftDoubleClick()
			self.parent.team.addMember(dragging.unit, self.index[1])
			self.uit = self.parent.team[self.index[1]]
			self.show(self.window.bgd)
			dragging.unit.inTeam = True
			self.window.bgd.blit(dragging.mask_surface, dragging.rect)
			self.parent.teamIndexArea.show(self.window.bgd)
			self.screen.blit(self.window.bgd, (0, 0))
		elif isinstance(dragging, self.__class__) and dragging: 
			newLeaderIndex = exchangeMember(dragging.parent.team, dragging.index[1], self.parent.team, self.index[1])
			if newLeaderIndex: 
				dragging.parent[newLeaderIndex].showLeader(self.window.bgd)
			self.uit, dragging.uit = dragging.uit, self.uit
			self.show(self.window.bgd); self.parent.teamIndexArea.show(self.window.bgd)
			dragging.show(self.window.bgd); dragging.parent.teamIndexArea.show(self.window.bgd)
			self.screen.blit(self.window.bgd, (0, 0))
		else: 
			self.parent.mouseDrop(dragging)

	def leftDoubleClick(self): 
		if self.uit: 
			self.uit.unit.inTeam = False
			unitArea = self.window.allUnitArea.searchUnit(self.uit.unit)
			if unitArea: 
				unitArea.show(self.window.bgd)
			self.uit = None
			newLeaderIndex = self.parent.team.removeMember(self.index[1])
			if newLeaderIndex: 
				self.parent[newLeaderIndex].showLeader(self.window.bgd)
			self.show(self.window.bgd); self.parent.teamIndexArea.show(self.window.bgd)
			self.screen.blit(self.window.bgd, (0, 0))

	def wheelClick(self): 
		if self.uit and not self.uit.isLeader: 
			old_leaderIndex = self.parent.team.changeLeader(self.index[1])
			self.showLeader(self.window.bgd)
			self.parent[old_leaderIndex].showLeader(self.window.bgd)
			self.screen.blit(self.window.bgd, (0, 0))

class TeamLine(Line_of_VScrollArea): 
	size = (70+30*6, 32)
	mask_surface = pg.Surface(size, SRCALPHA, 32)
	mask_surface.fill((255, 0, 0, 150))
	def __init__(self, i, window, screen, parent): 
		rect = Rect((425, 228+35*i), self.size)
		Line_of_VScrollArea.__init__(self, rect, window, screen, parent)
		self.mainRect = Rect((495, 230+35*i), (30*6, 30))
		self.team = None
	@property
	def index(self): 
		return self.team.index
	def __iter__(self): 
		return self.teamAreaList.__iter__()
	def __getitem__(self, key): 
		return self.teamAreaList[key]
	def show(self, screen=None): 
		if screen is None: 
			screen = self.screen
		self.teamIndexArea.show(screen)
		for uit, teamArea in zip(self.team, self): 
			teamArea.uit = uit
			teamArea.show(screen)
	def mouseDrop(self, dragging): 
		if (isinstance(dragging, TeamIndexArea) and dragging.parent.team): 
			if dragging.parent != self: 
				i1, i2 = dragging.parent.index, self.index
				self.team.index = i1
				dragging.parent.team.index = i2
				teamList = self.window.teamList
				teamList[i1], teamList[i2] = teamList[i2], teamList[i1]
				dragging.parent.team, self.team = teamList[i1], teamList[i2]
				dragging.parent.show(self.window.bgd)
				self.show(self.window.bgd)
			self.screen.blit(self.window.bgd, (0, 0))
		else: 
			self.parent.mouseDrop(dragging)

class AllTeamArea(Monoheight_VScrollArea): 
	def __init__(self, rect, window, screen, parent): 
		Monoheight_VScrollArea.__init__(self, rect, window, screen, parent)
		self.scrollBar = VScrollBar((255, 255, 255), Rect((677, 228), (3, 417)), window, screen, self)
	def __iter__(self): 
		return self.teamAreaLine_list.__iter__()
	def __len__(self): 
		return 12
	def __getitem__(self, key): 
		return self.teamAreaLine_list[key]
	def show(self, screen=None): 
		if screen is None: 
			screen = self.screen
		startLine = self.startLine
		for teamLine, teamAreaLine in zip(self.itemLine_list[startLine: startLine+12], self): 
			teamAreaLine.team = teamLine
			teamAreaLine.show(screen)

		self.scrollBar.show(screen)
	def wheelUp(self, lineCount=1): 
		Monoheight_VScrollArea.DefaultState.wheelUp(self, lineCount)
		widget = self.window.widgetList.findArea(pg.mouse.get_pos())
		widget.mouse_on(None)
	def wheelDown(self, lineCount=1): 
		Monoheight_VScrollArea.DefaultState.wheelDown(self, lineCount)
		widget = self.window.widgetList.findArea(pg.mouse.get_pos())
		widget.mouse_on(None)

class OrganizeTeamWindow(VB_Window, UnitPanelMixin): 
	class DismissState(VB_Window.FreezeState): 
		pass
	class DisbandState(VB_Window.FreezeState): 
		pass

	def __init__(self, gameData, screen): 
		self.fullWidget = FullWidget(self)
		VB_Window.__init__(self, screen, gameData)
		self.hiredUnitList = gameData.hiredUnitList
		self.teamList = gameData.teamList
		self.unitArea_to_dismiss = None
		self.teamLine_to_disband = None

		self.set_root_pnl(screen)
		self.root_bt_list = [self.bt_nextTurn, self.bt_campaign, self.bt_item, self.bt_hire]
		self.bt_organizeTeam.index = 1
		
		self.setAllUnitArea(UnitArea, AllUnitArea)

		self.allTeamArea = AllTeamArea(Rect((425, 228), (70+185, 417)), self, screen, self.fullWidget)
		self.allTeamArea.teamAreaLine_list = [TeamLine(i, self, screen, 
			self.allTeamArea) for i in range(12)]
		for i, teamAreaLine in enumerate(self.allTeamArea.teamAreaLine_list): 
			teamAreaLine.teamIndexArea = TeamIndexArea(Rect((425, 230+35*i), (30, 30)), self, screen, teamAreaLine)
			teamAreaList = []
			for j in range(6): 
				teamAreaList.append(TeamArea(self, (i, j), screen, teamAreaLine))
			teamAreaLine.teamAreaList = teamAreaList

		self.widgetList_normal = WidgetList(self, [self.allUnitArea, self.allTeamArea]+self.root_bt_list)
		self.bt_dismiss = copy.copy(self.bt_yes)
		self.bt_dismiss.leftClick = partial(self.dismissUnit)
		self.widgetList_dismiss = WidgetList(self, [self.bt_dismiss, self.bt_no])
		self.bt_disband = copy.copy(self.bt_yes)
		self.bt_disband.leftClick = partial(self.disbandTeam)
		self.widgetList_disband = WidgetList(self, [self.bt_disband, self.bt_no])

		self.backgroundImg = loadImg(r'event\cg_ye_24c.bmp')
		self.set_bgd_base()
		self._bgd_normal = None
		self.bgd_dict.update({self.NormalState: 'bgd_normal', 
			self.DismissState: 'bgd_dismiss', 
			self.DisbandState: 'bgd_disband', 
			})
		self.widgetList_dict.update({self.NormalState: 'widgetList_normal', 
			self.DismissState: 'widgetList_dismiss', 
			self.DisbandState: 'widgetList_disband', 
			})
		self.bFullScreen = False

	def dismissUnit(self): 
		self.state = self.NormalState
		for equip in self.unitArea_to_dismiss.unit.items: 
			if equip is not None: 
				self.gameData.item_equipped[equip] -= 1
		self.hiredUnitList.pop(self.hiredUnitList.index(self.unitArea_to_dismiss.unit))
		blit_sameRect(self.bgd, self.bgd_base, UnitDetailMixin.unitDetailRect)
		self.setUnit()
		self.screen.blit(self.bgd, (0, 0))

	def disbandTeam(self): 
		self.state = self.NormalState
		for teamArea in (teamArea for teamArea in self.teamLine_to_disband if teamArea): 
			teamArea.uit.unit.inTeam = False
			unitArea = self.allUnitArea.searchUnit(teamArea.uit.unit)
			if unitArea: 
				unitArea.show(self.bgd)
			teamArea.uit = None

		self.teamLine_to_disband.team.removeAllMembers()
		self.teamLine_to_disband.show(self.bgd)
		self.screen.blit(self.bgd, (0, 0))

	def set_bgd_base(self): 
		bgd = self.backgroundImg.copy()
		bgd.blit(loadImg(r'interface\slg_ui\rORG_bg01.png'), (0, 0))
		bgd.blit(loadImg(r'interface\slg_ui\rORG_bg02.png'), (0, 200))
		bgd.blit(loadImg(r'interface\slg_ui\rORG_bg03.png'), (700, 200))
		bgd.blit(loadImg(r'interface\slg_ui\root_ui.png'), (0, 0))
		self.draw_root_pnl(bgd)
		self.bgd_base = bgd

	def set_bgd_normal(self): 
		self._bgd_normal = self.bgd_base.copy()
		self.setUnit()
		self.setTeam()

	def setTeam(self): 
		self.allTeamArea.itemLine_list = self.teamList
		self.allTeamArea.scrollBar.setState()
		self.allTeamArea.show(self.bgd)

	def set_bgd_dismiss(self): 
		self._bgd_dismiss = self.freeze_dlg('解雇しますか？', (550, 255))

	@property
	def bgd_dismiss(self):
		self.set_bgd_dismiss()
		return self._bgd_dismiss

	def set_bgd_disband(self): 
		self._bgd_disband = self.freeze_dlg('師団を解散しますか？', (495, 255))

	@property
	def bgd_disband(self):
		self.set_bgd_disband()
		return self._bgd_disband

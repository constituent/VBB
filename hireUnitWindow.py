#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# 给每个Widget建一个搜索的网格
# 雇佣
# us_comp.png

# 教训1：一定不要省事写if，而要用状态模式
# 教训2：不要在细节处纠结性能问题，至少直到完全写完功能
# 重复blit、不必要的blit全图什么的随它去，否则可能严重增大程序复杂度
# 最后出于性能原因或者只是洁癖再来改都行

from itertools import zip_longest
from enum import Enum, IntEnum
from operator import attrgetter
from vb import *

class TypeButton(SelectableRectButton): 
	TypeButtonIndex = IntEnum('TypeButtonIndex', '魔獣 亜人 兵卒 傭兵 聖職 妖精 造魔 悪魔 竜族 神族 倭国 不死 蟲族 勇者 女神')
	def __init__(self, typename, pos, window, screen, parent): 
		self.typename = typename
		picPath = ('interface\slg_ui', 'rDraft_bt{:0>2}.png'.format(getattr(self.TypeButtonIndex, typename)))
		self.ori_img = loadImg(picPath)
		SelectableRectButton.__init__(self, splitImg(self.ori_img, 3), pos, window, screen, parent=parent)
		self.mouse_on_index = 2
		self.mouse_off_index = 0
		self.index = 0
		self.selected = False
	def setSelect(self, bgd): 
		selected = self.window.selected
		if selected is not None: 
			ub = self.window.selected.ub
		startLine = self.window.allUnitBaseArea.startLine
		self.window.allUnitBaseArea.startLine = 0
		self.window.setUnitBase(self.typename)

		if selected is not None: 
			if not isinstance(selected, AllUnitBaseArea.DummySelected): 
				index = [selected.index[0]+startLine, selected.index[1]]
				self.window.selected = AllUnitBaseArea.DummySelected(self.window, index, self.window.selectedTypeButton, 
					ub, self.screen)
			elif selected.typeButton == self: 
				i, j = selected.index
				if 0 <= i < 4: 
					self.window.allUnitBaseArea.ubAreaLine_list[i].ubAreaList[j].reSelect()

		self.window.selectedTypeButton = self
		self.selected = True
		self.index = 1
		self.show(bgd)
	def leftClick(self): 
		selectedTypeButton = self.window.selectedTypeButton
		if selectedTypeButton != self: 
			selectedTypeButton.selected = False
			selectedTypeButton.index = 0
			selectedTypeButton.show(self.window.bgd)
			selectedTypeButton.show()
			
			self.setSelect(self.window.bgd)
			
			rect = self.window.allUnitBaseArea.rect
			self.screen.blit(self.window.bgd.subsurface(rect), rect)
			self.show()

class SortButton(RectButton): 
	SortType = Enum('SortType', 'index cost divine')
	def create_SortType_generator(SortType): 
		while True: 
			yield SortType.cost
			yield SortType.divine
			yield SortType.cost
			yield SortType.index
	sortType_generator = create_SortType_generator(SortType)
	sortFuncDict = {SortType.cost: attrgetter('cost'), 
		SortType.divine: lambda ub: tuple(DIVINES.index(d) for d in ub.divine), 
		SortType.index: attrgetter('index')
	}
	def __init__(self, window, screen, parent): 
		picPath = ('interface\slg_ui', 'rDraft_bt17.png')
		self.ori_img = loadImg(picPath)
		RectButton.__init__(self, splitImg(self.ori_img, 3), (642, 615), window, screen, parent=parent)
		self.mouse_on_index = 2
		self.mouse_off_index = 0

	def leftClick(self): 
		def searchNowIndex(selectedIndex): 
			for i, ubLine in enumerate(self.window.ubLine_list): 
				for j, ub in enumerate(ubLine): 
					if ub.index == selectedIndex: 
						return ub, (i, j)
		if self.window.selected: 
			selectedIndex = self.window.selected.ub.index

		sortType = next(self.sortType_generator)
		for unitBaseList in self.window.unitBaseDict.values(): 
			unitBaseList.sort(key=self.sortFuncDict[sortType])
		self.window.setUnitBase(self.window.selectedTypeButton.typename)
		allUnitBaseArea = self.window.allUnitBaseArea

		if self.window.selected: 
			if (isinstance(self.window.selected, allUnitBaseArea.DummySelected) and 
				self.window.selectedTypeButton != self.window.selected.typeButton): 
				unitBaseList = self.window.unitBaseDict[self.window.selected.typeButton.typename]
				for i, ub in enumerate(unitBaseList): 
					if ub.index == selectedIndex: 
						break
				else: 
					raise
				self.window.selected.index = divmod(i, 8)
			else: 
				ub, (i, j) = searchNowIndex(selectedIndex)
				i -= allUnitBaseArea.startLine
				if 0 <= i < 4: 
					selected = allUnitBaseArea[i][j]
					self.window.selected = selected
					self.window.bgd.blit(selected.mask_surface, selected.rect)
				else: 
					self.window.selected = allUnitBaseArea.DummySelected(self.window, (i, j), 
						self.window.selectedTypeButton, ub, self.screen)

		rect = allUnitBaseArea.rect
		blit_sameRect(self.screen, self.window.bgd, rect)

class TitleBox(RectWidget): 
	mask_surface = pg.Surface((34, 34), SRCALPHA, 32)
	mask_surface.fill((255, 255, 255, 100))
	rect1_pre = Rect((945, 320), (145, 15))
	rect1_suf = Rect((1135, 320), (145, 15))
	def __init__(self, setPos, window, pos, screen, parent): 
		rect = Rect(pos, (34, 34))
		RectWidget.__init__(self, rect, window, screen, parent)
		self.setPos = setPos
		self.medal = None
		self._selectedTitleLine = None
		self.title = None

		if setPos == 1: 
			self.filterFunc = lambda title: title.set in (0, 1)
			self.rect1 = self.rect1_pre
		else: 
			self.filterFunc = lambda title: title.set in (0, 2)
			self.rect1 = self.rect1_suf

	def mouse_on(self, last_widget): 
		pg.draw.rect(self.screen, (255, 0, 0), self.rect, 1)
	def mouse_off(self, widget): 
		self.screen.blit(self.window.bgd.subsurface(self.rect), self.rect)

	@property
	def selectedTitleLine(self): 
		return self._selectedTitleLine
	@selectedTitleLine.setter
	def selectedTitleLine(self, value): 
		# 三个地方的title，一个技能，一个报酬，一个雇用资源
		if self._selectedTitleLine: 
			self.window.bgd.blit(self.window.bgd_base.subsurface(self.rect1), self.rect1)
			self.screen.blit(self.window.bgd.subsurface(self.rect1), self.rect1)

		last_value = self._selectedTitleLine

		self._selectedTitleLine = value
		if value: 
			pg.freetype.Font("msgothic.ttc", 15).render_to(self.window.bgd, self.rect1, 
				self._selectedTitleLine.title.name, (255, 255, 255))
			self.screen.blit(self.window.bgd.subsurface(self.rect1), self.rect1)
			self.title = value.title
		else: 
			self.title = None

		selectedUnitArea = self.window.selected
		if selectedUnitArea and value != last_value: 
			selectedUnitArea.clearDetail()
			selectedUnitArea.drawDetail()

	def clearSelected(self): 
		self.window.bgd.blit(self.window.bgd_base.subsurface(self.rect), self.rect)
		if self.medal: 
			self.window.bgd.blit(medal_list[self.medal.index], self.rect)
		self.screen.blit(self.window.bgd.subsurface(self.rect), self.rect)

	def leftClick(self): 
		if self.window.selectedTitleBox == self: 
			self.window.selectedTitleBox = None
			self.clearSelected()
			self.window.allTitleArea.clear()
		else: 
			if self.window.selectedTitleBox is not None: 
				self.window.selectedTitleBox.clearSelected()
				self.window.allTitleArea.clear()
			self.window.selectedTitleBox = self
			self.window.bgd.blit(self.mask_surface, self.rect)
			self.screen.blit(self.mask_surface, self.rect)
			self.show()

	def leftDoubleClick(self): 
		self.medal = None
		self.selectedTitleLine = None
		self.window.bgd.blit(self.window.bgd_base.subsurface(self.rect), self.rect)
		self.screen.blit(self.window.bgd.subsurface(self.rect), self.rect)
		self.window.allTitleArea.clear()

	def mouseDrop(self, dragging): 
		if isinstance(dragging, MedalArea) and dragging and dragging.available: 
			self.medal = dragging.medal
			self.window.bgd.blit(medal_list[self.medal.index], self.rect)
			self.screen.blit(self.window.bgd, (0, 0))
			self.selectedTitleLine = None

			self.window.allTitleArea.clear()
			if self.window.selectedTitleBox is not None: 
				if self.window.selectedTitleBox != self: 
					self.window.selectedTitleBox.clearSelected()
			self.window.selectedTitleBox = self
			self.window.bgd.blit(self.mask_surface, self.rect)
			self.screen.blit(self.mask_surface, self.rect)
			self.window.allTitleArea.show(self.medal, self.filterFunc)

	def show(self): 
		if self.medal is None: 
			medal = self.window.tacticaList[0]
		else: 
			medal = self.medal
		self.window.allTitleArea.show(medal, self.filterFunc)
		if self.selectedTitleLine: 
			self.window.bgd.blit(self.selectedTitleLine.mask_surface_, self.selectedTitleLine.rect)
			self.screen.blit(self.selectedTitleLine.mask_surface_, self.selectedTitleLine.rect)

class TitleLine(Line_of_VScrollArea): 
	title_font = pg.freetype.Font("msgothic.ttc", 12)
	mask_surface = pg.Surface((360, 12), SRCALPHA, 32)
	mask_surface.fill((255, 0, 0, 150))
	mask_surface_ = pg.Surface((360, 12), SRCALPHA, 32)
	mask_surface_.fill((0, 255, 255, 100))
	def __init__(self, rect, window, screen, parent): 
		Line_of_VScrollArea.__init__(self, rect, window, screen, parent)
		self.title = None
	def show(self, screen): 
		if self.title is None: 
			pass
		else: 
			self.title_font.render_to(screen, self.pos, self.title.display(), (221, 223, 225))
	def mouse_on(self, last_widget): 
		if self.title: 
			self.screen.blit(self.mask_surface, self.rect)
	def mouse_off(self, widget): 
		self.screen.blit(self.window.bgd.subsurface(self.rect), self.rect)

	def leftClick(self): 
		if self.title: 
			selectedTitleBox = self.window.selectedTitleBox
			if selectedTitleBox.selectedTitleLine == self: 
				selectedTitleBox.selectedTitleLine = None
				self.window.bgd.blit(self.window.bgd_base.subsurface(self.rect), self.rect)
				self.show(self.window.bgd)
				self.screen.blit(self.window.bgd.subsurface(self.rect), self.rect)
				self.mouse_on(None)
			else: 
				if selectedTitleBox.selectedTitleLine is not None: 
					self.window.bgd.blit(self.window.bgd_base.subsurface(selectedTitleBox.selectedTitleLine.rect), 
						selectedTitleBox.selectedTitleLine.rect)
					selectedTitleBox.selectedTitleLine.show(self.window.bgd)
					self.screen.blit(self.window.bgd.subsurface(selectedTitleBox.selectedTitleLine.rect), 
						selectedTitleBox.selectedTitleLine.rect)
				selectedTitleBox.selectedTitleLine = self
				self.window.bgd.blit(self.mask_surface_, self.rect)
				self.screen.blit(self.mask_surface_, self.rect)

class AllTitleArea(Monoheight_VScrollArea): 
	def __init__(self, rect, window, screen, parent): 
		Monoheight_VScrollArea.__init__(self, rect, window, screen, parent)
	def __iter__(self): 
		return self.titleAreaLine_list.__iter__()
	def __len__(self): 
		return 15
	def __getitem__(self, key): 
		return self.titleAreaLine_list[key]
	def show(self, medal, filterFunc=lambda title: True): 
		titleList = [title for title in self.window.tacticaDict[medal.name].titleList if filterFunc(title)]
		for titleLine, title in zip_longest(self.titleAreaLine_list, titleList): 
			titleLine.title = title
			titleLine.show(self.window.bgd)
		self.screen.blit(self.window.bgd.subsurface(self.rect), (self.rect))
	def clear(self): 
		for titleLine in self.titleAreaLine_list: 
			titleLine.title = None
		self.window.bgd.blit(self.window.bgd_base.subsurface(self.rect), (self.rect))
		self.screen.blit(self.window.bgd.subsurface(self.rect), (self.rect))

class MedalArea(RectWidget): 
	mask_surface = pg.Surface((32, 32), SRCALPHA, 32)
	mask_surface.fill((0, 0, 0, 150))
	def __init__(self, window, pos, screen, parent): 
		rect = Rect(pos, (32, 47))
		RectWidget.__init__(self, rect, window, screen, parent)
		self.subRect1 = Rect((pos[0], pos[1]+2), (32, 32))
		self.subRect2 = Rect((pos[0], pos[1]+34), (32, 13))
		self.medal = None
		self._available = True

	def __bool__(self): 
		return self.medal is not None

	@property
	def available(self): 
		return self._available

	def setAvailable(self, rare): 
		if self.medal: 
			if self.medal.rare <= rare: 
				if not self._available: 
					self._available = True
					self.show(self.window.bgd)
			else: 
				if self._available: 
					self._available = False
					self.window.bgd.blit(self.mask_surface, self.subRect1)

	def show(self, screen=None): 
		if screen is None: 
			screen = self.screen
		if self.medal is None: 
			screen.fill((0, 0, 0), self.rect)
		else: 
			screen.blit(medal_list[self.medal.index], (self.pos[0]-1, self.pos[1]))

	def mouse_on(self, last_widget): 
		if self.medal is None: 
			return
		pg.draw.rect(self.screen, (255, 0, 0), self.subRect1, 1)
		if (not isinstance(last_widget, self.__class__) or last_widget.medal is None) and self.window.selectedTitleBox is not None: 
			self.window.allTitleArea.clear()
		filterFunc = (lambda selectedTitleBox: (lambda title: True) if selectedTitleBox is None 
			else selectedTitleBox.filterFunc)(self.window.selectedTitleBox)
		self.window.allTitleArea.show(self.medal, filterFunc)

	def mouse_off(self, widget): 
		self.screen.blit(self.window.bgd.subsurface(self.subRect1), self.subRect1)
		self.window.allTitleArea.clear()
		if not isinstance(widget, self.__class__) or widget.medal is None: 
			selectedTitleBox = self.window.selectedTitleBox
			if selectedTitleBox is not None: 
				selectedTitleBox.show()

	def mouseDrag(self): 
		# 有点卡，可以考虑用sprite，或者只重画部分区域
		if self.medal and self.window.selected and self.available: 
			medal_img = medal_list[self.medal.index]
			self.screen.blit(self.window.bgd, (0, 0))
			widget = self.window.widgetList.findArea(pg.mouse.get_pos())
			if isinstance(widget, TitleBox): 
				widget.mouse_on(None)
			self.screen.blit(medal_img, pg.mouse.get_pos())
	def showRequire(self, type_): 
		color = {0: (0, 0, 0), 
			1: (0, 136, 0), 
		}[type_]
		self.window.bgd.fill(color, self.subRect2)

class MedalLine(Line_of_VScrollArea): 
	def __init__(self, rect, window, screen, parent): 
		Line_of_VScrollArea.__init__(self, rect, window, screen, parent)
	def __iter__(self): 
		return self.medalAreaList.__iter__()
	def __getitem__(self, key): 
		return self.medalAreaList[key]

class AllMedalArea(Monoheight_VScrollArea): 
	def __init__(self, rect, window, screen, parent): 
		Monoheight_VScrollArea.__init__(self, rect, window, screen, parent)
	def __iter__(self): 
		return self.medalAreaLine_list.__iter__()
	def __len__(self): 
		return 5
	def __getitem__(self, key): 
		return self.medalAreaLine_list[key]

class UnitBaseArea(RectWidget, UnitDetailMixin): 
	mask_surface = pg.Surface((64, 82), SRCALPHA, 32)
	mask_surface.fill((255, 255, 255, 100))
	faceImgList = splitImg(loadImg((r'interface\slg_ui', 'icon06.png')), 5)
	faceRect = Rect((829, 238), (34, 20))
	def __init__(self, window, index, screen, parent): 
		self.index = index
		i, j = index
		pos = (60+65*j, 304+85*i)
		rect = Rect(pos, (64, 82))
		RectWidget.__init__(self, rect, window, screen, parent)
		self.ub = None
	def __bool__(self): 
		return self.ub is not None

	def show(self, screen=None): 
		if screen is None: 
			screen = self.screen
		if self.ub is None: 
			screen.fill((0, 0, 0), self.rect)
		else: 
			img = loadImg(self.ub.get_fc()).subsurface(Rect((8, 10), (124, 124)))
			img = pg.transform.smoothscale(img, (62, 62))# 80
			img.blit(combineImg(moon_dict[d] for d in self.ub.divine), (1, 1))

			screen.fill((0, 136, 0), self.rect)
			screen.blit(img, (self.pos[0]+1, self.pos[1]+1))
			screen.blit(job_dict[self.ub.job], (self.pos[0]+4, self.pos[1]+64))
			screen.blit(resource_list[self.ub.pay-1], (self.pos[0]+21, self.pos[1]+66))
			self.cost_font.render_to(screen, (self.pos[0]+42, self.pos[1]+66), '{:2}'.format(self.ub.cost), (254, 254, 254))

	def getUnit(self): 
		employType = self.window.employType

		if self.window.selected == self: 
			title1 = self.window.pre_titleBox.title
			title2 = self.window.suf_titleBox.title
			titles = (title1, title2)
		else: 
			titles = (None, None)
		ub = self.ub
		moonEffect = ub.getMoonEffect(employType, titles, self.window.moon, self.window.daylight)
		unit = Unit(ub, employType, moonEffect=moonEffect, titles=titles, level=200)
		unit.area_available = True
		return unit

	def drawDetail(self): 
		bgd = self.window.bgd

		ub = self.ub
		for i in ub.recipeIndexList: 
			self.window.allMedalArea[(i-1)//8][(i-1)%8].showRequire(1)

		unit = self.getUnit()
		moonEffect = unit.moonEffect
		self._drawDetail(unit)

		blit_sameRect(bgd, self.window.bgd_base, self.faceRect)
		bgd.blit(self.faceImgList[moonEffect], (829, 238))

		# blit_sameRect(self.screen, bgd, self.unitDetailRect)
		# blit_sameRect(self.screen, bgd, self.faceRect)
		self.screen.blit(bgd, (0, 0))

	def clearDetail(self): 
		if self.ub: 
			blit_sameRect(self.window.bgd, self.window.bgd_base, self.unitDetailRect)
			blit_sameRect(self.window.bgd, self.window.bgd_base, self.faceRect)
			for i in self.ub.recipeIndexList: 
				self.window.allMedalArea[(i-1)//8][(i-1)%8].showRequire(0)
			self.screen.blit(self.window.bgd, (0, 0))

	def mouse_on(self, last_widget): 
		if self.ub is None: 
			return
		pg.draw.rect(self.screen, (255, 0, 0), self.rect, 1)
		if self.window.selected is not None and (not isinstance(last_widget, self.__class__) or last_widget.ub is None): 
			self.window.selected.clearDetail()
		self.drawDetail()

	def mouse_off(self, widget): 
		self.clearDetail()
		if self.window.selected is not None and (not isinstance(widget, self.__class__) or widget.ub is None): 
			self.window.selected.drawDetail()
		self.screen.blit(self.window.bgd.subsurface(self.rect), self.rect)

	def leftClick(self): 
		if self != self.window.selected and self.ub: 
			for titleBox in (self.window.pre_titleBox, self.window.suf_titleBox): 
				titleBox.medal = None
				titleBox.selectedTitleLine = None
				self.window.bgd.blit(self.window.bgd_base.subsurface(titleBox.rect), titleBox.rect)
			self.window.allTitleArea.clear()
			self.window.selectedTitleBox = None
			self.reSelect()
			for medalAreaLine in self.window.allMedalArea: 
				for medalArea in medalAreaLine: 
					medalArea.setAvailable(UnitBase.MAX_RARE[self.ub.growth])
			if self.window.state != self.window.UnitSelectedState: 
				self.window.decideButton.show(self.window.bgd)
				self.window.state = self.window.UnitSelectedState
			else: 
				self.screen.blit(self.window.bgd, (0,0))

	def reSelect(self): 
		lastSelected = self.window.selected
		self.window.selected = self
		if lastSelected is not None: 
			lastSelected.show(self.window.bgd)
		self.window.bgd.blit(self.mask_surface, self.rect)

class UnitBaseLine(Line_of_VScrollArea): 
	def __init__(self, rect, window, screen, parent): 
		Line_of_VScrollArea.__init__(self, rect, window, screen, parent)
	def __iter__(self): 
		return self.ubAreaList.__iter__()
	def __getitem__(self, key): 
		return self.ubAreaList[key]

class AllUnitBaseArea(Monoheight_VScrollArea): 
	class DummySelected(UnitBaseArea): 
		def __init__(self, window, index, typeButton, ub, screen): 
			self.window = window
			self.index = index
			self.typeButton = typeButton
			self.ub = ub
			self.screen = screen
			self.rect = Rect((0, 0), (0, 0))
		def show(self, screen=None): 
			pass

	class DefaultState(Monoheight_VScrollArea.DefaultState): 
		default = True
		def wheelUp(self, lineCount=1): 
			Monoheight_VScrollArea.DefaultState.wheelUp(self, lineCount)
			widget = self.window.widgetList.findArea(pg.mouse.get_pos())
			widget.mouse_on(None)
		def wheelDown(self, lineCount=1): 
			Monoheight_VScrollArea.DefaultState.wheelDown(self, lineCount)
			widget = self.window.widgetList.findArea(pg.mouse.get_pos())
			widget.mouse_on(None)
	class UnitSelectedState(Monoheight_VScrollArea.DefaultState): 
		def wheelUp(self, lineCount=1): 
			startLine_before = self.startLine
			ub = self.window.selected.ub
			Monoheight_VScrollArea.DefaultState.wheelUp(self, lineCount)
			n = startLine_before-self.startLine
			if n and (not isinstance(self.window.selected, self.DummySelected) or 
				self.window.selected.typeButton == self.window.selectedTypeButton): 
				i, j = self.window.selected.index
				if 0<=i+n<4: 
					self.ubAreaLine_list[i+n].ubAreaList[j].reSelect()
				else: 
					self.window.selected = self.DummySelected(self.window, (i+n, j), self.window.selectedTypeButton, ub, self.screen)
				self.window.screen.blit(self.window.bgd.subsurface(self.rect), self.rect)

			widget = self.window.widgetList.findArea(pg.mouse.get_pos())
			widget.mouse_on(None)
			
		def wheelDown(self, lineCount=1): 
			startLine_before = self.startLine
			ub = self.window.selected.ub
			Monoheight_VScrollArea.DefaultState.wheelDown(self, lineCount)
			n = startLine_before-self.startLine
			if n and (not isinstance(self.window.selected, self.DummySelected) or 
				self.window.selected.typeButton == self.window.selectedTypeButton): 
				i, j = self.window.selected.index
				if 0<=i+n<4: 
					self.ubAreaLine_list[i+n].ubAreaList[j].reSelect()
				else: 
					self.window.selected = self.DummySelected(self.window, (i+n, j), self.window.selectedTypeButton, ub, self.screen)
				self.window.screen.blit(self.window.bgd.subsurface(self.rect), self.rect)

			widget = self.window.widgetList.findArea(pg.mouse.get_pos())
			widget.mouse_on(None)

	def __init__(self, rect, window, screen, parent): 
		Monoheight_VScrollArea.__init__(self, rect, window, screen, parent)
		self.scrollBar = VScrollBar((255, 255, 255), Rect((580, 304), (2, 336)), window, screen, self)
	def __iter__(self): 
		return self.ubAreaLine_list.__iter__()
	def __len__(self): 
		return 4
	def __getitem__(self, key): 
		return self.ubAreaLine_list[key]
	def show(self, screen=None): 
		if screen is None: 
			screen = self.screen
		startLine = self.startLine
		for ubLine, ubAreaLine in zip_longest(self.window.ubLine_list[startLine: startLine+4], self, fillvalue=[None]*8): 
			for ub, ubArea in zip_longest(ubLine, ubAreaLine): 
				ubArea.ub = ub
				ubArea.show(screen)

		self.scrollBar.show(screen)

class FullWidget(Widget): 
	def __init__(self, window): 
		Widget.__init__(self, window)
	class DefaultState(Widget.DefaultState): 
		default = True
		def mouseDrop(self, dragging): 
			# 可以优化
			self.window.screen.blit(self.window.bgd, (0, 0))
	class HiringState(Widget.DefaultState): 
		def leftClick(self): 
			self.window.state = self.window.UnitSelectedState

class BrainWashButton(RectButton): 
	def __init__(self, window, screen, parent): 
		imgList = splitImg(loadImg(('interface\slg_ui', 'rDraft_bt32.png')), 3, 2)
		RectButton.__init__(self, imgList, (1165, 225), window, screen, available=True, parent=parent)
		self.selected = False
		self.index = 0
	def mouse_on(self, last_widget): 
		if self.selected: 
			self.index = 5
		else: 
			self.index = 2
		self.show()
	def mouse_off(self, widget): 
		if self.selected: 
			self.index = 3
		else: 
			self.index = 0
		self.show()
	def leftClick(self): 
		self.selected ^= True
		self.mouse_on(None)
		self.window.employType = 3-self.window.employType
		if self.window.selected: 
			self.window.selected.clearDetail()
			self.window.selected.drawDetail()

class DecideButton(RectButton): 
	def __init__(self, window, screen, parent): 
		imgList = splitImg(loadImg(('interface\slg_ui', 'rDraft_bt33.png')), 3)
		RectButton.__init__(self, imgList, (1220, 225), window, screen, available=True, parent=parent)
		self.index = 0
		self.mouse_on_index = 1
		self.mouse_off_index = 0
	def leftClick(self): 
		self.window.hireUnit()

class HireUnitWindow(VB_Window): 
	typeButtonOrder = '亜人 魔獣 妖精 倭国 悪魔 不死 造魔 竜族 蟲族 兵卒 傭兵 聖職 神族 勇者 女神'.split()
	class UnitSelectedState(VB_Window.NormalState): 
		def __setup__(self): 
			VB_Window.NormalState.__setup__(self)
			self.allUnitBaseArea.state = self.allUnitBaseArea.UnitSelectedState
		# def __clear__(self): 
		# 	VB_Window.NormalState.__clear__(self)
		# 	self.allUnitBaseArea.state = self.allUnitBaseArea.DefaultState
	class HiringState(VB_Window.NormalState): # FreezeState似乎没啥用
		def __setup__(self): 
			VB_Window.NormalState.__setup__(self)
			self.fullWidget.state = self.fullWidget.HiringState
		def __clear__(self): 
			VB_Window.NormalState.__clear__(self)
			self.fullWidget.state = self.fullWidget.DefaultState

	def __init__(self, gameData, screen, unitBaseDict, tacticaList, tacticaDict): 
		self.fullWidget = FullWidget(self)
		VB_Window.__init__(self, screen, gameData)
		self.hiredUnitList = gameData.hiredUnitList
		self.selected = None
		self.selectedTitleBox = None
		self.employType = 1
		self.selectedTypeButton = None

		self.set_root_pnl(screen)
		self.root_bt_list = [self.bt_nextTurn, self.bt_campaign, self.bt_organizeTeam, self.bt_item]
		self.bt_hire.index = 1

		self.typeButtonList = [TypeButton(typename, (5, 340+20*i), self, screen, self.fullWidget) 
			for (i, typename) in enumerate(self.typeButtonOrder)]
		self.sortButton = SortButton(self, screen, self.fullWidget)

		self.unitBaseDict = unitBaseDict
		self.allUnitBaseArea = AllUnitBaseArea(Rect((60, 304), (522, 337)), self, screen, self.fullWidget)
		self.allUnitBaseArea.ubAreaLine_list = [UnitBaseLine(Rect((60, 304+85*i), (65*8-1, 82)), self, screen, 
			self.allUnitBaseArea) for i in range(4)]
		for i, ubAreaLine in enumerate(self.allUnitBaseArea.ubAreaLine_list): 
			ubAreaList = []
			for j in range(8): 
				ubAreaList.append(UnitBaseArea(self, (i, j), screen, ubAreaLine))
			ubAreaLine.ubAreaList = ubAreaList

		self.tacticaList = tacticaList[: -2]; self.tacticaDict = tacticaDict
		self.medalLine_list = []
		index = 0
		while index < len(self.tacticaList[1: ]): 
			self.medalLine_list.append(self.tacticaList[1: ][index: index+8])
			index += 8
		self.allMedalArea = AllMedalArea(Rect((585, 304), (279, 249)), self, screen, self.fullWidget)
		self.allMedalArea.medalAreaLine_list = [MedalLine(Rect((585, 304+50*i), (35*8-1, 49)), self, screen, 
			self.allMedalArea) for i in range(5)]
		self.allMedalArea.itemLine_list = self.allMedalArea.medalAreaLine_list
		for i, medalAreaLine in enumerate(self.allMedalArea.medalAreaLine_list): 
			medalAreaList = []
			for j in range(8): 
				medalAreaList.append(MedalArea(self, (586+35*j, 305+50*i), screen, medalAreaLine))
			medalAreaLine.medalAreaList = medalAreaList
		self.nullMedal = MedalArea(self, (831, 558), screen, self.fullWidget)


		self.allTitleArea = AllTitleArea(Rect((910, 405), (365, 220)), self, screen, self.fullWidget)
		self.allTitleArea.titleAreaLine_list = [TitleLine(Rect((910, 405+15*i), (360, 12)), self, screen, 
			self.allTitleArea) for i in range(15)]
		self.allTitleArea.itemLine_list = self.allTitleArea.titleAreaLine_list

		self.pre_titleBox = TitleBox(1, self, (905, 304), screen, self.fullWidget)
		self.suf_titleBox = TitleBox(2, self, (1095, 304), screen, self.fullWidget)

		self.brainWashButton = BrainWashButton(self, screen, self.fullWidget)
		self.decideButton = DecideButton(self, screen, self.fullWidget)

		self.widgetList_normal = WidgetList(self, [self.allUnitBaseArea, self.allMedalArea, self.nullMedal, 
			self.sortButton, self.brainWashButton]+self.typeButtonList+self.root_bt_list)
		self.widgetList_selected = WidgetList(self, [self.allUnitBaseArea, self.allMedalArea, self.nullMedal, 
			self.pre_titleBox, self.suf_titleBox, self.allTitleArea, self.sortButton, self.brainWashButton, 
			self.decideButton]+self.typeButtonList+self.root_bt_list)
		self.widgetList_hiring = WidgetList(self, [])

		self.backgroundImg = loadImg(r'event\cg_ye_24c.bmp')
		self.set_bgd_base()
		self._bgd_normal = None
		self._bgd_selected = None
		self.bgd_dict.update({self.NormalState: 'bgd_normal', 
			self.UnitSelectedState: 'bgd_selected', 
			self.HiringState: 'bgd_hiring'})
		self.widgetList_dict.update({self.NormalState: 'widgetList_normal', 
			self.UnitSelectedState: 'widgetList_selected', 
			self.HiringState: 'widgetList_hiring'})
		self.bFullScreen = False

	def hireUnit(self): 
		self.hiredUnitList.append(self.selected.getUnit())
		self.state = self.HiringState

	def setUnitBase(self, typename): 
		unitBaseList = self.unitBaseDict[typename]
		self.ubLine_list = []
		self.allUnitBaseArea.itemLine_list = self.ubLine_list
		index = 0
		while index < len(unitBaseList): 
			self.ubLine_list.append(unitBaseList[index: index+8])
			index += 8
		self.allUnitBaseArea.scrollBar.setState()
		self.allUnitBaseArea.show(self.bgd)

	def set_bgd_base(self): 
		bgd = self.backgroundImg.copy()
		bgd.blit(loadImg(r'interface\slg_ui\rDraft_bg00.png'), (0, 0))
		bgd.blit(loadImg(r'interface\slg_ui\rDraft_bg01.png'), (0, 294))
		blit_topright(bgd, loadImg(r'interface\slg_ui\rDraft_bg02.png'), (1280, 294))
		bgd.blit(loadImg(r'interface\slg_ui\root_ui.png'), (0, 0))
		self.draw_root_pnl(bgd)
		self.brainWashButton.show(bgd)
		
		self.bgd_base = bgd

	def set_bgd_normal(self): 
		self._bgd_normal = self.bgd_base.copy()
		self.update_medalArea()
		pg.freetype.Font("msgothic.ttc", 20).render_to(self._bgd_normal, (55, 240), 'ユニットが選択されていません', (255, 255, 255))
		self.typeButtonList[0].setSelect(self._bgd_normal)
		self.typeButtonList[-1].show(self._bgd_normal)
		self.typeButtonList[-2].show(self._bgd_normal)

	def set_bgd_selected(self): 
		self._bgd_selected = self.bgd_normal.copy()
		rect = Rect((1, 203), (408, 87))
		self._bgd_selected.blit(self.bgd_base.subsurface(rect), (rect))

	@property
	def bgd_selected(self): 
		if self._bgd_selected is None: 
			self.set_bgd_selected()
		return self._bgd_selected

	def set_bgd_hiring(self): 
		self._bgd_hiring = self.bgd_selected.copy()
		img = loadImg(self.selected.ub.get_bf())
		rect = img.get_rect()
		rect.center = (640, 360)
		self._bgd_hiring.blit(img, rect)

	@property
	def bgd_hiring(self): 
		self.set_bgd_hiring()
		return self._bgd_hiring

	def update_medalArea(self): 
		startLine = self.allMedalArea.startLine
		for medalLine, medalAreaLine in zip(self.medalLine_list[startLine: startLine+5], self.allMedalArea): 
			for medal, medalArea in zip_longest(medalLine, medalAreaLine): 
				medalArea.medal = medal
				medalArea.show(self.bgd)
		self.nullMedal.medal = self.tacticaList[0]
		self.nullMedal.show(self.bgd)

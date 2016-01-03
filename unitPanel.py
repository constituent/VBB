#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from itertools import zip_longest

from vb import *

__all__ = ['UnitArea_', 'UnitLine', 'AllUnitArea_', 'UnitPanelMixin']

class UnitArea_(RectWidget, UnitDetailMixin): 
	size = (48, 63)
	mask_surface = pg.Surface(size, SRCALPHA, 32)
	mask_surface.fill((0, 0, 0, 150))
	# imgList = splitImg(loadImg(r'interface\icon\uf_.bmp'), 20, 31)[: -6]
	# 总大小960*1953，每个48*63
	# imgList.reverse()
	# # 对应太麻烦了，拉倒
	def __init__(self, window, index, screen, parent): 
		self.index = index
		i, j = index
		pos = (730+50*j, 255+65*i)
		# rect = Rect(pos, (48, 40))
		rect = Rect(pos, self.size)
		RectWidget.__init__(self, rect, window, screen, parent)
		self.unit = None

	def __bool__(self): 
		return self.unit is not None

	def getImg(self): 
		ub = self.unit.unitBase
		return loadImg(ub.get_uw()).subsurface(Rect((135, 2), (48, 40)))# 将就了，不管了

	def mouse_on(self, last_widget): 
		if self.unit is None: 
			return
		pg.draw.rect(self.screen, (255, 0, 0), self.rect, 1)
		self.drawDetail()

	def mouse_off(self, widget): 
		self.clearDetail()
		self.screen.blit(self.window.bgd.subsurface(self.rect), self.rect)

	def drawDetail(self): 
		self._drawDetail(self.unit)
		blit_sameRect(self.screen, self.window.bgd, self.unitDetailRect)
		# self.screen.blit(self.window.bgd, (0, 0))

	def clearDetail(self): 
		if self.unit: 
			blit_sameRect(self.window.bgd, self.window.bgd_base, self.unitDetailRect)
			blit_sameRect(self.screen, self.window.bgd, self.unitDetailRect)
			# self.screen.blit(self.window.bgd, (0, 0))

class UnitLine(Line_of_VScrollArea): 
	def __init__(self, rect, window, screen, parent): 
		Line_of_VScrollArea.__init__(self, rect, window, screen, parent)
	def __iter__(self): 
		return self.unitAreaList.__iter__()
	def __getitem__(self, key): 
		return self.unitAreaList[key]

class AllUnitArea_(Monoheight_VScrollArea): 
	def __init__(self, rect, window, screen, parent): 
		Monoheight_VScrollArea.__init__(self, rect, window, screen, parent)
		self.scrollBar = VScrollBar((255, 255, 255), Rect((1130, 255), (3, 388)), window, screen, self)
	def __iter__(self): 
		return self.unitAreaLine_list.__iter__()
	def __len__(self): 
		return 6
	def __getitem__(self, key): 
		return self.unitAreaLine_list[key]
	def searchUnit(self, unit): 
		for unitLine in self: 
			for unitArea in unitLine: 
				if unitArea.unit == unit: 
					return unitArea
		return None
	def show(self, screen=None): 
		if screen is None: 
			screen = self.screen
		startLine = self.startLine
		for unitLine, unitAreaLine in zip_longest(self.itemLine_list[startLine: startLine+6], self, fillvalue=[None]*8): 
			for unit, unitArea in zip_longest(unitLine, unitAreaLine): 
				unitArea.unit = unit
				unitArea.show(screen)

		self.scrollBar.show(screen)

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

class UnitPanelMixin(): 
	def setAllUnitArea(self, UnitArea, AllUnitArea): 
		self.allUnitArea = AllUnitArea(Rect((730, 255), (403, 388)), self, self.screen, self.fullWidget)
		self.allUnitArea.unitAreaLine_list = [UnitLine(Rect((730, 255+65*i), (50*8-1, 63)), self, self.screen, 
			self.allUnitArea) for i in range(6)]
		for i, unitAreaLine in enumerate(self.allUnitArea.unitAreaLine_list): 
			unitAreaList = []
			for j in range(8): 
				unitAreaList.append(UnitArea(self, (i, j), self.screen, unitAreaLine))
			unitAreaLine.unitAreaList = unitAreaList
	def setUnit(self): 
		hiredUnitList = self.hiredUnitList
		self.allUnitArea.itemLine_list = []
		index = 0
		while index < len(hiredUnitList): 
			self.allUnitArea.itemLine_list.append(hiredUnitList[index: index+8])
			index += 8
		self.allUnitArea.scrollBar.setState()
		self.allUnitArea.show(self.bgd)
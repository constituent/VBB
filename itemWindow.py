#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from enum import IntEnum
from itertools import zip_longest

from vb import *
from unitPanel import *


class TypeButton(SelectableRectButton): 
	TypeButtonIndex = IntEnum('TypeButtonIndex', '片手 両手 射撃 杖 鞭 爪 盾 鎧 獣装 法衣 道具 素材')
	def __init__(self, typename, pos, window, screen, parent): 
		self.typename = typename
		picPath = ('interface\slg_ui', 'rEquip_bt{:0>2}.png'.format(getattr(self.TypeButtonIndex, typename)+9))
		self.ori_img = loadImg(picPath)
		SelectableRectButton.__init__(self, splitImg(self.ori_img, 3), pos, window, screen, parent=parent)
		self.mouse_on_index = 2
		self.mouse_off_index = 0
		self.index = 0
		self.selected = False
	def setSelect(self, bgd): 
		self.window.allItemArea.startLine = 0
		self.window.allItemArea.set_itemLine_list(self.window.itemDict[self.typename])
		self.window.allItemArea.scrollBar.setState()
		self.window.allItemArea.show(bgd)

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
			
			rect = self.window.allItemArea.rect
			self.screen.blit(self.window.bgd.subsurface(rect), rect)
			self.show()

class ItemDetailMixin(): 
	itemDetailRect = Rect((5, 280), (275, 360))
	name_font = pg.freetype.Font("msgothic.ttc", 24)
	other_font = pg.freetype.Font("msgothic.ttc", 16)
	attrColors = [(255, 0, 0), (255, 186, 0), (0, 255, 192), (0, 174, 255)]
	def drawDetail(self): 
		bgd = self.window.bgd
		item = self.item

		self.name_font.render_to(bgd, (10, 300), item.name, (255, 255, 255))
		self.other_font.render_to(bgd, (10, 345), '{}  ランク：{}'.format(item.type, item.rare), (255, 255, 255))
		bgd.blit(loadImg(item.getImg()), (10, 370))

		if item.type == '素材': 
			pass
		elif item.type == '消耗': 
			pass
		else: 
			tempList = []
			possession = self.window.gameData.item_possession[item]; limit = item.limit
			color = (255, 0, 0) if possession == limit else (255, 255, 255)
			tempList.append(self.other_font.render('所持:{}/{}'.format(possession, limit), color)[0])
			tempList.append(self.other_font.render('装備:{}'.format(self.window.gameData.item_equipped[item]), (255, 255, 255))[0])

			statusList = [self.other_font.render('{}:{}'.format(attr, item.add[index]), self.attrColors[index])[0] 
				for index, attr in enumerate(('攻撃', '防御', '速度', '知力'))]

			skillList = [self.other_font.render(str(skill), (255, 255, 255))[0] for skill in item.skills]

			bgd.blit(combineImg([combineImg(surfaceList, 1, interval=3) for surfaceList in (tempList, statusList, skillList)], 
				1, interval=10), (170, 345))

		blit_sameRect(self.screen, bgd, self.itemDetailRect)

	def clearDetail(self): 
		blit_sameRect(self.window.bgd, self.window.bgd_base, self.itemDetailRect)
		blit_sameRect(self.screen, self.window.bgd_base, self.itemDetailRect)

class EquipBox(RectWidget, ItemDetailMixin): 
	def __init__(self, index, window, pos, screen, parent): 
		self.index = index
		rect = Rect(pos, (48, 48))
		RectWidget.__init__(self, rect, window, screen, parent)
		self.equip = None
		self.equipType = None

	@property
	def item(self): 
		return self.equip

	def mouse_on(self, last_widget): 
		pg.draw.rect(self.screen, (255, 0, 0), self.rect, 1)
		if self.equip: 
			self.drawDetail()

	def mouse_off(self, widget): 
		self.clearDetail()
		self.screen.blit(self.window.bgd.subsurface(self.rect), self.rect)

	def show(self, screen): 
		if screen is None: 
			screen = self.screen
		if self.equip is None: 
			blit_sameRect(screen, self.window.bgd_base, self.rect)
		else: 
			screen.blit(pg.transform.smoothscale(loadImg(self.equip.getImg()), (48, 48)), self.pos)

	def leftDoubleClick(self): 
		if self.equip is not None: 
			bgd = self.window.bgd
			self.clearDetail()
			self.window.gameData.item_equipped[self.equip] -= 1
			itemArea = self.window.allItemArea.searchItem(self.equip)
			if itemArea: 
				itemArea.show(bgd)
			self.equip = None
			self.show(bgd)

			selectedUnit = self.window.selectedUnit
			selectedUnit.unit.changeEquip(self.index, None)
			selectedUnit.show(bgd)
			self.window.bgd.blit(selectedUnit.mask_surface, selectedUnit.rect)
			selectedUnit.clearDetail()
			selectedUnit.drawDetail()

			self.screen.blit(bgd, (0, 0))

	def mouseDrop(self, dragging): 
		bgd = self.window.bgd
		if (isinstance(dragging, ItemArea) and dragging and dragging.item.type == self.equipType and 
			dragging.available): 
			
			self.window.gameData.item_equipped[dragging.item] += 1
			dragging.show(bgd)
			if self.equip is not None: 
				self.window.gameData.item_equipped[self.equip] -= 1
				itemArea = self.window.allItemArea.searchItem(self.equip)
				if itemArea: 
					itemArea.show(bgd)

			blit_sameRect(bgd, self.window.bgd_base, self.rect)
			self.equip = dragging.item
			self.show(bgd)
			# 体现已装备数量的变化
			self.clearDetail()
			self.drawDetail()

			selectedUnit = self.window.selectedUnit
			selectedUnit.unit.changeEquip(self.index, dragging.item)
			selectedUnit.show(bgd)
			self.window.bgd.blit(selectedUnit.mask_surface, selectedUnit.rect)
			selectedUnit.clearDetail()
			selectedUnit.drawDetail()
			
		self.screen.blit(bgd, (0, 0))

class UnitArea(UnitArea_): 
	mask_surface = pg.Surface((48, 63), SRCALPHA, 32)
	mask_surface.fill((255, 255, 255, 100))
	def __init__(self, window, index, screen, parent): 
		UnitArea_.__init__(self, window, index, screen, parent)
		self.equip1_rect = Rect((self.pos[0]+4, self.pos[1]+44), (18, 18))
		self.equip2_rect = Rect((self.pos[0]+26, self.pos[1]+44), (18, 18))
	@property
	def available(self): 
		return True

	def show(self, screen=None): 
		if screen is None: 
			screen = self.screen
		
		screen.fill((0, 0, 0), self.rect)
		if self.unit is not None: 
			screen.blit(self.getImg(), self.pos)
			equip = self.unit.unitBase.equip
			# VBG的神兽啥的没装备
			if equip[0]: 
				screen.blit(loadImg((r'interface\btl_ui', 'item_icon{}.png'.format(equip[0]))), (self.pos[0]+5, self.pos[1]+45))
				screen.blit(loadImg((r'interface\btl_ui', 'item_icon{}.png'.format(equip[1]))), (self.pos[0]+27, self.pos[1]+45))

				if self.unit.items[0]: 
					pg.draw.rect(screen, (255, 0, 0), self.equip1_rect, 2)
				if self.unit.items[1]: 
					pg.draw.rect(screen, (255, 0, 0), self.equip2_rect, 2)

			if not self.available: 
				screen.blit(self.mask_surface, self.rect)

	def mouse_on(self, last_widget): 
		if self.unit is None: 
			return
		pg.draw.rect(self.screen, (255, 0, 0), self.rect, 1)
		if self.window.selectedUnit is not None and (not isinstance(last_widget, self.__class__) or last_widget.unit is None): 
			self.window.selectedUnit.clearDetail()
		self.drawDetail()

	def mouse_off(self, widget): 
		self.clearDetail()
		if self.window.selectedUnit is not None and (not isinstance(widget, self.__class__) or widget.unit is None): 
			self.window.selectedUnit.drawDetail()
		self.screen.blit(self.window.bgd.subsurface(self.rect), self.rect)

	def leftClick(self): 
		if self != self.window.selectedUnit and self.unit: 
			for equipBox, item in zip(self.window.equipBoxList, self.unit.items): 
				blit_sameRect(self.window.bgd, self.window.bgd_base, equipBox.rect)
				equipBox.equip = item
				equipBox.show(self.window.bgd)

			blit_sameRect(self.window.bgd, self.window.bgd_base, Rect((290, 345), (8, 298)))
			for equip_, equipBox in zip(self.unit.unitBase.equip, self.window.equipBoxList): 
				if equip_ != '': 
					y = 345+25*(getattr(TypeButton.TypeButtonIndex, equip_)-1)
					self.window.bgd.blit(loadImg(r'interface\slg_ui\targetline12s.png'), (290, y+6))
				equipBox.equipType = equip_

			self.reSelect()
			if self.window.state != self.window.UnitSelectedState: 
				self.window.state = self.window.UnitSelectedState
			else: 
				self.screen.blit(self.window.bgd, (0,0))

	def reSelect(self): 
		lastSelectedUnit = self.window.selectedUnit
		self.window.selectedUnit = self
		if lastSelectedUnit is not None: 
			lastSelectedUnit.show(self.window.bgd)
		self.window.bgd.blit(self.mask_surface, self.rect)

class DummySelected(UnitArea): 
	def __init__(self, window, index, unit, screen): 
		self.window = window
		self.index = index
		self.unit = unit
		self.screen = screen
		self.rect = Rect((0, 0), (0, 0))
	def show(self, screen=None): 
		pass

class AllUnitArea(AllUnitArea_): 
	class UnitSelectedState(Monoheight_VScrollArea.DefaultState): 
		def wheelUp(self, lineCount=1): 
			startLine_before = self.startLine
			unit = self.window.selectedUnit.unit
			Monoheight_VScrollArea.DefaultState.wheelUp(self, lineCount)
			n = startLine_before-self.startLine
			if n: 
				i, j = self.window.selectedUnit.index
				if 0<=i+n<6: 
					self.unitAreaLine_list[i+n].unitAreaList[j].reSelect()
				else: 
					self.window.selectedUnit = DummySelected(self.window, (i+n, j), unit, self.screen)
				self.screen.blit(self.window.bgd.subsurface(self.rect), self.rect)

			widget = self.window.widgetList.findArea(pg.mouse.get_pos())
			widget.mouse_on(None)
			
		def wheelDown(self, lineCount=1): 
			startLine_before = self.startLine
			unit = self.window.selectedUnit.unit
			Monoheight_VScrollArea.DefaultState.wheelDown(self, lineCount)
			n = startLine_before-self.startLine
			if n: 
				i, j = self.window.selectedUnit.index
				if 0<=i+n<6: 
					self.unitAreaLine_list[i+n].unitAreaList[j].reSelect()
				else: 
					self.window.selectedUnit = DummySelected(self.window, (i+n, j), unit, self.screen)
				self.screen.blit(self.window.bgd.subsurface(self.rect), self.rect)

			widget = self.window.widgetList.findArea(pg.mouse.get_pos())
			widget.mouse_on(None)

class ItemArea(RectWidget, ItemDetailMixin): 
	def __init__(self, window, index, screen, parent): 
		self.index = index
		i, j = index
		pos = (375+50*j, 345+50*i)
		rect = Rect(pos, (48, 48))
		RectWidget.__init__(self, rect, window, screen, parent)
		self.item = None
	def __bool__(self): 
		return self.item is not None
	@property
	def available(self): 
		return self.window.gameData.item_left(self.item) > 0

	def show(self, screen): 
		if screen is None: 
			screen = self.screen
		blit_sameRect(screen, self.window.bgd_base, self.rect)
		if self.item is not None: 
			try: 
				screen.blit(pg.transform.smoothscale(loadImg(self.item.getImg()), (48, 48)), self.pos)
				item_left = self.window.gameData.item_left(self.item)
				color = (255, 255, 255) if item_left else(255, 0, 0)
				surface, rect = self.other_font.render(str(item_left), color, size=15)
				blit_topright(screen, surface, (self.pos[0]+43, self.pos[1]+32))
			except FileNotFoundError: 
				self.item = None

	def mouse_on(self, last_widget): 
		if self.item is None: 
			return
		pg.draw.rect(self.screen, (255, 0, 0), self.rect, 1)
		self.drawDetail()

	def mouse_off(self, widget): 
		self.clearDetail()
		self.screen.blit(self.window.bgd.subsurface(self.rect), self.rect)

	def mouseDrag(self): 
		if (self.item and self.window.selectedUnit and self.available and 
			self.item.type in self.window.selectedUnit.unit.unitBase.equip): 

			itemImg = pg.transform.smoothscale(loadImg(self.item.getImg()), (48, 48))
			self.screen.blit(self.window.bgd, (0, 0))
			widget = self.window.widgetList.findArea(pg.mouse.get_pos())
			if isinstance(widget, EquipBox): 
				pg.draw.rect(self.screen, (255, 0, 0), widget.rect, 1)
			self.screen.blit(itemImg, pg.mouse.get_pos())

class ItemAreaLine(Line_of_VScrollArea): 
	def __init__(self, rect, window, screen, parent): 
		Line_of_VScrollArea.__init__(self, rect, window, screen, parent)
	def __iter__(self): 
		return self.itemAreaList.__iter__()
	def __getitem__(self, key): 
		return self.itemAreaList[key]

class AllItemArea(Monoheight_VScrollArea): 
	def __init__(self, rect, window, screen, parent): 
		Monoheight_VScrollArea.__init__(self, rect, window, screen, parent)
		self.scrollBar = VScrollBar((255, 255, 255), Rect((675, 345), (3, 298)), window, screen, self)
	def __iter__(self): 
		return self.itemAreaLine_list.__iter__()
	def __len__(self): 
		return 6
	def __getitem__(self, key): 
		return self.itemAreaLine_list[key]
	def searchItem(self, item): 
		for itemAreaLine in self: 
			for itemArea in itemAreaLine: 
				if itemArea.item == item: 
					return itemArea
		return None
	def set_itemLine_list(self, itemList): 
		self.itemLine_list = []
		index = 0
		while index < len(itemList): 
			self.itemLine_list.append(itemList[index: index+6])
			index += 6
	def show(self, screen=None): 
		if screen is None: 
			screen = self.screen
		startLine = self.startLine

		for itemLine, itemAreaLine in zip_longest(self.itemLine_list[startLine: startLine+6], self, fillvalue=[None]*6): 
			for item, itemArea in zip_longest(itemLine, itemAreaLine): 
				itemArea.item = item
				itemArea.show(screen)

		self.scrollBar.show(screen)

class FullWidget(Widget): 
	def __init__(self, window): 
		Widget.__init__(self, window)
	class DefaultState(Widget.DefaultState): 
		default = True
		def mouseDrop(self, dragging): 
			self.window.screen.blit(self.window.bgd, (0, 0))

class ItemWindow(VB_Window, UnitPanelMixin): 
	typeButtonOrder = '片手 両手 射撃 杖 鞭 爪 盾 鎧 獣装 法衣 道具 素材'.split()
	class UnitSelectedState(VB_Window.NormalState): 
		def __setup__(self): 
			VB_Window.NormalState.__setup__(self)
			self.allUnitArea.state = self.allUnitArea.UnitSelectedState

	def __init__(self, gameData, screen, itemDict): 
		self.fullWidget = FullWidget(self)
		VB_Window.__init__(self, screen, gameData)
		self.itemDict = itemDict
		self.hiredUnitList = gameData.hiredUnitList
		self.selectedTypeButton = None
		self.selectedUnit = None

		self.set_root_pnl(screen)
		self.root_bt_list = [self.bt_nextTurn, self.bt_campaign, self.bt_organizeTeam, self.bt_hire]
		self.bt_item.index = 1

		self.equipBoxList = [EquipBox(i, self, (545+70*i, 285), screen, self.fullWidget) for i in range(2)]

		self.typeButtonList = [TypeButton(typename, (300, 345+25*i), self, screen, self.fullWidget) 
			for (i, typename) in enumerate(self.typeButtonOrder)]

		self.allItemArea = AllItemArea(Rect((375, 345), (303, 298)), self, screen, self.fullWidget)
		self.allItemArea.itemAreaLine_list = [ItemAreaLine(Rect((375, 345+50*i), (50*6-2, 48)), self, screen, 
			self.allItemArea) for i in range(6)]
		for i, itemAreaLine in enumerate(self.allItemArea.itemAreaLine_list): 
			itemAreaList = []
			for j in range(6): 
				itemAreaList.append(ItemArea(self, (i, j), screen, itemAreaLine))
			itemAreaLine.itemAreaList = itemAreaList

		self.setAllUnitArea(UnitArea, AllUnitArea)
		
		self.widgetList_normal = WidgetList(self, [self.allItemArea, self.allUnitArea]+
			self.typeButtonList+self.root_bt_list)
		self.widgetList_selected = WidgetList(self, [self.allItemArea, self.allUnitArea]+self.equipBoxList+
			self.typeButtonList+self.root_bt_list)

		self.backgroundImg = loadImg(r'event\cg_ye_24c.bmp')
		self.set_bgd_base()
		self._bgd_normal = None
		self._bgd_selected = None
		self.bgd_dict.update({self.NormalState: 'bgd_normal', 
			self.UnitSelectedState: 'bgd_selected', 
			})
		self.widgetList_dict.update({self.NormalState: 'widgetList_normal', 
			self.UnitSelectedState: 'widgetList_selected', 
			})
		self.bFullScreen = False

	def set_bgd_base(self): 
		bgd = self.backgroundImg.copy()
		bgd.blit(loadImg(r'interface\slg_ui\rORG_bg01.png'), (0, 0))
		bgd.blit(loadImg(r'interface\slg_ui\rEquip_bg01.png'), (0, 200))
		bgd.blit(loadImg(r'interface\slg_ui\rORG_bg03a.png'), (700, 200))
		bgd.blit(loadImg(r'interface\slg_ui\root_ui.png'), (0, 0))
		self.draw_root_pnl(bgd)

		for typeButton in self.typeButtonList: 
			typeButton.show(bgd)
		
		self.bgd_base = bgd

	def set_bgd_normal(self): 
		self._bgd_normal = self.bgd_base.copy()
		self.typeButtonList[0].setSelect(self._bgd_normal)
		self.setUnit()

	def set_bgd_selected(self): 
		self._bgd_selected = self.bgd_normal.copy()

	@property
	def bgd_selected(self): 
		if self._bgd_selected is None: 
			self.set_bgd_selected()
		return self._bgd_selected

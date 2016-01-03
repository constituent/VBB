#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from .basic import *

class Widget(Stateful): 
	def __init__(self, window, screen=None, parent=None): 
		self.window = window
		self.screen = screen
		self.hintShowing = False
		self._parent = None
		self.parent = parent
		self.children = []
	@property
	def parent(self): 
		return self._parent
	@parent.setter
	def parent(self, value): 
		if self.parent is not None: 
			raise RuntimeError('Can not change parent')
		if value is not None: 
			value.children.append(self)
		self._parent = value
	def addChild(self, child): 
		# 暂时不提供更改parent的方法，当真需要时再说
		child.parent = self
	
	# def collidepoint(self, pos): 
	# 	if self.pos[0]<pos[0]<self.pos[0]+self.width and self.pos[1]<pos[1]<self.pos[1]+self.height: 
	# 		return True
	# 	else: 
	# 		return False
	def findChild(self, pos): 
		for child in self.children: 
			if child.collidepoint(pos): 
				return child.findChild(pos)
		return self
	class DefaultState(State): 
		default = True
		def mouse_on(self, last_widget): 
			if self.parent is not None: 
				self.parent.mouse_on(last_widget)
		def mouse_off(self, widget): 
			if self.parent is not None: 
				self.parent.mouse_off(widget)
		def showHint(self): 
			if self.parent is not None: 
				self.parent.showHint()

		for methodName in ['leftDoubleClick', 'leftClick', 'wheelClick', 'rightClick', 
			'wheelUp', 'wheelDown', 'mouseCatch', 'mouseDrag']: 
			exec('''\
def {methodName}(self): 
	if self.parent is not None: 
		self.parent.{methodName}()'''.format(methodName=methodName))

		def mouseDrop(self, dragging): 
			if self.parent is not None: 
				self.parent.mouseDrop(dragging)

		def show(self, screen=None): 
			pass

class RectWidget(Widget): 
	def __init__(self, rect, window, screen, parent=None): 
		Widget.__init__(self, window, screen, parent)
		self.rect = rect
	def collidepoint(self, pos): 
		return self.rect.collidepoint(pos)
	@property
	def pos(self):
		return self.rect.topleft
	@property
	def width(self):
		return self.rect.width
	@property
	def height(self):
		return self.rect.height

class WidgetList(): 
	def __init__(self, belong, widgetList=None): 
		self.defaultArea = belong.fullWidget
		if widgetList is None: 
			widgetList = []
		self.widgetList = [widget for widget in widgetList if widget is not None]
		self.last_widget = self.defaultArea

		def constructMesh(widgetList, p, wh): 
			xList = sorted(set(widget.pos[p] for widget in widgetList) | set(widget.pos[p]+getattr(widget, wh) for widget in widgetList))
			x_widget_list = [set() for _ in range(len(xList))]
			for widget in widgetList: 
				# for i in (i for (i, x) in enumerate(xList) if widget.pos[p] <= x < widget.pos[p]+getattr(widget, wh)): 
				# 	x_widget_list[i].add(widget)

				# 上面的更优雅，下面的对于有序的xList及时break。所以还是用下面那种了

				for i, x in enumerate(xList): 
					if x < widget.pos[p]: 
						continue
					elif widget.pos[p] <= x < widget.pos[p]+getattr(widget, wh): 
						x_widget_list[i].add(widget)
					elif x >= widget.pos[p]+getattr(widget, wh): 
						break
			return xList, x_widget_list

		self.xList, self.x_widget_list = constructMesh(self.widgetList, 0, 'width')
		self.yList, self.y_widget_list = constructMesh(self.widgetList, 1, 'height')

	def __iter__(self): 
		return self.widgetList.__iter__()

	def __len__(self): 
		return self.widgetList.__len__()
		
	def findArea(self, pos): 
		def agdg(p, xList): 
			return next((i for (i, x) in enumerate(xList) if x>=pos[p]), 0)-1
		
		if self.widgetList: 
			widgetList = self.x_widget_list[agdg(0, self.xList)] & self.y_widget_list[agdg(1, self.yList)]
		else: 
			widgetList = []
		
		for widget in widgetList: 
			if widget.collidepoint(pos): 
				return widget.findChild(pos)
		return self.defaultArea

class RectButton(RectWidget): 
	def __init__(self, imgList, pos, window, screen, available=True, parent=None): 
		self.imgList = imgList
		rect = self.imgList[0].get_rect()
		rect.topleft = pos
		RectWidget.__init__(self, rect, window, screen, parent)
		self.available = available
	class DefaultState(RectWidget.DefaultState): 
		default = True
		def show(self, screen=None): 
			if screen is None: 
				screen = self.screen
			screen.blit(self.imgList[self.index], self.pos)
		def mouse_on(self, last_widget): 
			if self.available: 
				self.index = self.mouse_on_index
				self.show()
		def mouse_off(self, widget): 
			if self.available: 
				self.index = self.mouse_off_index
				self.show()

class SelectableRectButton(RectButton): 
	class DefaultState(RectButton.DefaultState): 
		default = True
		def mouse_on(self, last_widget): 
			if self.available and not self.selected: 
				self.index = self.mouse_on_index
				self.show()
		def mouse_off(self, widget): 
			if self.available and not self.selected: 
				self.index = self.mouse_off_index
				self.show()

class ScrollArea(RectWidget): 
	pass

class VScrollArea(ScrollArea): 
	pass

class Monoheight_VScrollArea(VScrollArea): 
	def __init__(self, rect, window, screen, parent=None): 
		VScrollArea.__init__(self, rect, window, screen, parent)
		self.startLine = 0
	class DefaultState(VScrollArea.DefaultState): 
		default = True
		def wheelUp(self, lineCount=1): 
			if self.startLine>0: 
				self.startLine -= lineCount
				self.startLine = max(self.startLine, 0)
				# self.window.update_ubArea()
				last_widget = self.window.widgetList.findArea(pg.mouse.get_pos())
				last_widget.mouse_off(None)
				self.show(self.window.bgd)
				# self.screen.blit(self.window.bgd, (0,0))
				self.screen.blit(self.window.bgd.subsurface(self.rect), self.rect)
				
		def wheelDown(self, lineCount=1): 
			temp = len(self.itemLine_list)-len(self)
			if self.startLine < temp: 
				self.startLine += lineCount
				self.startLine = min(self.startLine, temp)
				# self.window.update_ubArea()
				last_widget = self.window.widgetList.findArea(pg.mouse.get_pos())
				last_widget.mouse_off(None)
				self.show(self.window.bgd)
				# self.screen.blit(self.window.bgd, (0,0))
				self.screen.blit(self.window.bgd.subsurface(self.rect), self.rect)

class Line_of_VScrollArea(RectWidget): 
	pass

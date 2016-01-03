#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, time
from enum import Enum
from collections import namedtuple

from .widget import *

class BaseWindow(Stateful): 
	class BaseGameState(State): 
		default = True
		def processEvent(self): 
			for event in self.processBaseEvent(): 
				pass

		def processOther(self): 
			pass

	class GameState(BaseGameState): 
		def __setup__(self): 
			BaseWindow.BaseGameState.__setup__(self)
			self.screen.blit(self.bgd, (0,0))
		def __clear__(self): 
			BaseWindow.BaseGameState.__clear__(self)
			self.lastState = self.state

	class FreezeState(GameState): 
		pass

	class TerminateState(FreezeState): 
		def __setup__(self): 
			BaseWindow.FreezeState.__setup__(self)
			self.terminate()
		def processEvent(self): 
			# 供重写了__setup__方法的子类继承用
			for event in self.processBaseEvent(): 
				if event.type == KEYDOWN: 
					if event.key == K_ESCAPE: 
						self.state = self.lastState
					elif (event.key == K_F4 and event.mod&KMOD_ALT): 
						self.terminate()

	def __init__(self, screen): 
		self.screen = screen
	def terminate(self): 
		pg.quit()
		sys.exit()
	def processBaseEvent(self): 
		'处理通用的事件，例如切换全屏、退出游戏等等'
		for event in pg.event.get(): 
			self.noEventTime = 0
			if event.type == QUIT: 
				self.state = self.TerminateState
			elif event.type == KEYDOWN: 
				if event.key == K_RETURN and event.mod&KMOD_ALT: 
					if self.bFullScreen: 
						pg.display.set_mode((1280, 720))
					else: 
						pg.display.set_mode((1280, 720), FULLSCREEN | HWSURFACE)
					self.screen.blit(self.bgd, (0,0))
					self.bFullScreen = not self.bFullScreen
				else: 
					yield event
			else: 
				yield event

DOUBLECLICKINTERVAL = 0.5
# MouseAction = Enum('MouseAction', ['LEFTDOUBLECLICK', 'LEFTCLICK', 'WHEELCLICK', 'RIGHTCLICK', 
# 	'WHEELUP', 'WHEELDOWN'])
# EventProcess = namedtuple('EventProcess', ['judgeFunction', 'callee'])
# eventList = {k: EventProcess(*v) for k, v in eventList.items()}
class MouseEvents(BaseWindow): 
	def __init__(self, screen): 
		BaseWindow.__init__(self, screen)
		self.lastLeftClick = (0, (0, 0))
		self.dragging = None
		self.mouseMoved = False
	def processBaseEvent(self): 
		for event in BaseWindow.processBaseEvent(self): 
			if event.type == MOUSEBUTTONDOWN: 
				if event.button == 1: 
					self.dragging = self.widgetList.findArea(event.pos)
					self.dragging.mouseCatch()
					self.mouseMoved = False
			elif event.type == MOUSEBUTTONUP: 
				if event.button == 1: 
					if not self.mouseMoved: 
						lastLeftClickedTime, lastPos = self.lastLeftClick
						self.lastLeftClick = (time.time(), event.pos)
						if self.lastLeftClick[1] == lastPos and self.lastLeftClick[0]-lastLeftClickedTime<DOUBLECLICKINTERVAL: 
							self.leftDoubleClick(event)
						else: 
							self.leftClick(event)
					else: 
						self.widgetList.findArea(event.pos).mouseDrop(self.dragging)
					self.dragging = None
				elif event.button == 2: 
					self.wheelClick(event)
				elif event.button == 3: 
					self.rightClick(event)
				elif event.button == 4: 
					self.wheelUp(event)
				elif event.button == 5: 
					self.wheelDown(event)
			elif event.type == MOUSEMOTION: 
				self.mouseMoved = True
				if self.dragging is not None: 
					# 如果想在dragging时触发mouse_on，显式调用吧
					# 毕竟有时不想触发mouse_on
					self.dragging.mouseDrag()
				else: 
					widget = self.widgetList.findArea(event.pos)
					if widget != self.widgetList.last_widget: 
						last_widget = self.widgetList.last_widget
						last_widget.mouse_off(widget)
						self.widgetList.last_widget = widget
						widget.mouse_on(last_widget)
			else: 
				yield event

	# print("{methodName}")
	for methodName in ['leftDoubleClick', 'leftClick', 'wheelClick', 'rightClick', 'wheelUp', 'wheelDown']: 
		exec('''\
def {methodName}(self, event): 
	widget = self.widgetList.findArea(event.pos)
	widget.{methodName}()'''.format(methodName=methodName))

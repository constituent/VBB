#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from os.path import *
from functools import lru_cache

import pygame as pg
import pygame.freetype
from pygame.locals import *
from pygame.sprite import DirtySprite, LayeredDirty

from state import State, stateful, Stateful
	
BASE_DATA_PATH = join(dirname(dirname(__file__)), 'data')

def get_bgm_path(filename): 
	return join(BASE_DATA_PATH, 'sound', 'bgm', filename)

@lru_cache(maxsize=1024)
def loadImg(relativePath, flipVertically=False): 
	if not (flipVertically is True or flipVertically is False): 
		raise RuntimeError('invalid parameter')
	if flipVertically: 
		img = pg.transform.flip(loadImg(relativePath), True, False)
	else: 
		if isinstance(relativePath, str): 
			relativePath = (relativePath, )
		filePath = join(BASE_DATA_PATH, *relativePath)
		# 文件名里有汉字的话直接load(filePath)会出错
		with open(filePath, 'rb') as f: 
			img = pg.image.load(f)

	return img

def splitImg(img, x, y=1, *, sliceWidth=None, sliceHeight=None): 
	width, height = img.get_size()
	if sliceWidth is None: 
		assert width%x == 0
		w = width//x
	else: 
		w = sliceWidth
	if sliceHeight is None: 
		assert height%y == 0
		h = height//y
	else: 
		h = sliceHeight

	result = []
	for j in range(y): 
		for i in range(x): 
			result.append(img.subsurface((i*w, j*h), (w, h)))

	return result

def combineImg(imgList, axis=0, *, bgColor=None, interval=0): 
	imgList = [i for i in imgList if i is not None]
	if not imgList: 
		return None
	
	if axis == 0: 
		maxHeight = max(i.get_height() for i in imgList)
		if bgColor is None: 
			surface = pg.Surface((sum(img.get_width() for img in imgList)+interval*(len(imgList)-1), maxHeight), 
				SRCALPHA, 32)
		else: 
			surface = pg.Surface((sum(img.get_width() for img in imgList)+interval*(len(imgList)-1), maxHeight))
			surface.fill(bgColor)
		offset = 0
		for img in imgList: 
			surface.blit(img, (offset, 0))
			offset += img.get_width()+interval
	elif axis == 1: 
		maxWidth = max(i.get_width() for i in imgList)
		if bgColor is None: 
			surface = pg.Surface((maxWidth, sum(img.get_height() for img in imgList)+interval*(len(imgList)-1)), 
				SRCALPHA, 32)
		else: 
			surface = pg.Surface((maxWidth, sum(img.get_height() for img in imgList)+interval*(len(imgList)-1)))
			surface.fill(bgColor)
		offset = 0
		for img in imgList: 
			surface.blit(img, (0, offset))
			offset += img.get_height()+interval

	return surface

def combineNumberImg(imgList, number): 
	# 0-9加小数点
	def getIndex(c): 
		if c == '.': 
			return 10
		else: 
			return int(c)
	return combineImg(imgList[getIndex(c)] for c in str(number))

class MyDirtySprite(DirtySprite): 
	# 默认情况下不显示的Sprite
	def __init__(self, screen): 
		DirtySprite.__init__(self)
		self.screen = screen
		self.image = pg.Surface((0, 0))
		self.rect = Rect(0, 0, 0, 0)
	
class HintArea(MyDirtySprite): 
	def get_pos(self): 
		pos = list(pg.mouse.get_pos())
		if pos[0]+self.rect.width>self.screen.get_width(): 
			pos[0] = self.screen.get_width()-self.rect.width
		if pos[1]+self.rect.height>self.screen.get_height(): 
			pos[1] = self.screen.get_height()-self.rect.height

		return pos
	def update(self, str_List, font): 
		hint_area_List = [font.render(s, (0, 0, 0), (255, 255, 255))[0] for s in str_List]
		self.image = combineImg(hint_area_List, 1, bgColor=(255, 255, 255))
		self.rect = self.image.get_rect()
		self.rect.topleft = self.get_pos()# 先获取rect，再由rect计算pos

def blit_topright(surface, source, topright, *args, **kwargs): 
	rect = source.get_rect()
	rect.topright = topright
	surface.blit(source, rect, *args, **kwargs)

def blit_sameRect(surface, source, rect): 
	surface.blit(source.subsurface(rect), rect)
#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from main import *
from vb import *
from battleWindow import BattleWindow
from hireUnitWindow import HireUnitWindow
from itemWindow import ItemWindow
from organizeTeamWindow import OrganizeTeamWindow

# venus blood immortal 圣女之血永不朽
# 圣女之血，于焉坠落
# 如果VB的系统要改手游，可以改成塔防，一座塔/一个敌人不是一个单位而是一个师团。当然塔未必是不能移动的
# 复活时加的血没显示？

# 现在范围无效过于重要了，特别是高难度除了特化了的T被攻击轻易就是上万的伤害
# 考虑改成非主目标的伤害固定为主目标伤害的一半，而不是分别计算
# 弄成一个可以设定的选项，包括设定只对敌方攻击己方时有效

# 次元作为攻击技能已经很强了，考虑增加防御能力，例如附带的格挡固定为75，或者至少为75
# 徽章可以考虑通过研究科技来开放。当然科技还可以包括别的，比如增加收入、减少工资

# 前排受到物理伤害减半
# 非target成为被攻击主目标的，无论是因为前进、后逸、防阵还是前排挡排的枪，也物理伤害减半
# 这两个减半能不能叠加呢……保守一点，还是不叠加了
# 奇袭现在意义略小，考虑改成被奇袭到前排的单位不会物理伤害减半
# 如果奇袭是随机交换位置对玩家太不利。只对敌方是这个效果感觉额外引入复杂性

# 鼠标停留后自动搜寻师团和单位。具体地说，编成界面（已经加入师团的）单位上停留找师团，师团中某单位上停留找单位，
# 装备界面装备上停留找装备着的单位。1、3更重要，因为2可以通过过滤（兵种）来帮助定位且并不太实用。
# 如果加入行号显示有助于2之后更改装备，但也并非太必要

# 自己治愈改成按maxHP计算。但似乎并非太必要且增加复杂性，需要仔细衡量
# 次元溢出75的部分当成兜割算
# 城壁当成按比例增减物理伤害。开方函数可以保留

# 限制数量的高级装备未必要固定两个技能，而是可以比如4选2
# 主角可以弄个技能树，玩家指定8个技能中的全部或者其中几个
# 主角可装备任意装备
# 单位可以变成装备
# 突出职业区别，现在只有毫无存在感的1.5倍循环伤害加成。加入职业天赋系统，每个单位在雇佣时可按职业选择3个天赋中的一个
# 天赋最好是功能型而不是数值型，例如“盾兵：以牙还牙，当被暴击时反击必然暴击；移形换影，替目标承担放射伤害”
# 而不是“法师：xxxx：治疗量增加10%”这样的。法术吸血？
# blader: 热血根性，若HP>1，则受到伤害后至少保留1点HP
# 龙血狂战：战斗开始时HP上限增加一倍
# lancer: 破法银枪，攻击时额外造成对方智力点伤害，不受龙鳞、巨大的影响
# shooter: 分裂之箭，范围攻击时对非主目标造成全额伤害
# 暴雨梨花，攻击次数*2，伤害减半。减少伤害溢出，并配合异常赋与。但被龙鳞克？
# 百步穿杨，按自己速度减对方闪避
# caster: 法术吸血
# 法术护盾：只受到一半伤害，但HP上限也减少同样数值。回合结束时HP上限恢复。感觉有点太强了，不过这游戏强调的是输出而不是硬度所以大概还好吧
# guarder: 以牙还牙，当被暴击时反击必然暴击。如果再加上攻击时，反击者暴击则必然暴击
# 程序上似乎稍微有点麻烦，当以牙还牙单位攻击以牙还牙单位的时候。总之鼓励盾兵当输出也是不错的
# 移形换影，替目标承担放射和对术反射的伤害
# destroyer：非暴击时伤害增加50%
# assasine：致命必杀时无视50%防御而非25%
# 若某次攻击杀死了目标，则不受反击（包括自爆？）。考虑到热血根性和复活，需要直接判断而不能通过剩余HP
# 当然这个的平衡性好像有点难
# 为了那些比如当T的shooter，再提供一个公共的天赋，例如误入歧职：全属性+10%

# 初始5难度：easy normal hard very hard despair
# 追加难度：thanatos inferno
# hard通关后那些改变divine的称号是否改变变成可选
# very hard通关后称号和装备的活性、指挥、弱体技能可以改变
# despair通关后单位可以装备化
# thanatos通关追加新模式，如电脑一般不能打称号，但可以以不变的价格招多个同一种单位
# 主角就叫巧夢(たくむ)好了（笑）

moon = '火'
daylight = True

screen = pg.display.set_mode((1280, 720))
# pg.display.set_caption("Virtual Battle Immortal")
pg.display.set_caption("Venus Blood Immortal ver. 0.01")

# new game
gameData = GameData(moon, daylight, itemList)

# from core.unit import MoonEffect
# gameData.hiredUnitList = [Unit(ub, 1, moonEffect=MoonEffect.best, level=200) for ub in unitBaseList[: 60]]

battle_bgm_file_path = get_bgm_path('21 終末に見るユメ -Battle12：Gaia of eternal dream-.ogg')

def run_hire(): 
	hireUnitWindow = HireUnitWindow(gameData, screen, unitBaseDict, tacticaList, tacticaDict)
	return hireUnitWindow.run()

def run_item(): 
	itemWindow = ItemWindow(gameData, screen, itemDict)
	return itemWindow.run()

def run_organize(): 
	organizeTeamWindow = OrganizeTeamWindow(gameData, screen)
	return organizeTeamWindow.run()

def run_normal(): 
	with play_bgm(DEFAULT_BGM): 
		result = WindowType.HireUnitWindow
		while True: 
			result = window_dict[result]()
			if result == WindowType.BattleWindow: 
				break

	return run_battle

def run_battle(): 
	# 显示不要太透明
	yoru = -10 if gameData.daylight else 10
	background = Background(gameData.moon, gameData.daylight, 蟲=10, 神=10, 夜=yoru)
	with play_bgm(battle_bgm_file_path): 
		for battle in getBattles(gameData, background): 
			battleWindow = BattleWindow(screen, battle, gameData)
			battleResult = battleWindow.run()
			if battleResult in (BattleResult.勝利, BattleResult.完勝): 
				break

	return run_normal

window_dict = {
	WindowType.OrganizeTeamWindow: run_organize, 
	WindowType.HireUnitWindow: run_hire, 
	WindowType.BattleWindow: run_battle, 
	WindowType.ItemWindow: run_item, 
}

result = run_normal
while True: 
	result = result()

# 逃跑
# 开战
# 设定

# 称号改变守护属性弄成可选项
# 成就系统
# 防止多开
# 信号机制
# parent。看看之前写的pyqt gui
# netRetry可以提供关键字参数不显示任何retry信息；要显示的话，也要注意stdout不是线程安全的

# F12是重启（回标题画面）
# F2 save（当然只是部分状态下可用），F3 load
# 加上“攻”和“守”的地形效果。虽然似乎没什么必要，攻防智速的地形效果
# 不同城的经济收入是不同的，至少有大城和小城之分
# 专守可以有个数值，满100才是50%减伤
# 学学三国志，比如可以有多个剧本，打完一个剧本开一个徽章
# 复活改成每回合（或每敌方/我方回合）可发动一次。注意显示时是否涂黑。都改好了，只是注意在回合结束/开始时刷新recovered为False
# pygame侵入比如物理攻击代码以得知哪些效果（例如闪避）发生了以显示，感觉应该采用类似于logging模块那样类似于全局变量的形式
# 在《编写高质量代码 改善Python程序的91个建议》里还把其称为通过模块实现单件模式

# 按https://www.python.org/dev/peps/pep-0506/#alternatives所述
# 重放录像其实只需要保存一个伪随机数生成器的初始种子，就能得到完全一样的伪随机序列，于是暴击、闪避等等就成了确定性的行为了
# 某方全灭之后没有结束（未处理返回值非None的情况）

# 所有同名同数值的Skill都返回同一个对象
# 攻击时随时可以调整目标，至少可以弄一个选项是否允许玩家这样做。需要向玩家提示下一个行动的单位？


# def  StatusCalc(sta_,Exp_,par): 
# 	if(par=='mor'){
# 		sta_ = sta_ + (int)((sta_ * sqrt(Exp_)/500) + (int)(sqrt(Exp_)/40));
# 		if(sta_ >  99){sta_ =  99;}
# 	}else{
# 		sta_ = sta_ + (int)((sta_ * sqrt(Exp_)/200) + (int)(sqrt(Exp_)/25));
# 		if(sta_ > 999){sta_ = 999;}
# 	}
# 	if(sta_ < 1){sta_ = 1;}
# 	return sta_;

# def calExp(level): 
# 	return 10*(level-1)**2
# from math import sqrt
# sta_ = 13
# level = 150
# Exp_ = calExp(level)
# print(sta_ + (int)((sta_ * sqrt(Exp_)/200) + (int)(sqrt(Exp_)/25)))
# print(int(sta_*(1+sqrt(Exp_)/500)+sqrt(Exp_)/25))

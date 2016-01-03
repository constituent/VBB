#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from itertools import chain

# 個別横座標補正指定(自軍)
personXYp_dict = {
	'm0038': [ 120,   0], # マンティコア
	'm0044': [  50,   0], # ダンタリオン
	'm0046': [ 100,   0], # グリフォン
	'm0047': [ 100,   0], # カトブレパス
	'm0053': [  30,   0], # アンドロリマウス
	'm0057': [ 130,   0], # バジリスク

	'm0059': [ 100,   0], # クジャラボラス
	'm0082': [ 100,   0], # 火車
	'm0134': [  50,  50], # デスドラグーン
	'm0152': [ 150,   0], # ドラゴンゾンビ
	'm0161': [  50,   0], # マシンドラゴン
	'm0185': [ 100,   0], # マシンザウルス

	'm0196': [ 100,   0], # シルバードラゴン
	'm0201': [ 100,   0], # コロッサルドラゴン
	'm0207': [  50,   0], # シーサーペント
	'm0208': [  50,   0], # マグマサーペント
	'm0211': [  50,   0], # ガストサーペント
	'm0216': [ 100,   0], # ゴールドドラゴン

	'm0217': [ 100,   0], # アビスヒュドラ
	'm0222': [ 100,   0], # クイーンケルベロス
	'm0232': [ 100,   0], # 異獣バグス
	'm0236': [ 100,   0], # 異獣プラタルス
	'm0239': [ 100,   0], # 変異獣ドグマ
	'm0242': [ 100,   0], # 変異獣ギグス

	'm0243': [  50,   0], # 変異獣プラトナム
	'm0247': [  50,   0], # 白虎
	'm0261': [ 100,  75], # 朱雀
	'm0277': [  50,   0], # 狂天使アラキバ
	'm0343': [  50,  50], # 竜騎士
	'm1043': [  25,   0], # マガフ
	'm1044': [  25,   0], # 禁呪マガフ

	'm1046': [  80,   0], # 焔竜王ジュリア
	'm1047': [  80,   0], # 地竜公オルガ
	'm0281': [  80,   0], # リンドヴルム

	'm0040': [   0,  75], # ラードーン
	'm0061': [ -50,   0], # ソードジーニ
	'm0077': [ -25,   0], # ノクターンスカラー
	'm0079': [ -25,   0], # 般若武者
	'm0111': [ -10,   0], # インキュバス
	'm0161': [   0,   0], # レイスソルダート

	'm0171': [ -50,  25], # エーテルモノリス
	'm0191': [  10,   0], # クリスタルドラゴン
	'm0212': [  75,   0], # アーマードラゴン
	'm0205': [  15,  25], # 応龍
	'm0213': [  75,   0], # ワイバーン
	'm0233': [   0,  50], # バルバ・ドラグス
}

# 個別横座標補正指定(敵軍)
personXYe_dict = {
	'm0038': [ 130,   0], # マンティコア
	'm0039': [ 100,   0], # ジュエルビースト
	'm0043': [ 100,   0], # シグムント
	'm0046': [ 115,   0], # グリフォン
	'm0047': [ 115,   0], # カトブレパス
	'm0049': [ 100,   0], # アイアンタートル

	'm0057': [ 130,   0], # バジリスク
	'm0059': [ 130,   0], # クジャラボラス
	'm0071': [  50,   0], # ユニコロン
	'm0082': [  80,   0], # 火車
	'm0122': [  80,   0], # アスモデ
	'm0134': [ 100, -50], # デスドラグーン

	'm0152': [ 130,   0], # ドラゴンゾンビ
	'm0161': [  80,   0], # レイスソルダート
	'm0154': [  50,   0], # ダークストーカー
	'm0166': [ 100,   0], # マシンドラゴン
	'm0185': [ 110,   0], # マシンザウルス
	'm0196': [ 280,   0], # シルバードラゴン

	'm0201': [ 150,   0], # コロッサルドラゴン
	'm0207': [ 200,   0], # シーサーペント
	'm0208': [ 200,   0], # マグマサーペント
	'm0211': [ 200,   0], # ガストサーペント
	'm0212': [ 110,   0], # アーマードラゴン
	'm0213': [ 180,   0], # ワイバーン

	'm0216': [ 280,   0], # ゴールドドラゴン
	'm0217': [ 100,   0], # アビスヒュドラ
	'm0222': [ 120,   0], # クイーンケルベロス
	'm0232': [ 120,   0], # 異獣バグス
	'm0247': [ 100,   0], # 白虎
	'm0261': [ 125, -50], # 朱雀

	'm0275': [ 130,   0], # 玄武
	'm0277': [ 100,   0], # 狂天使アラキバ
	# 'm0281': [ 280,   0], # リンドヴルム
	'm0281': [ 240,   0], # リンドヴルム
	'm0343': [ 100, -50], # 竜騎士
	'm1043': [  50,   0], # マガフ
	'm1044': [  50,   0], # 禁呪マガフ

	'm1046': [ 100,   0], # 炎竜王ジュリア
	'm1047': [ 120,   0], # 地竜公オルガ

	'm1048': [ 130,  50], # 聖女アイリス※神獣
	'm1050': [ 130,   0], # 始原淫魔アルミランダ※神獣
	'm1052': [ 160,   0], # 亡者の始祖ハムド※神獣
	'm1054': [ 130,   0], # 魔神竜ウェルギウス※神獣
	'm1055': [ 130,   0], # 暴食竜ウェルギウス※神獣
	'm1056': [ 130,   0], # 戦艦クルセロ※神獣

		# 
	'm0024': [   0, -50], # エルダーギガース
	'm0026': [  50,   0], # オーガ
	'm0035': [  50,   0], # マキシマムオーガ
	'm0040': [  25,   0], # ラードーン
	'm0041': [  25,   0], # ラミア
	'm0042': [  50,   0], # ケルベロス

	'm0048': [  90,   0], # 蛇神カドゥルー
	'm0053': [  80,   0], # アンドロリマウス
	'm0054': [  50,   0], # デスフロッグ
	'm0066': [  25,   0], # アルウラネ
	'm0069': [  25,   0], # ティターニア
	'm0072': [ -10,   0], # サテュロス

	'm0078': [  45,   0], # ポンポコ忍者
	'm0099': [  45,   0], # ヤマタノオロチ
	'm0104': [  50,   0], # デビル
	'm0106': [  15, -10], # ベレト
	'm0121': [  30,   0], # イビルライダー
	'm0123': [  30,   0], # アークデーモン

	'm0126': [  40,   0], # グール
	'm0127': [ -10,   0], # ミイラ女
	'm0137': [ -10,   0], # バンシー
	'm0150': [  25,   0], # ノスフェラトゥ
	'm0155': [  40,   0], # マンイーター
	'm0162': [  40,   0], # ミミック

	'm0171': [ -25, -25], # エーテルモノリス
	'm0175': [  25,   0], # アルケフェアリー
	'm0177': [  50,   0], # ガーゴイル
	'm0179': [  30,   0], # エーテルガーター
	'm0182': [  25,   0], # センチュリオン
	'm0186': [  25,   0], # ドラゴンパピー

	'm0191': [ 100,   0], # クリスタルドラゴン
	'm0197': [  40,   0], # ドラゴバルーン
	'm0206': [  80,   0], # ドラゴンソウル
	'm0225': [  50,   0], # 異獣ベヌフライ
	'm0227': [  25,   0], # 触手姫
	'm0232': [   0,   0], # 異獣バグス

	'm0234': [  25,   0], # ガイアスキャリア
	'm0236': [ 100,   0], # 異獣プラタルス
	'm0242': [ 125,   0], # 変異獣ギグス
	'm0240': [  40,   0], # 変異獣ストローワ
	'm0243': [ 100,   0], # 変異獣プラトナム
	'm0251': [  75,   0], # フォモル

	'm0282': [  35,   0], # 狂天使アザゼル
}

for i in chain(range(2031, 2040), [2041, 2042, 2043, 2048, 5046, 5047]): 
	# 敌方的魔神龙，坐标是对的；但敌方的别的（VBG里的）大型单位，例如ガイアスクイーン是不对的
	# 己方的全不对
	personXYe_dict.update({'m'+str(i): [70, 25]})
	personXYp_dict.update({'m'+str(i): [35, 25]})

personXYe_dict.update({'m2035': [90, 25]})
personXYe_dict.update({'m2036': [90, 25]})
personXYe_dict.update({'m2038': [90, 25]})

personXYp_dict.update({'m1048': [50, 0]})
personXYp_dict.update({'m1050': [50, 50]})
personXYp_dict.update({'m1052': [80, 50]})
personXYp_dict.update({'m1054': [50, 50]})
personXYp_dict.update({'m1055': [50, 50]})
personXYp_dict.update({'m1056': [100, 50]})
personXYe_dict.update({'m5048': [70,  75]})
personXYp_dict.update({'m5048': [35, -25]})

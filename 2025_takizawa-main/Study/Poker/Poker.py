# -*- coding: utf-8 -*-
# poker用のclass
import random

class Card:
    def __init__(self,s,n):
        self.suit = s
        self.num = n

    def disp(self):
        return self.suit+str(self.num)

class Poker:
    # コンストラクタ
    def __init__(self):
        list_word = ["s","h","d","c"]
        list_num = [1,2,3,4,5,6,7,8,9,10,11,12,13]
        ## 52枚のカード作成
        card_list = []
        for i in list_word:
            for j in list_num:
                card_list.append(Card(i,j))

        # カードをシャッフル
        card_list = random.sample(card_list,len(card_list))
        # 手札
        self.__hand = card_list[:5]
        # 山札
        self.__deck = card_list[6:]

    # ゲッタ
    def gethand(self):
        return self.__hand

    # 綺麗に表示
    def printhand(self):
        return list(map(lambda x:str(x.disp()),self.__hand))


    # 手札入れ替え
    # 指定された引数をデック先頭と入れ替え，デックからpop
    def change_card(self,change_num):
        for i in change_num:
            self.__hand[i] = self.__deck.pop(0)

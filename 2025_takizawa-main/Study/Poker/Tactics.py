# -*- coding: utf-8 -*-
import re
from collections import Counter

def tactics(hand,times):
    # <summary>
    # 手札と回数から何を変更するべきか決定するプログラムメソッド（これを作成する）
    # </summary>
    # <param name="hand">手札</param>
    # <param name="times">回数</param>
    # <returns>変更するカード番号を返す</returns>

    for i in range(len(hand)):
        # hand[i].num = 1
        print(hand[i].suit + str(hand[i].num))

    # # プログラム（簡単バージョン）

    # if (times % 2) == 0:
    #     return [0,2,4]
    # else:
    #     return [1,3]


    # ##以下が変更箇所！！

    # プログラム（１回目の対戦用）

    # ストレートよりも強い役が出ていたら変えない
    # フラッシュ判別
    hand_ = []
    for i in range(len(hand)):
        hand_i_ = hand[i].suit
        hand_.append(hand_i_)

    a, b, c, d =0, 0, 0, 0
    for i in range(len(hand)):
        if hand_[i] == 'h':
            a=a+1
        elif hand_[i] == 's':
            b=b+1
        elif hand_[i] == 'd':
            c=c+1
        elif hand_[i] == 'c':
            d=d+1

    if a==5 or b==5 or c==5 or d==5:
        return []

    # ストレート、フォーカード、フルハウスを判別するための前処理
    hand_ = []
    for i in range(len(hand)):
        hand_i_ = hand[i].num
        hand_.append(hand_i_)
    hand_.sort()

    # ストレート判別
    suto=0
    for i in range(len(hand)-1):
        if hand_[i+1] == hand_[i]+1:
            suto=suto+1
        elif hand_[0] ==1 and hand_[4]==13:
            suto=suto+1
    if suto==4:
        return []

    # フォーカード判別
    if hand_[0]==hand_[3] or hand_[1]==hand_[4]:
        return []
    
    # フルハウス判別
    if (hand_[0]==hand_[1]) and (hand_[3]==hand_[4]) and (hand_[1]==hand_[2] or hand_[2]==hand_[3]):
        return []
    
    # ストレートよりも強い役がなかったときの処理
    # 持ち札の数値だけからなるリストhand_を作成
    hand_ = []
    for i in range(len(hand)):
        hand_i_ = hand[i].num
        hand_.append(hand_i_)
    
    #持ち札の数値が一つでも揃っている場合
    if len(hand_) != len(set(hand_)):

        #手札における各数値の頻度の辞書
        count_dic = Counter(hand_)

        #辞書をもとに, 頻度最大の数値のリストを作成する
        keys = [k for k, v in count_dic.items() if v == max(count_dic.values())]

        #頻度が最大ではない, つまり変更対象の数値のインデックスリストを作成する
        change_index = []
        for i in range(len(hand_)):
            if hand_[i] in keys:
                continue
            else:
                change_index.append(i)
        return change_index

    #持ち札の数値が一つも揃っていない場合、全てを入れ替える
    else:
        return [0, 1, 2, 3, 4]





## 方針を以下に記す！

#一定以上強い役が出たら変えない
#ペアがあったら残す
#１、２、３、４、６のような場合、6のみを変える <-間に合わず


# if 持ち札のスコア＞＝ストレート:
#    変えない

# else:
   
#     if 持ち札の数が一つはそろっている:
#        持ち札で最も多く出ている数に揃える

#     else 持ち札の数が一つも揃っていない
#         絵柄で揃える



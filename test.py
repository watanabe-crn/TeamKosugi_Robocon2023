#!/usr/bin/env python
# _*_ coding: utf-8 _*_

from acctello_test import AccTello
from ballon import Ballon
import time
import random

# 風船の番号
# 1-----
# |    |
# -----2
# ※ 1 と 2 はそれぞれ、縦の距離と高さが当日確定します。




def main():
    
    acc = AccTello()

    # 識別対象の位置を設定
    # フィールドの左端からの距離を横、縦で測り入力。単位はcm

    # 1つ目の対象
    obj1_y = int(300)  # 前後
    obj1_z = int(100)  # 高さ
    # 2つ目の対象
    obj2_y = int(100)  # 前後
    obj2_z = int(150)  # 高さ
    
    
    # 風船
    bal_1 = Ballon(1,50,obj1_y,270,obj1_z)
    bal_2 = Ballon(2,340,obj2_y,90,obj2_z)
    bal = [bal_1,bal_2]

    # 開始
    acc.startGame()
    
    for i in range(len(bal)) :
        acc.move(bal[i])
    
    # 終了
    acc.endGame()
    
if __name__ == "__main__":
    main()

def get_next_balloon_no(i, bal_no, card_no):
    if i==0:
        # 一つ目の場合、ランダムで設定
        return random.randint(1,4)
    elif i==1:
        # 二つ目の場合、一つ目のカード番号により分岐
        if card_no[0] < 3:
            # 対角の風船
            if bal_no[0] + 2 > 4:
                return bal_no[0] - 2
            else:
                return bal_no[0] + 2
        else:
            # 隣の風船
            if bal_no[0] == 4:
                return 1
            else:
                return bal_no[0] + 1
    elif i==2:
        # 三つ目の場合、まだ確認していない風船のうち番号の小さい風船を設定
        for i in range(4):
            if i not in bal_no:
                return i





        



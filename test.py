#!/usr/bin/env python
# _*_ coding: utf-8 _*_

from acctello_test import AccTello
from ballon import Ballon
import time
import random

# 風船の番号
# 1----2
# |    |
# 4----3



def main():

    # アクセス用クラス
    acc = AccTello()

    # カメラ映像表示
    acc.showCamera()

    # 風船
    bal_1 = Ballon(1, 1,19,135)
    bal_2 = Ballon(2, 19,19,225)
    bal_3 = Ballon(3, 19,1,325)
    bal_4 = Ballon(4, 1,1,45)
    bal = [bal_1,bal_2,bal_3,bal_4]

    # 撮影済みカード番号（最大値）
    took_photo_no = 0

    # カード番号に対する風船
    card = [bal_1, bal_1, bal_1, bal_1]

    # メイン処理
    # 開始
    acc.startGame()

    acc.move(bal[0])


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





        



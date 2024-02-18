#!/usr/bin/env python
# _*_ coding: utf-8 _*_

from acctello import AccTello
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
    bal_1 = Ballon(-9,9)
    bal_2 = Ballon(9,9)
    bal_3 = Ballon(9,-9)
    bal_4 = Ballon(-9,-9)
    bal = [bal_1,bal_2,bal_3,bal_4]

    # 撮影済みカード番号（最大値）
    took_photo_no = 0

    # カード番号に対する風船
    card = [bal_1, bal_1, bal_1, bal_1]

    # メイン処理
    # 開始
    acc.startGame()

    # カード確認
    bal_no = []
    card_no = []
    for i in range(3):
        # 移動先の風船番号を取得
        next_baloon_no = get_next_balloon_no(i, next_baloon_no)

        # 取得した番号の風船に移動
        acc.move(bal(next_baloon_no))

        # 風船のカード確認
        ret = acc.conf_card(bal(next_baloon_no), took_photo_no)
        card[ret[0] - 1] = bal(next_baloon_no) # カード番号のリストを更新
        if ret[1]:
            took_photo_no = ret[0]  # 撮影した場合は撮影済みカード番号を更新
        
        # 風船番号、カード番号
        bal_no.append(next_baloon_no)
        card_no.append(ret[0])

    # 未撮影のカード撮影
    for i in range(4 - took_photo_no):
        # 未撮影の風船に移動
        acc.move(bal(took_photo_no + 1))
        # 撮影
        acc.savePic(took_photo_no + 1)
        took_photo_no = took_photo_no + 1

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
        if 1 not in bal_no:
            return 1
        elif 2 not in bal_no:
            return 2
        elif 3 not in bal_no:
            return 3
        elif 4 not in bal_no:
            return 4
        




        



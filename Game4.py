#!/usr/bin/env python
# _*_ coding: utf-8 _*_

from acctello import AccTello
from ballon import Ballon
import time
import random

# 風船の番号
# 1----2

def main():

    # アクセス用クラス
    acc = AccTello()

    # カメラ映像表示
    acc.showCamera()

    # 風船
    bal_1 = Ballon(1,50,300,270,100) # No,左右,前後,角度,高さ
    bal_2 = Ballon(2,340,100,90,100) # No,左右,前後,角度,高さ
    bal = [bal_1,bal_2]

    # メイン処理
    # 開始
    acc.startGame()

    for i in range(len(bal)) :
        #風船に移動
        acc.move(bal[i])

        # 風船のカード確認して撮影
        acc.savePic(acc.conf_card())

    # 終了
    acc.endGame()

if __name__ == "__main__":
    main()
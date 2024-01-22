#!/usr/bin/env python
# _*_ coding: utf-8 _*_

from acctello import AccTello
import time


def main():

    #アクセス用クラス
    acc = AccTello()

    #カメラ映像表示
    acc.showCamera()

    #メイン処理
    acc.startGame()
    time.sleep(20)
    
    acc.move()

    acc.endGame()

if __name__ == "__main__":
    main()


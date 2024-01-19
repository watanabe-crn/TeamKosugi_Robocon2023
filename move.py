# coding=utf-8
from djitellopy import Tello

# 定数
tello = Tello()

def movenext():

#フィールドサイズ
    XY_SIZE = 900   #フィールドの縦横のサイズ（cm）
    Z_SIZE  = 400   #フィールドの高さのサイズ（cm）

#開始位置
    
    xVal = 0   #現在位置（横）
    yVal = 0   #現在位置（縦）
    zVal = 0   #現在位置（高さ）
    aVal = 0   #現在位置（角度）

#移動先の風船のXY座標
    #左下1,1・左上1,19・右上19,19・右下19,1
    #座標0と20はフィールド外
    balloon1 = (1,1)
    balloon2 = (1,19)
    balloon3 = (19,1)
    balloon4 = (19,19)

    tello.go_xyz_speed(1, 1, 10, 20)
    tello.rotate_clockwise(90)
    tello.rotate_counter_clockwise(90)

#このスクリプトが直接実行されたときだけ処理を行う
if __name__ == '__main__':
    movenext()
    
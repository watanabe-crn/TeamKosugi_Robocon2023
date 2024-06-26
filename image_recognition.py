# coding=utf-8
from djitellopy import Tello
from os import path

import cv2
import numpy as np
import time
import threading
import queue
import datetime


def image_analysis(image):

    # 拡縮（閾値調整用）
    # 30cm:3 50cm:1 100cm:0.3
    scaling = 1

    # ノイズ除去閾値
    contourArea_min = 500*scaling
    contourArea_max = 1000*scaling

    ## 平均化するピクセル数
    #pixel_a = 30
    #pixel_b = 30

    # 色基準で2値化する。
    image = cv2.imread(image, cv2.IMREAD_GRAYSCALE)

    # 閾値の設定
    threshold = 100

    # 二値化(閾値を超えた画素を255にする。)
    ret, img_thresh = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY_INV)

    contours, hierarchy= cv2.findContours(img_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    #特定の面積以外のノイズ除去 ここの数字を適切な値にする
    cv2.drawContours(img_thresh,[i for i in contours if abs(cv2.contourArea(i))<= contourArea_min or abs(cv2.contourArea(i))> contourArea_max], -1,(0,0,0),-1)

    #デバッグ用
    cv2.imwrite('output_shapes1.png',img_thresh)

    #第一引数で輝度で平均化処理する。
    #第二引数は平均化するピクセル数で30x30ピクセル
#    img_thresh = cv2.blur(img_thresh,(pixel_a,pixel_b))

    contours, hierarchy = cv2.findContours(img_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) #輪郭抽出

    count_objects_image = len(contours)

    print("画像内のオブジェクト数：",str(count_objects_image))
#    print("画像内の円の数：",circles)

image_analysis("50cm.png")
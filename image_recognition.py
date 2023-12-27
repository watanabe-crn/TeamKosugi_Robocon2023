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
    # 色基準で2値化する。
    image = cv2.imread(image, cv2.IMREAD_GRAYSCALE)

    #デバッグ用
    cv2.imwrite('output_shapes1.png',image)

    # 閾値の設定
    threshold = 100

    # 二値化(閾値100を超えた画素を255にする。)
    ret, img_thresh = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY_INV)

    #デバッグ用 
    cv2.imwrite('output_shapes2.png',img_thresh)

    contours, hierarchy= cv2.findContours(img_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)    
    count_objects_image = len(contours)

    print("画像内のオブジェクト数：",str(count_objects_image))

image_analysis("test.jpg")
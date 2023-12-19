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
    image = cv2.imread(image)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    #デバッグ用
    cv2.imwrite('output_shapes.png',image)

    lower_color = np.array([0, 0, 0])
    upper_color = np.array([179, 128, 100])

    # 指定した色に基づいたマスク画像の生成
    mask = cv2.inRange(hsv, lower_color, upper_color)
    edges = cv2.Canny(mask,50,200)
    #デバッグ用
    cv2.imwrite('output_shapes2.png',edges)
    contours, hierarchy= cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    count_objects_image = len(contours)

    print("画像内のオブジェクト数：",str(count_objects_image))

image_analysis("test.jpg")
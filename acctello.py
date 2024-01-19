# coding=utf-8
from djitellopy import Tello

import cv2
import time
import threading
import queue
import datetime

# 定数
PIC_CNT = 3     #１回あたりの写真保存枚数
PIC_INT = 0.1   #画像保存感覚（秒）
XY_SIZE = 900   #フィールドの縦横のサイズ（cm）
Z_SIZE = 900    #フィールドの高さのサイズ（cm）

class AccTello:
    """Telloアクセス用クラス"""
    def __init__(self) :
        self.tello = Tello()
        # Telloへ接続
        self.tello.connect()
        self.motor_on = False
        # 画像転送を有効にする
        #tello.streamoff()
        self.tello.streamon()
        self.frame_read = self.tello.get_frame_read()
        self.camera_dir = Tello.CAMERA_FORWARD
        self.q_stop = queue.Queue()

        self.xVal = 0   #現在位置（横）
        self.yVal = 0   #現在位置（縦）
        self.zVal = 0   #現在位置（高さ）
        self.aVal = 0   #現在位置（角度）

        #画像転送が安定するまで少し待つ
        time.sleep(1)

    def _showCamera(self):
        #ループ（Escが押されるまでループ
        try:
            stopReq = self.q_stop.get()
            while stopReq == False:
                # 画像取得
                image = self.frame_read.frame
                # カメラ方向による回転
                small_image = cv2.resize(image, dsize=(480,360))
                if self.camera_dir == Tello.CAMERA_DOWNWARD:
                    small_image = cv2.rotate(small_image, cv2.ROTATE_90_CLOCKWISE)
                
                # ウィンドウに表示
                cv2.imshow('OpenCV Window', small_image)

                # OpenCVウィンドウでキー入力を1ms待つ
                key = cv2.waitKey(1) & 0xFF
                if key == 27:
                    break
                elif key == ord('c'):
                    if self.camera_dir == Tello.CAMERA_FORWARD:
                        self.tello.set_video_direction(Tello.CAMERA_DOWNWARD)
                        self.camera_dir = Tello.CAMERA_DOWNWARD
                    else:
                        self.tello.set_video_direction(Tello.CAMERA_FORWARD)
                        self.camera_dir = Tello.CAMERA_FORWARD
                    time.sleep(0.5)
                
                if not self.q_stop.empty():
                    stopReq = self.q_stop.get()

            cv2.destroyAllWindows()

        except(KeyboardInterrupt, SystemExit):
            print("Ctrl+Cを検知")
                        
        del self.tello.background_frame_read

    def showCamera(self):
        self.q_stop.put(False)

        vth = threading.Thread(target=self._showCamera)
        vth.setDaemon(True)
        vth.start()

    def startGame(self):
        #ゲーム開始
        self.savePic(1)   #開始時間撮影
#        self.tello.takeoff()   #離陸
        self.zVal = self.tello.get_height()    #現在位置（高さ）に高度設定
        print('高さ = {}cm'.format(self.tello.get_height()))
    
    def endGame(self):
        #ゲーム終了
#        self.tello.land()   #着陸
        self.zVal = self.tello.get_height()    #現在位置（高さ）に高度設定
        print('高さ = {}cm'.format(self.tello.get_height()))
        self.savePic(5)   #終了時間撮影

        #終了処理
        self.tello.set_video_direction(Tello.CAMERA_DOWNWARD)
        self.tello.streamoff()
        self.frame_read.stop
        self.q_stop.put(True)

    def ooesavePic(self, no):
        # 画像保存
        for i in range(PIC_CNT):
            dt = datetime.datetime.now()
            fn = '{}_{}{}{}{}.png'.format(no,dt.hour,dt.minute,dt.second,dt.microsecond)
            cv2.imwrite(fn, self.frame_read.frame) #画像保存
            time.sleep(PIC_INT) #指定秒数待機



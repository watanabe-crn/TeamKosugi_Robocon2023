# coding=utf-8
from djitellopy import Tello

import cv2
import time
import threading
import queue
import datetime

import move
from ballon import Ballon

# 定数
PIC_CNT = 3     #１回あたりの写真保存枚数
PIC_INT = 0.1   #画像保存感覚（秒）
XY_SIZE = 900   #フィールドの縦横のサイズ（cm）
Z_SIZE = 900    #フィールドの高さのサイズ（cm）
speed = 1   # 移動スピード指定（s/cm）
zahyo_cm = 50   # 座標一マスあたりの距離(cm)

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
        self.zahyo = [self.xVal, self.yVal, self.zVal, self.aVal]    #現在位置（xyz座標）と角度

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
        #self.tello.takeoff()   #離陸
        self.xVal=10
        self.yVal=10
        self.zVal = self.tello.get_height()    #現在位置（高さ）に高度設定
        print('高さ = {}cm'.format(self.tello.get_height()))
        self.aVal=0

    def startMove(self,bal):
        # 移動先座標[x,y]・角度を取得し、変数にセット
        next_zahyo = Ballon.get_inner_position(bal)
        self.next_aVal = Ballon.get_r(bal)
        self.setNextZahyo(next_zahyo)
        # 移動距離計算
        distance = self.calcDistance()
        # 風船の内側へ移動
        #self.tello.go_xyz_speed(distance[0],distance[1],0,100)
        # 現在地として座標を設定
        self.setCurrentZahyo(next_zahyo)
        # 風船の外側へ移動
        #next_zahyo = Ballon.get_take_photo_position(bal)
        self.setNextZahyo(next_zahyo)
        distance = self.calcDistance()
        #self.tello.go_xyz_speed(distance[0],distance[1],0,50)
        self.setCurrentZahyo(next_zahyo)
        # 高さ設定
        # if self.zVal < 80:
        #     self.tello.move_up(100 - self.zVal)
        # elif self.zVal > 110:
        #     self.tello.move_down(self.zVal - 90)
        self.zVal = self.tello.get_height()    #現在位置（高さ）に高度設定

        # 風船に向かい回転
        #self.rotate(self)
        # 風船の高さ調査
        # for i in range (10):
        #     self.tello.move_up(20)
        

    def move(self,bal):
        # 高さを取得値か最低か最高に設定
        if self.next_zVal != 0:
            self.tello.go_xyz_speed(0,0, self.zVal-self.next_zVal, 30)
        elif self.zVal > 250:
            if self.zVal < 400:
                self.tello.move_up(400 - self.zVal)
            else:
                self.tello.move_down(self.zVal - 400)
        else:
            if self.zVal < 100:
                self.tello.move_up(100 - self.zVal)
            else:
                self.tello.move_down(self.zVal - 100)
        self.zVal = self.tello.get_height()    #現在位置（高さ）に高度設定
        # 正面へ回転
        if self.next_aVal < 180:
            self.tello.rotate_counter_clockwise(self.next_aVal)
        else:
            self.tello.rotate_clockwise(360 - self.next_aVal)
        self.aVal = self.next_aVal  # 現在位置（角度）を設定
        # 撮影位置へ移動
        # 移動先座標[x,y]・角度を取得し、変数にセット
        next_zahyo = Ballon(bal).get_take_photo_position
        self.next_aVal = Ballon(bal).get_r
        self.setNextZahyo(next_zahyo)
        # 隣り合う風船の場合、撮影場所へ移動
        if self.xVal == self.next_xVal:
            distance = self.calcDistance(self)
            self.tello.go_xyz_speed(distance[0],distance[1],0,100)
            self.setCurrentZahyo(next_zahyo)
        elif self.yVal == self.next_yVal:
            distance = self.calcDistance(self)
            self.tello.go_xyz_speed(distance[0],distance[1],0,100)
            self.setCurrentZahyo(next_zahyo)
        # 体格の風船の場合、以下の順に移動
        # ①風船の内側
        # ②撮影位置
        else:
            next_zahyo = Ballon(bal).get_inner_position
            self.setNextZahyo(next_zahyo)
            distance = self.calcDistance(self)
            # 風船の内側へ移動
            self.tello.go_xyz_speed(distance[0],distance[1],0,100)
            # 現在地として座標を設定
            self.setCurrentZahyo(next_zahyo)
            # 風船の外側へ移動
            next_zahyo = Ballon(bal).get_take_photo_position
            self.setNextZahyo(next_zahyo)
            distance = self.calcDistance(self)
            self.tello.go_xyz_speed(distance[0],distance[1],0,50)
            self.setCurrentZahyo(next_zahyo)
        # 風船へ向く
        self.rotate(self)
        
        # 風船の高さ調査
        if self.next_zVal == 0:
            # for i in range (10):
            #     if self.zVal < 250:
            #       self.tello.move_up(20)
            #     else:
            #       self.tello.move_down(20)
            print
                   
    def setCurrentZahyo(self,zahyo):
        # リストで受け取った移動先座標の値をそれぞれ変数に代入します
        self.xVal = zahyo[0]
        self.yVal = zahyo[1]
        self.zahyo = [self.xVal, self.yVal, self.zVal, self.aVal]    #現在位置（xyz座標）と角度

        # dst_a = Ballon(bal).get_r

    def setNextZahyo(self,zahyo):
        # リストで受け取った移動先座標の値をそれぞれ変数に代入します
        self.next_xVal = zahyo[0]
        self.next_yVal = zahyo[1]
        # dst_a = Ballon(bal).get_r
    
    def calcDistance(self):
        # x（縦軸）とy（横軸）の移動距離を返却
        x = zahyo_cm * (self.next_yVal - self.yVal)
        y = zahyo_cm * (self.next_xVal - self.xVal)
        ret = [x,y]
        return ret

    def rotate(self):
        # 風船に向かい回転
        if self.next_aVal < 180:
            self.tello.rotate_clockwise(self.next_aVal)
        else:
            self.tello.rotate_counter_clockwise(360 - self.next_aVal)
        self.aVal = self.next_aVal  # 現在位置（角度）を設定

    
    def conf_card(self, bal, took_photo_no):
        # カードを解析して番号を取得

        # カード番号が撮影済みカード番号の次の番号だったら撮影
    
        # リターン（カード番号、撮影済（Bool）
        ret = (1, True)
        return ret

    def endGame(self):
        # ゲーム終了
        # 正面へ回転
        self.tello.rotate_clockwise(10)

        # 開始位置に移動
        distance=self.calcDistance
        self.tello.go_xyz_speed(distance[0],distance[1],0,50)
        
#        self.tello.land()   #着陸
        self.zVal = self.tello.get_height()    #現在位置（高さ）に高度設定
        print('高さ = {}cm'.format(self.tello.get_height()))
        self.savePic(6)   #終了時間撮影

        #終了処理
        self.tello.set_video_direction(Tello.CAMERA_DOWNWARD)
        self.tello.streamoff()
        self.frame_read.stop
        self.q_stop.put(True)

    def savePic(self, no):
        # 画像保存
        for i in range(PIC_CNT):
            dt = datetime.datetime.now()
            fn = '{}_{}{}{}{}.png'.format(no,dt.hour,dt.minute,dt.second,dt.microsecond)
            cv2.imwrite(fn, self.frame_read.frame) #画像保存
            time.sleep(PIC_INT) #指定秒数待機



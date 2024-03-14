# coding=utf-8
from djitellopy import Tello

import cv2
import time
import threading
import queue
import datetime


from ballon import Ballon

# 定数
PIC_CNT = 3     #１回あたりの写真保存枚数
PIC_INT = 0.1   #画像保存感覚（秒）
XY_SIZE = 900   #フィールドの縦横のサイズ（cm）
Z_SIZE = 900    #フィールドの高さのサイズ（cm）
speed = 100   # 移動スピード指定（s/cm） # 100がgo_xyz_speedコマンドのMax値
zahyo_cm = 10   # 座標一マスあたりの距離(cm)

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

        self.xVal = 10   #現在位置（横）
        self.yVal = 10   #現在位置（縦）
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

    def move(self,bal):
        # 高さを取得値か最低か最高に設定
        # 一つ目の風船の場合、最も低い位置へ移動
        if self.xVal == 10:
            if self.zVal < 80:
                self.tello.move_up(100 - self.zVal)
            elif self.zVal > 110:
                self.tello.move_down(self.zVal - 90)
            if self.next_zVal != 0:
                self.tello.go_xyz_speed(0,0, self.zVal-self.next_zVal, speed * 0.5)
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
        self.rotateFront()
        # 撮影位置へ移動
        # 移動先座標[x,y]・角度を取得し、変数にセット
        next_zahyo = Ballon.get_take_photo_position(bal)
        next_aVal = Ballon.get_r(bal)
        self.setNextZahyo(next_zahyo)
        # 隣り合う風船の場合、撮影場所へ移動
        if self.xVal == self.next_xVal or self.yVal == self.next_yVal:
            distance = self.calcDistance(self)
            self.tello.go_xyz_speed(distance[0],distance[1],0,speed)
            self.setCurrentZahyo(next_zahyo)
        # 対角の風船の場合、以下の順に移動
        # ①自風船の内側
        # ②次の風船の内側
        # ③撮影位置
        
        else:
            #1つ目の風船ではない場合
            if self.xVal != 10:
                # 自風船の内側へ移動
                #?#どうやって自風船の内側を求めるか
                next_zahyo = Ballon(bal).get_take_photo_position
                self.setNextZahyo(next_zahyo)
                distance = self.calcDistance(self)
                #?# カーブの経路を指定しなければいけないが、4パターン分岐がある
                self.tello.curve_xyz_speed(distance[0],distance[1],0,speed * 0.5)
                self.setCurrentZahyo(next_zahyo)
            # 次の風船の内側へ移動
            next_zahyo = Ballon(bal).get_inner_position
            next_aVal = Ballon.get_r(bal)
            self.setNextZahyo(next_zahyo)
            distance = self.calcDistance(self)
            self.tello.go_xyz_speed(distance[0],distance[1],0,speed)
            # 現在地として座標を設定
            self.setCurrentZahyo(next_zahyo)
            # 次の風船の外側へ移動
            next_zahyo = Ballon(bal).get_take_photo_position
            self.setNextZahyo(next_zahyo)
            distance = self.calcDistance(self)
            #?# カーブの経路を指定しなければいけないが、4パターン分岐がある
            self.tello.curve_xyz_speed(distance[0],distance[1],0,speed * 0.5)
            self.setCurrentZahyo(next_zahyo)
        # 風船へ向く
        self.rotate(next_aVal)
        
        # 風船の高さ調査
        if self.next_zVal == 0:
            # for i in range (10):
            #     if self.zVal < 250:
            #       self.tello.move_up(20)
            #     else:
            #       self.tello.move_down(20)
            print

         # 風船の高さが不明の場合は高さを確認
        image = self.frame_read.frame
        dot_count = self.image_analysis(image)
        if self.zVal >= 90 and self.zVal <= 110:
            while dot_count >=1 and dot_count <= 4:
                self.zVal = Tello.get_height()
                Ballon.set_z(self.zVal)
            else:
                Tello.move_up(30)
                image = self.frame_read.frame
                dot_count = self.image_analysis(image)
        elif self.zVal >= 390 and self.zVal <= 410 :
            while dot_count >=1 and dot_count <= 4:
                self.zVal = Tello.get_height()
                Ballon.set_z(self.zVal)
            else:
                Tello.move_down(30)
                image = self.frame_read.frame
                dot_count = self.image_analysis(image)

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

    def rotate(self, next_aVal):
        # 風船に向かい回転
        if next_aVal < 180:
            self.tello.rotate_clockwise(next_aVal)
        else:
            self.tello.rotate_counter_clockwise(360 - next_aVal)
        self.aVal = next_aVal  # 現在の角度を設定
    
    def rotateFront(self):
        # 正面に向かい回転
        if self.aVal < 180:
            self.tello.rotate_counter_clockwise(self.aVal)
        else:
            self.tello.rotate_clockwise(360 - self.aVal)
        self.aVal = 0 # 現在位置（角度）を設定
    def conf_card(self, bal, took_photo_no):
        # カードを解析して番号を取得
        image = self.frame_read.frame
        count = self.image_analysis(image)
        # カード番号が撮影済みカード番号の次の番号だったら撮影
        if count == took_photo_no + 1:
            self.savePic
            # リターン（カード番号、撮影済（Bool）
            ret = (count, True)
        else:
            ret = (count, False)
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

    def image_analysis(image):
        # 色基準で2値化する。
        image = cv2.imread(image, cv2.IMREAD_GRAYSCALE)

        # 閾値の設定
        threshold = 100

        # 二値化(閾値を超えた画素を255にする。)
        ret, img_thresh = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY_INV)

        contours, hierarchy= cv2.findContours(img_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        #特定の面積以外のノイズ除去 ここの数字を適切な値にする
        cv2.drawContours(img_thresh,[i for i in contours if abs(cv2.contourArea(i))<= 750 or abs(cv2.contourArea(i))> 1500], -1,(0,0,0),-1)

        #デバッグ用
        #cv2.imwrite('output_shapes1.png',img_thresh)

        #第一引数で輝度で平均化処理する。
        #第二引数は平均化するピクセル数で30x30ピクセル
        img_thresh = cv2.blur(img_thresh,(30,30))

        contours, hierarchy = cv2.findContours(img_thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) #輪郭抽出

        count_objects_image = len(contours)

        return count_objects_image
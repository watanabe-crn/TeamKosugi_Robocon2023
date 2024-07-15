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
XY_SIZE = 384   #フィールドの縦横のサイズ（cm）
Z_SIZE = 500    #フィールドの高さのサイズ（cm）
speed = 50   # 移動スピード指定（s/cm） # 100がgo_xyz_speedコマンドのMax値
zahyo_cm = int(1)   # 座標一マスあたりの距離(cm)

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

        # ドローンのスタート位置を現在位置として設定
        self.xVal = 197   #現在位置（横）
        self.yVal = 250   #現在位置（縦）
        self.zVal = 0   #現在位置（高さ）
        self.aVal = 0   #現在位置（角度）
        
        # スタート位置を保持
        # （高さ z は不要）
        self.start_position = [self.xVal, self.yVal, self.aVal]    #現在位置（xy座標）と角度

        print('スタート位置をドローンインスタンスに保持します。')
        print('[x, y, r] ：' + str(self.start_position))

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
        #self.savePic(1)   #開始時間撮影
        self.tello.takeoff()   #離陸
        self.zVal = self.tello.get_height()    #現在位置（高さ）に高度設定
        print('高さ = {}cm'.format(self.tello.get_height()))

    def move(self,bal):
        
### テスト用
        # self.start_position = [self.xVal, self.yVal, self.aVal]    #現在位置（xyz座標）と角度
### テスト用
#        
    ## 初期値設定
        if type(bal) is Ballon:
        # パラメータの型がBallonクラスの場合
        # 受け取った風船情報の取得
            self.bal_zahyo = bal.get_position()
            self.bal_xVal = self.bal_zahyo[0]
            self.bal_yVal = self.bal_zahyo[1]
            self.bal_zVal = self.bal_zahyo[2]
            self.bal_rVal = bal.get_r()

            print('Balloonの位置を取得します。')
            print('x ： ' + str(self.bal_xVal))
            print('y ： ' + str(self.bal_yVal))
            print('r ： ' + str(self.bal_rVal))
            print('z ： ' + str(self.bal_zVal))

        else:
        # パラメータの型がBallonクラス以外の場合
        # スタート位置を目標地としてセット
            self.bal_xVal = self.start_position[0]
            self.bal_yVal = self.start_position[1]
            self.bal_zVal = self.zVal               # 高さは現在の高さをセット（高さ調節なし）
            self.bal_rVal = self.start_position[2]

            print('スタート位置を取得します')
            print('x ： ' + str(self.bal_xVal))
            print('y ： ' + str(self.bal_yVal))
            print('r ： ' + str(self.bal_rVal))
            print('z ： ' + str(self.bal_zVal))
    
    ## 移動開始
    
        # return
    
        ## ドローンの向きが正面じゃない場合は旋回
        if not self.aVal == 0:
            self.rotateFront()
            print('正面を向きます')
        
        ## 高さ調節
        # 高さの移動量を決定
        self.z_distance = self.bal_zVal - self.zVal
        print('高さ移動量 ：' + str(self.z_distance))
        

        # 高さ移動
        if self.z_distance > 20 or self.z_distance < -20:   # 移動距離が20cm以下の場合のコマンドエラー回避
            if self.z_distance > 0:
                self.tello.move_up(self.z_distance)
            else:
                self.tello.move_down(- self.z_distance) # 負の数の場合、正の数に反転して降下
        
        # 現在位置（高さ）に高度設定
        self.zVal = self.tello.get_height()

## テスト用
        #         print('20cm以上の差があるので高さ移動します。')
        # self.zVal = self.bal_zVal
        # print('高さを風船の高さに合わせます')
        # print('高さ = {}cm'.format(self.zVal))      
## テスト用

        print('高さを風船の高さに合わせます')
        print('高さ = {}cm'.format(self.tello.get_height()))

        ## 座標移動
        # 縦横の移動量を決定
        xy_distance = self.calcDistance()   # x（縦軸）, y（横軸）の移動距離をリストで取得
        
        # 縦横へ移動。実際には旋回せずに目的地へ直進して移動する
        self.tello.go_xyz_speed(xy_distance[0], xy_distance[1], 0, speed)

        print('xy方向に移動します')
        print('移動量 前に, 左に ：' + str(xy_distance[0]) + ',' + str(xy_distance[1]))
        print('速度　：' + str(speed))
        
        ## 現在位置にx, yを設定
        self.xVal = self.bal_xVal
        self.yVal = self.bal_yVal

        print('現在の座標 x, y ：' + str(self.xVal) + ',' + str(self.yVal))
        
        ## 角度調節
        # 旋回
        self.rotate(self.bal_rVal)
        
## テスト用
        self.aVal = self.bal_rVal
## テスト用
        print('風船へ旋回します')
        print('r ：' + str(self.aVal))

        print('moveメソッド終了')
        return
    
    def calcDistance(self):
        # x（縦軸）とy（横軸）の移動距離を返却
        x = zahyo_cm * (self.bal_yVal - self.yVal)
        y = zahyo_cm * (self.bal_xVal - self.xVal)
        ret = [x,-y]
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

    def conf_card(self):
        # カードを解析して番号を取得
        cv2.imwrite('tmp.png', self.frame_read.frame) #画像保存
        count = self.image_analysis('tmp.png')
        ret = count

    def endGame(self):
        # ゲーム終了
        self.move(None) # 開始位置に移動
        self.tello.land()   # 着陸

        self.zVal = self.tello.get_height()    # 現在位置（高さ）に高度設定
        print('高さ = {}cm'.format(self.tello.get_height()))
        #self.savePic(6)   # 終了時間撮影

        # 終了処理
        self.tello.set_video_direction(Tello.CAMERA_DOWNWARD)
        self.tello.streamoff()
        self.frame_read.stop
        self.q_stop.put(True)

    def savePic(self, no):
        # 画像保存
        for i in range(PIC_CNT):
            dt = datetime.datetime.now()
            fn = '{}_{}{}{}{}_{}.png'.format(no,dt.hour,dt.minute,dt.second,dt.microsecond,no)
            cv2.imwrite(fn, self.frame_read.frame) #画像保存
            time.sleep(PIC_INT) #指定秒数待機


    def image_analysis(self, image):
        # 拡縮（閾値調整用）
        # 30cm:3 50cm:1 100cm:0.3(距離によってscalingの数字を調整)
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

        return count_objects_image

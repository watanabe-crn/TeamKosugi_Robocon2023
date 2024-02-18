# coding=utf-8
from djitellopy import Tello

import cv2
import time
import threading
import queue
import datetime

import move

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
#        self.tello.takeoff()   #離陸
        self.zVal = self.tello.get_height()    #現在位置（高さ）に高度設定
        print('高さ = {}cm'.format(self.tello.get_height()))

    def move(self,bal):
        # 現在地(座標)
        print('現在の座標と角度です' + str(self.zahyo))
        # 目的の座標
        next_zahyo = [11,11,8,0]
        # 移動先を指定し、新たな座標を取得します
        # 第一引数：移動先座標　 第二引数：現在の座標
        new_zahyo = move.movenext(next_zahyo, self.zahyo)

        print('新しい座標と角度です' + str(new_zahyo))

        # 移動後の現在地（座標）を求めます
        self.zahyo = new_zahyo
        print('現在の座標と角度を更新しました' + str(self.zahyo))

        # 風船の高さが不明の場合は高さを確認

        # 高さを確認したら高さを風船クラスに設定

    
    def conf_card(self, bal, took_photo_no):
        # カードを解析して番号を取得

        # カード番号が撮影済みカード番号の次の番号だったら撮影
    
        # リターン（カード番号、撮影済（Bool）
        ret = (1, True)
        return ret

    def endGame(self):
        # ゲーム終了
        # 開始位置に移動
        
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



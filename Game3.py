#!/usr/bin/env python
# _*_ coding: utf-8 _*_

from djitellopy import Tello
import time
import random

# 定数（テスト用）
# FIRST_LIMIT_TIME = 120.0 - 30.0   # 自由に動ける時間（期限）
# SECOND_LIMIT_TIME = 180.0 - 30.0  # 上下のみ移動できる時間（期限）
# START_Z_POS = 100                 # 最初の高さ
# FIRST_XY_MIN = 0                  # 最初の移動下限
# FIRST_XY_MAX = 0                  # 最初の移動上限
# XY_MIN = 5                        # 平面移動下限
# XY_MAX = 10                       # 平面移動上限
# Z_MIN = 3                         # 上下移動下限
# Z_MAX = 6                         # 上下移動上限

# 定数（本番用）
FIRST_LIMIT_TIME = 300.0 - 30.0     # 自由に動ける時間（期限）
SECOND_LIMIT_TIME = 480.0 - 30.0    # 上下のみ移動できる時間（期限）
START_Z_POS = 200                   # 最初の高さ
FIRST_XY_MIN = 35                   # 最初の移動下限
FIRST_XY_MAX = 55                   # 最初の移動上限
XY_MIN = 5                          # 平面移動下限
XY_MAX = 30                         # 平面移動上限
Z_MIN = 3                           # 上下移動下限
Z_MAX = 12                          # 上下移動上限


def main():
    tello = Tello()

    tello.connect()
    start_time = time.time()
    time.sleep(1)
    tello.takeoff()

    # 中心部に移動
    x_move = random.randint(FIRST_XY_MIN,FIRST_XY_MAX) * 10
    y_move = random.randint(FIRST_XY_MIN,FIRST_XY_MAX) * 10
    z_move = START_Z_POS - tello.get_height()
    move_speed = random.randint(30,80)
    tello.go_xyz_speed(x_move, y_move, z_move, move_speed)

    current_time = time.time()
    pre_time = time.time() # 10秒監視用

    try:
        while True:
            x_move = random.randint(XY_MIN, XY_MAX) * 10
            y_move = random.randint(XY_MIN, XY_MAX) * 10
            z_move = random.randint(Z_MIN, Z_MAX) * 10

            if current_time - start_time < FIRST_LIMIT_TIME:
                print(current_time)
                print(current_time - start_time)
                # 自由に動ける
                # 平行移動１
                move_speed = random.randint(30,80)
                tello.go_xyz_speed(x_move, y_move, 0, move_speed)
                # 待機
                time.sleep(move_speed * 0.04)
                # 上下移動１
                tello.move_up(z_move)
                # 待機
                time.sleep(move_speed * 0.04)

                # 平行移動２
                move_speed = random.randint(30,80)
                tello.go_xyz_speed(x_move * -2, y_move * -2, 0, move_speed)
                # 待機
                time.sleep(move_speed * 0.04)
                # 上下移動２
                tello.move_down(z_move * 2)
                # 待機
                time.sleep(move_speed * 0.04)

                # 平行移動３
                move_speed = random.randint(30,80)
                tello.go_xyz_speed(x_move, y_move, 0, move_speed)
                # 待機
                time.sleep(move_speed * 0.04)
                # 上下移動３
                tello.move_up(z_move)
                # 待機
                time.sleep(move_speed * 0.04)

            elif current_time - start_time < SECOND_LIMIT_TIME:
                print('上下のみ')
                print(current_time)
                print(current_time - start_time)
                # 上下のみ動ける
                move_speed = random.randint(30,80)
                z_move = random.randint(Z_MIN, Z_MAX) * 10

                # 上下移動１
                tello.move_up(z_move)
                # 待機
                time.sleep(move_speed * 0.04)

                # 上下移動２
                tello.move_down(z_move * 2)
                # 待機
                time.sleep(move_speed * 0.04)

                # 上下移動３
                # tello.move_up(z_move)
                # 待機
                time.sleep(move_speed * 0.04)

            elif current_time - pre_time > 10.0:
                print('接続維持')
                # 動けない（10秒ごとにドローンとの接続維持）
                tello.send_command_without_return('command')
                pre_time = time.time()

            current_time = time.time()

    except(KeyboardInterrupt, SystemExit):
        tello.land
        print('終了')

if __name__ == "__main__":
    main()

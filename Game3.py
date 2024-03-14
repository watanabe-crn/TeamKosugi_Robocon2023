#!/usr/bin/env python
# _*_ coding: utf-8 _*_

from djitellopy import Tello
import time
import random

# 定数
FIRST_LIMIT_TIME = 120 - 30     # 自由に動ける時間（期限）
SECOND_LIMIT_TIME = 180 - 30    # 上下のみ移動できる時間（期限）
START_Z_POS = 100               # 最初の高さ
FIRST_XY_MIN = 10               # 最初の移動下限
FIRST_XY_MAX = 20               # 最初の移動上限
XY_MIN = 5                      # 平面移動下限
XY_MAX = 10                     # 平面移動上限
Z_MIN = 3                       # 上下移動下限
Z_MAX = 6                      # 上下移動上限


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
    move_speed = random.randint(4,8)
    tello.go_xyz_speed(x_move, y_move, z_move, move_speed)

    # 決められた時間まで自由に動ける
    current_time = time.time()
    while current_time - start_time < FIRST_LIMIT_TIME:
        x_move = random.randint(XY_MIN, XY_MAX) * 10
        y_move = random.randint(XY_MIN, XY_MAX) * 10
        z_move = random.randint(Z_MIN, Z_MAX) * 10

        # 平行移動１
        move_speed = random.randint(4,8)
        tello.go_xyz_speed(x_move, y_move, 0, move_speed)
        # 待機
        time.sleep(move_speed * 0.2)
        # 上下移動１
        tello.move_up(z_move)
        # 待機
        time.sleep(move_speed * 0.2)

        # 平行移動２
        move_speed = random.randint(4,8)
        tello.go_xyz_speed(x_move * -2, y_move * -2, 0, move_speed)
        # 待機
        time.sleep(move_speed * 0.2)
        # 上下移動２
        tello.move_down(z_move * -2)
        # 待機
        time.sleep(move_speed * 0.2)

        # 平行移動３
        move_speed = random.randint(4,8)
        tello.go_xyz_speed(x_move, y_move, 0, move_speed)
        # 待機
        time.sleep(move_speed * 0.2)
        # 上下移動３
        tello.move_up(z_move)
        # 待機
        time.sleep(move_speed * 0.2)

        current_time = time.time()

    while current_time - start_time < SECOND_LIMIT_TIME:
        z_move = random.randint(Z_MIN, Z_MAX) * 10
        move_speed = random.randint(4,8)

        # 上下移動１
        tello.move_up(z_move)
        # 待機
        time.sleep(move_speed * 0.2)

        # 上下移動２
        tello.move_down(z_move * -2)
        # 待機
        time.sleep(move_speed * 0.2)

        # 上下移動３
        tello.move_up(z_move)
        # 待機
        time.sleep(move_speed * 0.2)

        current_time = time.time()

if __name__ == "__main__":
    main()

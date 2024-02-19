# coding=utf-8
from djitellopy import Tello

# 定数
tello = Tello()

def movenext(next_zahyo_list, current_zahyo_list):
    print('movenextメソッドを開始します。')
    print('呼び出し元から渡された移動先座標：' + str(next_zahyo_list))
    # リストで受け取った移動先座標の値をそれぞれ変数に代入します
    dst_x = next_zahyo_list[0]
    dst_y = next_zahyo_list[1]
    dst_z = next_zahyo_list[2]
    dst_a = next_zahyo_list[3]

    # リストで受け取った現在の座標の値をそれぞれ変数に代入します
    crt_x = current_zahyo_list[0]
    crt_y = current_zahyo_list[1]
    crt_z = current_zahyo_list[2]
    crt_a = current_zahyo_list[3]
    # 移動スピード指定（s/cm）
    speed = 20
    # 座標一マスあたりの距離(cm)
    zahyo_cm = 50

    #現在の座標と目的の座標を比べ、移動距離を計算します
    x_cm = zahyo_cm * (dst_x - crt_x)
    y_cm = zahyo_cm * (dst_y - crt_y)
    z_cm = zahyo_cm * (dst_z - crt_z)
    
    print('移動先までの距離(cm)と角度：' + str(x_cm) + ',' + str(y_cm) + ',' + str(z_cm) + ',' + str(dst_a) )
    print('移動開始')
    tello.go_xyz_speed(x_cm, y_cm, z_cm, speed)
    print('移動終了')

    new_zahyo = [dst_x, dst_y, dst_z, dst_a]

    return new_zahyo
  
# if __name__ == '__main__':  

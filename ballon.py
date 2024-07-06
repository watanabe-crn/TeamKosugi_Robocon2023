# coding=utf-8

class Ballon:
    """Telloアクセス用クラス"""
    def __init__(self,bal_no,x,y,r,z) :
        self.pos_x = x   # 風船のX座標
        self.pos_y = y   # 風船のY座標
        self.pos_z = z   # 風船の高さ（Z座標）
        self.pos_r = r   # 風船を撮影する時の角度
        self.card_no = 0    # カードの番号
    
    def get_position(self):
        # 風船の座標
        ret = [self.pos_x,self.pos_y,self.pos_z]
        return ret
    
    def get_card_no(self):
        return self.card_no
    
    def set_z(self,z):
        self.pos_z = z
    
    def get_z(self):
        return self.pos_z
    
    def get_r(self):
        return self.pos_r
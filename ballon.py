# coding=utf-8

class Ballon:
    """Telloアクセス用クラス"""
    def __init__(self,bal_no,x,y) :
        self.pos_x = x   # 風船のX座標
        self.pos_y = y   # 風船のY座標
        self.pos_z = 0   # 風船の高さ（Z座標）
        self.card_no = 0    # カードの番号
    
    def get_position(self):
        # 風船の座標
        ret = [self.pos_x,self.pos_y,self.pos_z]
        return ret
    
    def get_take_photo_position(self):
        # 風船の外側の座標
        if self.pos_x < 0:
            x = self.pos_x - 1
        else:
            x = self.pos_x + 1
        
        if self.pos_yx < 0:
            y = self.pos_y - 1
        else:
            y = self.pos_y + 1
        ret = [x,y]
        return ret
    
    def get_card_no(self):
        return self.card_no
    
    def set_z(self,z):
        self.pos_z = z
    





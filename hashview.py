import hashlib

from kivy.graphics import Rectangle, Color
from kivy.uix.relativelayout import RelativeLayout


def byteArrayToBitArray(b):
    x = [0 for _ in range(len(b)*8)]
    for j in range(len(b)):
        for i in range(8):
            x[j * 8 + i] = 1 if (b[j] & (1 << i)) > 0 else 0
    return x


def getBitSeqFromBooleanArray(bit_index, bit_length, bb):
    a = 0
    m = 1
    i = bit_index + bit_length - 1
    while i >= bit_index:
        a += m if bb[i] else 0
        m <<= 1
        i -= 1
    return a

class HashView(RelativeLayout):

    colors16_ordered = [Color(c.r/255.0, c.g/255.0, c.b/255.0) for c in
                        [Color(0, 0, 0), Color(255, 0, 0), Color(0, 255, 0), Color(0, 0, 255),
                         Color(255, 255, 255), Color(255, 255, 0), Color(0, 255, 255), Color(255, 0, 255),
                         Color(0x7F, 0, 0), Color(0, 0x7F, 0x7F), Color(0, 0x7F, 0), Color(0x7F, 0x7F, 0),
                         Color(0x7F, 0x44, 0), Color(0x7F, 0, 0x6E), Color(0xFF, 0x88, 0), Color(0x7F, 0x7F, 0x7F)]]

    def __init__(self,data,gridSize,bitsPerCell,width,height):
        super(HashView, self).__init__(size=(width,height), pos_hint= {'center_x': .5, 'center_y': .5})

        self.data = data
        self.gridSize = gridSize
        self.bitsPerCell = bitsPerCell

        self.width_ = self.size[0]
        self.height_ = self.size[1]

        self.rSize = min(self.width_, self.height_) // self.gridSize
        self.outSize = self.gridSize * self.gridSize * self.bitsPerCell

        with self.canvas:
            if self.data is not None:
                h = hashlib.shake_128()
                h.update(self.data)
                outDigest = bytearray(h.digest(self.outSize // 8))
                bb = byteArrayToBitArray(outDigest)

                for i_ in range(self.gridSize):
                    for j_ in range(self.gridSize):
                        rColor = getBitSeqFromBooleanArray(self.bitsPerCell * (self.gridSize * i_ + j_),
                                                           self.bitsPerCell,
                                                           bb)
                        col = HashView.colors16_ordered[rColor]
                        Color(col.r, col.g, col.b)
                        Rectangle(size=(self.rSize, self.rSize), pos=(i_ * self.rSize, (self.gridSize - j_) * self.rSize))

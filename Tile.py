from panda3d.core import LPoint3, BitMask32


class Tile(object):
    def __init__(self, position, color, index, board, row, column):
        self.position = position
        self.color = color
        self.board = board
        self.row = row
        self.column = column
        self.index = index
        self.square = loader.loadModel("models/square")
        self.square.reparentTo(board.mother_root)
        self.square.setPos(self.tile_position(position))
        self.square.setColor(color)
        self.square.find("**/polygon").node().setIntoCollideMask(BitMask32.bit(1))
        self.square.find("**/polygon").node().setTag('object', str(index))

    def tile_position(self, position):
        offset_z = (self.board.level * 2) - 2
        offset_y = (position[1]) - 1
        offset_x = (position[2]) - 1
        return LPoint3(offset_x, offset_y, offset_z)

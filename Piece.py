from panda3d.core import LPoint3


class Piece(object):
    def __init__(self, position, color, beginning_board, model):
        self.beginning_board = beginning_board
        self.position = position
        self.color = color
        self.piece = loader.loadModel(model)
        self.piece.reparentTo(render)
        self.piece.setColor(color)
        self.piece.setPos(self.tile_position(position))
        self.square = None
        self.is_captured = False
        if color == (0.4, 0.2, 0.0, 1):
            self.piece.setH(self.piece, 180)

    def tile_position(self, position):
        offset_z = (self.beginning_board.level * 2) - 2
        offset_y = (position[1]) - 1
        offset_x = (position[2]) - 1
        return LPoint3(offset_x, offset_y, offset_z)

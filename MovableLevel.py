from Board import Board
from panda3d.core import LPoint3, BitMask32


class MovableLevel(Board):
    def __init__(self, is_left, number, level):
        self.number = number
        self.level = level
        self.is_left = is_left
        self.rows = 2
        self.columns = 2
        pin_index = 0
        if level == 3:
            self.first_row = 1
            pin_index += 2
        if level == 7:
            self.first_row = 9
            pin_index += 9
        if is_left:
            self.first_column = 1
        else:
            pin_index += 2
            self.first_column = 5
        self.tiles = [None for i in range(4)]
        self.stick = None
        self.current_pin = pin_index - 1

    def stick_position(self):
        offset_z = self.level * 2 - 3.0
        offset_y = self.first_row - 0.5
        offset_x = self.first_column - 0.5
        return LPoint3(offset_x, offset_y, offset_z)

    def draw_stick(self):
        self.stick = loader.loadModel("models/cube.egg")
        self.stick.reparentTo(self.mother_root)
        self.stick.setPos(self.stick_position())
        self.stick.setColor(0.85, 0.75, 0.5, 1)
        self.stick.setScale(0.1, 0.1, 1.0)
        self.stick.find("**/cube").node().setIntoCollideMask(BitMask32.bit(1))
        self.stick.find("**/cube").node().setTag('object', str(497 + self.number))
        return self.stick

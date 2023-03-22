from panda3d.core import LPoint3, BitMask32


class Board(object):
    def __init__(self, level, number, first_row, first_column):
        self.number = number
        self.level = level
        self.rows = 4
        self.columns = 4
        self.first_row = first_row
        self.first_column = first_column
        self.tiles = [None for i in range(16)]
        self.mother_root = None
        self.adjacent_pins = [None for i in range(4)]
        self.stick = None

    # 0 - front left, 1 - back left, 2 - front right, 3 - back right
    def adjacent_pin_position(self, index):
        rows_to_end = columns_to_end = 0
        if index % 2 == 0:
            rows_to_end = 4
        if index > 1:
            columns_to_end = 4
        offset_z = self.level * 2 - 2
        offset_y = self.first_row + rows_to_end - 1.5
        offset_x = self.first_column + columns_to_end - 1.5
        return LPoint3(offset_x, offset_y, offset_z)

    def draw_adjacent_pins(self, index):
        for i in range(4):
            self.adjacent_pins[i] = loader.loadModel("models/cube.egg")
            self.adjacent_pins[i].reparentTo(self.mother_root)
            self.adjacent_pins[i].setPos(self.adjacent_pin_position(i))
            self.adjacent_pins[i].setColor(0.85, 0.75, 0.5, 1)
            self.adjacent_pins[i].setScale(0.1, 0.1, 0.1)
            self.adjacent_pins[i].find("**/cube").node().setIntoCollideMask(BitMask32.bit(1))
            self.adjacent_pins[i].find("**/cube").node().setTag('object', str(1000 + index + i))

    def stick_position(self):
        offset_z = self.level * 2 - 4.02 - self.number * 2
        offset_y = self.first_row + 1.5
        offset_x = self.first_column + 0.5
        return LPoint3(offset_x, offset_y, offset_z)

    def draw_stick(self):
        self.stick = loader.loadModel("models/cube.egg")
        self.stick.reparentTo(self.mother_root)
        self.stick.setPos(self.stick_position())
        self.stick.setColor(0.85, 0.75, 0.5, 1)
        self.stick.setScale(0.3, 0.3, self.level)

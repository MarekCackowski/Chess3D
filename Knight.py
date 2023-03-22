from Piece import Piece


class Knight(Piece):
    def __init__(self, position, color, beginning_board):
        self.model = "models/knight"
        super().__init__(position, color, beginning_board, self.model)

    def is_legal(self, other_piece, tile_position, squares, pieces, just_checking):
        rows_difference = self.position[1] - tile_position[1]
        columns_difference = self.position[2] - tile_position[2]
        if abs(rows_difference) == 2 and abs(columns_difference) == 1:
            return True
        elif abs(columns_difference) == 2 and abs(rows_difference) == 1:
            return True
        else:
            return False

from Piece import Piece


class Bishop(Piece):
    def __init__(self, position, color, beginning_board):
        self.model = "models/bishop"
        super().__init__(position, color, beginning_board, self.model)

    def is_legal(self, other_piece, tile_position, squares, pieces, just_checking):
        if abs(self.position[1] - tile_position[1]) == abs(self.position[2] - tile_position[2]):
            if self.position[1] > tile_position[1]:
                if self.position[2] > tile_position[2]:
                    possible_squares = self.append_possible_squares_diagonal(-1, -1, squares, tile_position)
                else:
                    possible_squares = self.append_possible_squares_diagonal(1, -1, squares, tile_position)
                return not self.check_for_other_pieces(possible_squares, pieces)
            else:
                if self.position[2] > tile_position[2]:
                    possible_squares = self.append_possible_squares_diagonal(-1, 1, squares, tile_position)
                else:
                    possible_squares = self.append_possible_squares_diagonal(1, 1, squares, tile_position)
                return not self.check_for_other_pieces(possible_squares, pieces)
        else:
            return False

    def append_possible_squares_diagonal(self, direction_2, direction_1, squares, tile_position):
        possible_squares = []
        for square in squares:
            if self.position[2] * direction_2 < square.position[2] * direction_2 < tile_position[2] * direction_2 and \
                    self.position[1] * direction_1 < square.position[1] * direction_1 < tile_position[1] * direction_1:
                if abs(square.position[2] - self.position[2]) == abs(square.position[1] - self.position[1]):
                    possible_squares.append(square)
        return possible_squares

    @staticmethod
    def check_for_other_pieces(squares, pieces):
        for piece in pieces:
            for square in squares:
                if piece and piece.position and square.position[1:3] == piece.position[1:3]:
                    return True
        return False

from Piece import Piece


class Rook(Piece):
    def __init__(self, position, color, beginning_board, is_able_to_castle):
        self.model = "models/rook"
        self.is_able_to_castle = is_able_to_castle
        super().__init__(position, color, beginning_board, self.model)

    def is_legal(self, other_piece, tile_position, squares, pieces, just_checking):
        if self.position[1] == tile_position[1]:
            if self.position[2] > tile_position[2]:
                possible_squares = self.append_possible_squares(-1, 2, squares, tile_position[2])
            else:
                possible_squares = self.append_possible_squares(1, 2, squares, tile_position[2])
            if not self.check_for_other_pieces(possible_squares, pieces, tile_position) and not just_checking:
                self.is_able_to_castle = False
            return not self.check_for_other_pieces(possible_squares, pieces, tile_position)
        elif self.position[2] == tile_position[2]:
            if self.position[1] > tile_position[1]:
                possible_squares = self.append_possible_squares(-1, 1, squares, tile_position[1])
            else:
                possible_squares = self.append_possible_squares(1, 1, squares, tile_position[1])
            if not self.check_for_other_pieces(possible_squares, pieces, tile_position) and not just_checking:
                self.is_able_to_castle = False
            return not self.check_for_other_pieces(possible_squares, pieces, tile_position)
        else:
            return False

    def append_possible_squares(self, direction, position_index, squares, tile_position):
        possible_squares = []
        for square in squares:
            if self.position[position_index] * direction < square.position[position_index] * direction < tile_position * direction:
                if square.position[2 - ((position_index + 1) % 2)] == self.position[2 - ((position_index + 1) % 2)]:
                    possible_squares.append(square)
        return possible_squares

    def check_for_other_pieces(self, squares, pieces, tile_position):
        for piece in pieces:
            for square in squares:
                if piece and square.position[1:3] == piece.position[1:3]:
                    return True
        if self.position[0] in (3, 4, 5, 6) and tile_position[0] in (3, 4, 5, 6) and self.position[0] != tile_position[0]:
            return self.position[1] in (1, 10) or self.position[2] in (1, 6)

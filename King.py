from Piece import Piece


class King(Piece):
    def __init__(self, position, color, beginning_board):
        self.model = "models/king"
        self.is_able_to_castle = True
        super().__init__(position, color, beginning_board, self.model)

    def is_legal(self, other_piece, tile_position, squares, pieces, is_checking):
        if abs(tile_position[2] - self.position[2]) <= 1 and abs(tile_position[1] - self.position[1]) <= 1:
            if other_piece is not None:
                if other_piece.color != self.color:
                    if not is_checking:
                        self.is_able_to_castle = False
            if other_piece and other_piece.color != self.color:
                return not self.is_checked(tile_position, pieces, squares)
            if not other_piece:
                return not self.is_checked(tile_position, pieces, squares)
        return False

    def try_castle(self, rook, pieces, squares, game_info, just_checking):
        if game_info.is_first_turn:
            return False
        if self.is_able_to_castle and rook.is_able_to_castle:
            if self.position[1] == rook.position[1]:
                return self.castling_in_direction(rook, pieces, squares, 2, just_checking)
            elif self.position[2] == rook.position[2]:
                return self.castling_in_direction(rook, pieces, squares, 1, just_checking)
        else:
            return False

    def castling_in_direction(self, rook, pieces, squares, position_index, just_checking):
        if self.position[position_index] > rook.position[position_index]:
            possible_squares = self.append_possible_squares(-1, position_index, squares, rook.position[position_index])
        else:
            possible_squares = self.append_possible_squares(1, position_index, squares, rook.position[position_index])
        if not self.check_for_other_pieces(possible_squares, pieces) and not just_checking:
            self.is_able_to_castle = False
            rook.is_able_to_castle = False
        return not self.check_for_other_pieces(possible_squares, pieces)

    def append_possible_squares(self, direction, position_index, squares, tile_position):
        possible_squares = []
        for square in squares:
            if self.position[position_index] * direction < square.position[position_index] * direction < tile_position * direction:
                if square.position[2 - ((position_index + 1) % 2)] == self.position[2 - ((position_index + 1) % 2)]:
                    possible_squares.append(square)
        return possible_squares

    def is_checked(self, position, pieces, squares):
        temp_position = self.position
        if position is not None:
            temp_position = self.position
            self.position = position
        for piece in pieces:
            temp_piece_position = None
            if piece and piece.color != self.color:
                if piece.position and piece.position == self.position:
                    temp_piece_position = piece.position
                    piece.position = None
                if piece.position:
                    if not isinstance(piece, King) and piece.is_legal(self, self.position, squares, pieces, True):
                        self.position = temp_position
                        if not piece.position:
                            piece.position = temp_piece_position
                        return True
                    elif isinstance(piece, King) and abs(piece.position[2] - self.position[2]) <= 1 and abs(piece.position[1] - self.position[1]) <= 1:
                        self.position = temp_position
                        if not piece.position:
                            piece.position = temp_piece_position
                        return True
                if not piece.position and temp_piece_position:
                    piece.position = temp_piece_position
        self.position = temp_position
        return False

    def check_for_other_pieces(self, squares, pieces):
        for piece in pieces:
            for square in squares:
                if piece and piece.position and (square.position[1:3] == piece.position[1:3] or (square.position and self.is_checked(square.position, pieces, squares))):
                    return True
        return self.is_checked(None, pieces, squares)

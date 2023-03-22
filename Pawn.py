from Piece import Piece
from Knight import Knight
from Rook import Rook
from Queen import Queen
from Bishop import Bishop
from panda3d.core import LPoint3


class Pawn(Piece):
    def __init__(self, position, color, beginning_board, index):
        self.model = "models/pawn"
        self.is_first_move = True
        self.en_passant = False
        self.is_white = (1 if color == (0.85, 0.75, 0.5, 1) else - 1)
        super().__init__(position, color, beginning_board, self.model)
        self.index = index

    def is_legal(self, other_piece, tile_position, squares, pieces, just_checking):
        if other_piece is not None:
            if self.position[1] + self.is_white == other_piece.position[1] and (
                    self.position[2] + 1 == other_piece.position[2] or
                    self.position[2] - 1 == other_piece.position[2]):
                if other_piece.color != self.color:
                    if not just_checking:
                        self.is_first_move = False
                return True
            else:
                return False
        else:
            if (self.position[1] + self.is_white == tile_position[1] or
                self.position[1] + 2 * self.is_white == tile_position[1] and self.is_first_move) and \
                    self.position[2] == tile_position[2]:
                if self.position[1] + 2 * self.is_white == tile_position[1]:
                    possible_path = True
                    for i in range(64):
                        if pieces[i] and pieces[i].position[1:3] == [tile_position[1] - self.is_white,
                                                                     tile_position[2]]:
                            possible_path = False
                    if possible_path:
                        if not just_checking:
                            self.is_first_move = False
                            self.en_passant = self.position[1] + 2 * self.is_white == tile_position[1]
                        return True
                    else:
                        return False
                else:
                    if not just_checking:
                        self.is_first_move = False
                        self.en_passant = self.position[1] + 2 * self.is_white == tile_position[1]
                    return True
            elif self.position[1] + self.is_white == tile_position[1] and (self.position[2] + 1 == tile_position[2] or
                                                                           self.position[2] - 1 == tile_position[2]):
                for j in range(64):
                    if pieces[j] and pieces[j].position[1] == self.position[1] and \
                            (pieces[j].position[2] + 1 == self.position[2] or
                             pieces[j].position[2] - 1 == self.position[2]) \
                            and isinstance(pieces[j], Pawn) and pieces[j].en_passant and pieces[j].is_white != self.is_white:
                        if not just_checking:
                            pieces[j].piece.setPos(LPoint3(-100, -100, -100))
                            pieces[j].position = None
                            pieces[j] = None
                        return True
                return False
            else:
                return False

    def try_promote(self, rules, square):
        if ((square.board.level == 6 and self.position[1] == rules.game_info.last_row_white_level_6)
            or (square.board.level != 6 and self.position[1] == rules.game_info.last_row_white_other_levels) and self.is_white == 1) or \
                ((square.board.level == 2 and self.position[1] == rules.game_info.last_row_black_level_2)
                 or (square.board.level != 2 and self.position[1] == rules.game_info.last_row_black_other_levels) and self.is_white == -1):
            return True
        else:
            return False

    @staticmethod
    def promote(is_promoting, highlighted_square, pieces, squares, pieces_white, pieces_black):
        index = pieces[is_promoting].index
        pieces[is_promoting].piece.setPos(LPoint3(-100, -100, -100))
        if highlighted_square == 104:
            pieces[is_promoting] = Queen(squares[is_promoting].position,
                                         pieces[is_promoting].color,
                                         squares[is_promoting].board)
        elif highlighted_square == 102:
            pieces[is_promoting] = Rook(squares[is_promoting].position,
                                        pieces[is_promoting].color,
                                        squares[is_promoting].board, False)
        elif highlighted_square == 100:
            pieces[is_promoting] = Knight(squares[is_promoting].position,
                                          pieces[is_promoting].color,
                                          squares[is_promoting].board)
        elif highlighted_square == 98:
            pieces[is_promoting] = Bishop(squares[is_promoting].position,
                                          pieces[is_promoting].color,
                                          squares[is_promoting].board)
        if pieces[is_promoting].color == (0.85, 0.75, 0.5, 1):
            pieces_white[index] = pieces[is_promoting]
        else:
            pieces_black[index] = pieces[is_promoting]

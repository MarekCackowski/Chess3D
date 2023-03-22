from Pawn import Pawn
from Queen import Queen
from Knight import Knight
from Rook import Rook
from Bishop import Bishop
from King import King
from MovableLevel import MovableLevel


class GameInfo(object):
    def __init__(self):
        self.is_white_turn = True
        self.is_first_turn = True
        self.moves_without_pawn_move_or_capture = 0
        self.positions_of_pieces = []
        self.last_row_black_other_levels = 1
        self.last_row_black_level_2 = 2
        self.last_row_white_other_levels = 10
        self.last_row_white_level_6 = 9
        # -1: black won
        # 0: tie
        # 1: white won
        self.final_result = None
        self.moving_boards_current_positions = [None, 3, None, 4, None, None, None, None, 5, None, 6, None]
        self.possible_adjacent_pins = [[2, 3, 5, 6],
                                       [1, 4, 6],
                                       [1, 4, 7, 8],
                                       [2, 3, 8],
                                       [1, 6, 7, 9, 10],
                                       [1, 2, 5, 8, 10],
                                       [3, 5, 8, 11, 12],
                                       [3, 6, 4, 7, 12],
                                       [5, 10, 11],
                                       [5, 6, 9, 12],
                                       [7, 9, 12],
                                       [7, 8, 10, 11]]
        self.owner_color = [(0.85, 0.75, 0.5, 1), (0.85, 0.75, 0.5, 1), (0.4, 0.2, 0.0, 1), (0.4, 0.2, 0.0, 1)]

    def update_moves(self, pieces, boards):
        current_positions = []
        for piece in pieces:
            if piece and piece.color == (0.85, 0.75, 0.5, 1):
                self.append_current_position(piece, current_positions, 1, boards)
            else:
                self.append_current_position(piece, current_positions, 2, boards)
        for board in boards:
            if board and isinstance(board, MovableLevel):
                current_positions.append(board.current_pin)
        self.positions_of_pieces.append(current_positions)

    @staticmethod
    def append_current_position(piece, current_positions, is_white, boards):
        if isinstance(piece, Pawn):
            current_positions.append(
                is_white * 1 + boards[piece.position[0]].level * 100 + piece.position[1] * 1000 + piece.position[
                    2] * 10000)
        elif isinstance(piece, Rook):
            current_positions.append(
                is_white * 2 + boards[piece.position[0]].level * 100 + piece.position[1] * 1000 + piece.position[
                    2] * 10000)
        elif isinstance(piece, Knight):
            current_positions.append(
                is_white * 3 + boards[piece.position[0]].level * 100 + piece.position[1] * 1000 + piece.position[
                    2] * 10000)
        elif isinstance(piece, Bishop):
            current_positions.append(
                is_white * 4 + boards[piece.position[0]].level * 100 + piece.position[1] * 1000 + piece.position[
                    2] * 10000)
        elif isinstance(piece, King):
            current_positions.append(
                is_white * 5 + boards[piece.position[0]].level * 100 + piece.position[1] * 1000 + piece.position[
                    2] * 10000)
        elif isinstance(piece, Queen):
            current_positions.append(
                is_white * 6 + boards[piece.position[0]].level * 100 + piece.position[1] * 1000 + piece.position[
                    2] * 10000)

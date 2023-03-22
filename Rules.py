from Pawn import Pawn
from Rook import Rook
from King import King
from Board import Board
from MovableLevel import MovableLevel
from panda3d.core import LPoint3


class Rules(object):
    def __init__(self, game_info):
        self.game_info = game_info
        self.movable_level_numbers = [3, 4, 5, 6]
        self.current_positions = [1, 1, 1, 1]
        self.is_only_one_piece = [False, False, False, False]

    @staticmethod
    def en_passcant(pieces, color):
        for piece in pieces:
            if piece and isinstance(piece, Pawn):
                if piece.color == color:
                    piece.en_passant = False

    def check_for_repetitions(self):
        counter = 0
        num = self.game_info.positions_of_pieces[0]
        for i in self.game_info.positions_of_pieces:
            curr_frequency = self.game_info.positions_of_pieces.count(i)
            if curr_frequency > counter:
                counter = curr_frequency
                num = i
        max = 0
        for i in self.game_info.positions_of_pieces:
            if i == num:
                max += 1
        if max >= 3:
            self.game_info.final_result = 0

    def check_for_50_moves(self):
        if self.game_info.moves_without_pawn_move_or_capture > 50:
            self.game_info.final_result = 0

    def change_first_turn(self):
        self.game_info.is_first_turn = False

    def change_turn(self):
        self.game_info.is_white_turn = not self.game_info.is_white_turn

    def check_for_moves_without_pawn_move_or_capture(self, piece):
        if not isinstance(piece, Pawn):
            self.game_info.moves_without_pawn_move_or_capture += 1
        else:
            self.game_info.moves_without_pawn_move_or_capture = 0
        if piece is not None:
            self.game_info.moves_without_pawn_move_or_capture = 0

    def check_mate_or_stalemate(self, is_white, king, squares, pieces, boards):
        for piece in pieces:
            if piece and piece.color == king.color and self.legal_move_exist(piece, king, squares, pieces):
                return None
        for board in boards:
            if isinstance(board, MovableLevel) and self.legal_move_exist(board, king, squares, pieces):
                return None
        if king.is_checked(None, pieces, squares):
            self.game_info.final_result = -1 * is_white
        else:
            self.game_info.final_result = 0

    def check_for_result(self):
        if self.game_info.final_result is not None:
            return self.game_info.final_result

    def check_pieces_on_movable_level(self, movable_level, pieces):
        total_pieces = 0
        for tile in movable_level.tiles:
            for piece in pieces:
                if piece and tile.position[1:3] == piece.position[1:3] and piece.position[0] == movable_level.number:
                    total_pieces += 1
                    last_piece = piece
        if total_pieces == 0:
            return self.game_info.owner_color[movable_level.number - 3]
        elif total_pieces == 1:
            return last_piece.color
        else:
            return None

    def possible_moves_for_movable_level(self, movable_level, pieces, color):
        index = None
        for i in range(12):
            index = i + 1 if self.game_info.moving_boards_current_positions[i] == movable_level.number else index
        moves = self.game_info.possible_adjacent_pins[index - 1]
        if self.check_pieces_on_movable_level(movable_level, pieces) is True:
            temp_moves = self.copy_tab(moves)
            for i in range(len(temp_moves)):
                temp_moves[i] -= 1
            return temp_moves
        elif self.check_pieces_on_movable_level(movable_level, pieces) == color:
            is_white_turn = 1 if color == (0.85, 0.75, 0.5, 1) else -1
            temp_moves = self.copy_tab(moves)
            for i in range(len(temp_moves)):
                if temp_moves[i] - is_white_turn == index or temp_moves[i] + 4 * is_white_turn == index or temp_moves[i] - 5 * is_white_turn == index:
                    temp_moves[i] = None
                if temp_moves[i] and self.game_info.moving_boards_current_positions[temp_moves[i] - 1]:
                    temp_moves[i] = None
                if temp_moves[i]:
                    temp_moves[i] -= 1
            return temp_moves
        else:
            return None

    @staticmethod
    def copy_tab(moves):
        copy = [None for i in range(len(moves))]
        for i in range(len(moves)):
            copy[i] = moves[i]
        return copy

    def swap_pins(self, number, to):
        for i in range(12):
            if self.game_info.moving_boards_current_positions[i] == number:
                self.game_info.moving_boards_current_positions[i] = None
                break
        self.game_info.moving_boards_current_positions[to] = number

    def legal_move_exist(self, piece, king, squares, pieces):
        if isinstance(piece, Board):
            possible_moves = self.possible_moves_for_movable_level(piece, pieces, king.color)
            if possible_moves is not None:
                for i in range(len(possible_moves)):
                    if possible_moves[i]:
                        self.change_board_position(piece.tiles, possible_moves[i], piece.current_pin, piece.number, 1, False, pieces, squares)
                        if not king.is_checked(None, pieces, squares):
                            self.change_board_position(piece.tiles, possible_moves[i], piece.current_pin, piece.number, -1, False, pieces, squares)
                            return True
                        self.change_board_position(piece.tiles, possible_moves[i], piece.current_pin, piece.number, 1, True, pieces, squares)
                        if not king.is_checked(None, pieces, squares):
                            self.change_board_position(piece.tiles, possible_moves[i], piece.current_pin, piece.number, -1, True, pieces, squares)
                            return True
            return False
        temp_piece = piece.position
        for square in squares:
            skip = False
            for other_piece in pieces:
                temp_other_piece = None
                temp_other_piece_position = None
                if other_piece and other_piece.position == square.position:
                    if other_piece.color != piece.color:
                        temp_other_piece_position = other_piece.position
                        temp_other_piece = other_piece
                    else:
                        skip = True
            rooks = []
            for other_piece in pieces:
                if other_piece and isinstance(other_piece, Rook) and other_piece.color == piece.color:
                    rooks.append(other_piece)
            if not skip:
                if not isinstance(piece, King) and piece.is_legal(temp_other_piece, square.position, squares, pieces, True):
                    piece.position = square.position
                    if temp_other_piece:
                        temp_other_piece.position = None
                    if not king.is_checked(None, pieces, squares):
                        if temp_other_piece:
                            temp_other_piece.position = temp_other_piece_position
                        piece.position = temp_piece
                        return True
                elif isinstance(piece, King) and (piece.is_legal(temp_other_piece, square.position, squares, pieces, True)
                                                  or (len(rooks) > 0 and piece.try_castle(rooks[0], pieces, squares, self.game_info, True))
                                                  or (len(rooks) > 1 and piece.try_castle(rooks[1], pieces, squares, self.game_info, True))):
                    piece.position = square.position
                    if temp_other_piece:
                        temp_other_piece.position = None
                    if not king.is_checked(None, pieces, squares):
                        if temp_other_piece:
                            temp_other_piece.position = temp_other_piece_position
                        piece.position = temp_piece
                        return True
                piece.position = temp_piece
        return False

    def change_board_position(self, tiles, to, fr, number, is_not_cancel, is_rotated, pieces, squares):
        change_rotate_board = 1 if is_rotated else 0
        sign = 1 * is_not_cancel if fr > to else -1 * is_not_cancel
        i = 0
        for tile in tiles:
            if abs(fr - to) == 1:
                pos = tile.square.getPos() + LPoint3(((1 - change_rotate_board) if i % 2 == 1 else change_rotate_board) - 0.5, 4 * sign + ((1 - change_rotate_board) if i > 1 else change_rotate_board) - 0.5, 1)
            elif abs(fr - to) == 2:
                pos = tile.square.getPos() + LPoint3(((1 - change_rotate_board) if i % 2 == 1 else change_rotate_board) + (-4 * sign) - 0.5, ((1 - change_rotate_board) if i > 1 else change_rotate_board) - 0.5, 1)
            elif abs(fr - to) == 4:
                pos = tile.square.getPos() + LPoint3(((1 - change_rotate_board) if i % 2 == 1 else change_rotate_board) - 0.5, -2 * sign + ((1 - change_rotate_board) if i > 1 else change_rotate_board) - 0.5, -4 * sign + 1)
            elif abs(fr - to) == 5:
                pos = tile.square.getPos() + LPoint3(((1 - change_rotate_board) if i % 2 == 1 else change_rotate_board) - 0.5, 2 * sign + ((1 - change_rotate_board) if i > 1 else change_rotate_board) - 0.5, -4 * sign + 1)
            self.update_position(number, tile.index, pos, pieces, squares)
            i += 1

    @staticmethod
    def update_position(number, index, pos, pieces, squares):
        if pieces[index]:
            pieces[index].position = [number, pos[1] + 1, pos[0] + 1]
        if squares[index]:
            squares[index].position = [number, pos[1] + 1, pos[0] + 1]

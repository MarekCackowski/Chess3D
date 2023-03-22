from direct.showbase.ShowBase import ShowBase
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import AmbientLight, DirectionalLight
from panda3d.core import LPoint3, LVector3, BitMask32
from direct.gui.OnscreenText import OnscreenText
from direct.task.Task import Task
from Board import Board
from Tile import Tile
from Pawn import Pawn
from Queen import Queen
from Knight import Knight
from Rook import Rook
from Bishop import Bishop
from King import King
from MovableLevel import MovableLevel
from Rules import Rules
from GameInfo import GameInfo
import numpy as np


class Stage(ShowBase):
    def __init__(self, boards, pieces_white, pieces_black, rules):
        super().__init__()
        self.disableMouse()
        camera.setPosHpr(30, 5, 23, 90, -30, 0)
        self.setup_lights()
        self.picker = CollisionTraverser()
        self.pq = CollisionHandlerQueue()
        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))
        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.picker.addCollider(self.pickerNP, self.pq)
        self.highlighted = False
        self.dragging = False
        self.mouse_task = taskMgr.add(self.mouse_task, 'mouse_task')
        self.update_clock = taskMgr.add(self.update_clock, 'update_clock')
        self.accept("mouse1", self.grab)
        self.accept("mouse1-up", self.release)
        self.accept('q', self.rotate_camera)
        self.accept('w', self.cancel_move)
        self.accept('e', self.change_rotate_board)
        self.accept('r', self.start_new)
        self.current_position = True
        self.mother_root = render.attachNewNode("mother_root")
        self.current_square = None

        self.rules = rules
        self.boards = boards
        self.pieces_white = pieces_white
        self.pieces_black = pieces_black
        self.pieces = [None for i in range(64)]
        self.pieces_to_promote = [None for i in range(4)]
        self.squares = [None for i in range(64)]
        self.adjacent_pins = [None for i in range(12)]
        self.sticks = [None for i in range(4)]
        self.index = 0
        self.index_adjacent_pins = 0
        self.is_promoting = False
        self.base = None
        self.rotate_board = 0
        self.was_rotated = [0 for i in range(4)]
        self.current_camera_position = True
        self.promoted_due_to_board_movement = False
        self.time_white = 3600
        self.time_black = 3600
        self.text_white = OnscreenText(text='White: ' + str(self.time_white // 60) + ':' + str(self.time_white % 60),
                                       pos=(0.9, 0.9), scale=0.05)
        self.text_black = OnscreenText(
            text='Black: ' + str(int(self.time_black // 60)) + ':' + str(int(self.time_black % 60)), pos=(0.9, 0.85),
            scale=0.05)
        self.text_result = None

    def update_clock(self, task):
        if self.rules.game_info.final_result is None:
            if self.rules.game_info.is_white_turn:
                self.time_white -= globalClock.getDt()
            else:
                self.time_black -= globalClock.getDt()
            self.text_white.destroy()
            self.text_white = OnscreenText(
                text='White: ' + str(int(self.time_white // 60)) + ':' + str(int(self.time_white % 60)) + (
                    '' if self.time_white % 60 > 9 else '0'), pos=(0.9, 0.9), scale=0.05)
            self.text_black.destroy()
            self.text_black = OnscreenText(
                text='Black: ' + str(int(self.time_black // 60)) + ':' + str(int(self.time_black % 60)) + (
                    '' if self.time_black % 60 > 9 else '0'), pos=(0.9, 0.85), scale=0.05)
            if self.time_white < 0:
                self.rules.game_info.final_result = -1
                self.end_game(-1)
            if self.time_black < 0:
                self.rules.game_info.final_result = 1
                self.end_game(1)
            return task.cont

    @staticmethod
    def setup_lights():
        ambient_light = AmbientLight("ambient_light")
        ambient_light.setColor((.8, .8, .8, 1))
        directional_light = DirectionalLight("directional_light")
        directional_light.setDirection(LVector3(0, 45, -45))
        directional_light.setColor((0.2, 0.2, 0.2, 1))
        render.setLight(render.attachNewNode(directional_light))
        render.setLight(render.attachNewNode(ambient_light))

    @staticmethod
    def camera_position(current_position):
        if current_position:
            camera.setPosHpr(30, 5, 23, 90, -30, 0)
        else:
            camera.setPosHpr(3, -16, 28, 0, -45, 0)

    def cancel_move(self):
        self.cancel_move_piece()
        self.cancel_move_board()
        if self.rules.game_info.is_white_turn:
            self.time_white -= 120
        else:
            self.time_black -= 120

    def cancel_move_piece(self):
        if self.dragging and self.dragging < 64 and self.pieces[self.dragging]:
            self.pieces[self.dragging].piece.setPos(self.tile_position(self.dragging))
            self.dragging = False
            self.highlighted = False

    def cancel_move_board(self):
        if self.dragging and self.dragging > 499:
            movable_level = self.boards[self.dragging - 497]
            self.rotate_board = self.was_rotated[movable_level.number - 3]
            i = 0
            for tile in movable_level.tiles:
                tile_near_point = self.current_position + LPoint3(
                    ((1 - self.rotate_board) if i % 2 == 1 else self.rotate_board) - 0.5,
                    ((1 - self.rotate_board) if i > 1 else self.rotate_board) - 0.5, 1)
                i += 1
                for piece in self.pieces:
                    if piece and piece.piece.getPos() == tile.square.getPos():
                        piece.piece.setPos(tile_near_point)
                tile.square.setPos(tile_near_point)
                self.update_position(movable_level.number, tile.index, tile_near_point)
            movable_level.stick.setPos(self.current_position)
            self.rotate_board = 0
            self.dragging = False
            self.highlighted = False

    def rotate_camera(self):
        self.camera_position(self.current_camera_position)
        self.current_camera_position = not self.current_camera_position

    def change_rotate_board(self):
        self.rotate_board = 1 - self.rotate_board

    @staticmethod
    def if_null(var, val):
        if var is None:
            return val
        return var.color

    def draw_boards(self):
        for board in self.boards:
            board.mother_root = self.mother_root
            i = 0
            for row in range(0, board.rows):
                for column in range(0, board.columns):
                    if row % 2 == column % 2:
                        color = (0, 0, 0, 1)
                    else:
                        color = (1, 1, 1, 1)
                    board.tiles[i] = Tile([board.number, row + board.first_row, column + board.first_column], color,
                                          self.index, board, row, column)
                    self.squares[self.index] = board.tiles[i]
                    i += 1
                    self.index += 1
            if not isinstance(board, MovableLevel):
                board.draw_adjacent_pins(self.index_adjacent_pins)
                board.draw_stick()
                self.index_adjacent_pins += 4
            else:
                (board.draw_stick())
        self.index_adjacent_pins = 0
        index_sticks = 0
        for board in self.boards:
            if not isinstance(board, MovableLevel):
                for i in range(4):
                    self.adjacent_pins[self.index_adjacent_pins] = board.adjacent_pins[i]
                    self.index_adjacent_pins += 1
            else:
                self.sticks[index_sticks] = board.stick
                index_sticks += 1

        self.draw_base()

    def draw_base(self):
        self.base = loader.loadModel("models/cube.egg")
        self.base.reparentTo(self.mother_root)
        self.base.setPos(LPoint3(2.5, 4.7, -2))
        self.base.setColor(0.85, 0.75, 0.5, 1)
        self.base.setScale(2, 3.5, 0.1)

    def find_squares_for_pieces(self):
        for piece in self.pieces_white:
            for board in self.boards:
                for tile in board.tiles:
                    if tile.position == piece.position:
                        piece.square = int(tile.index)
                        break
                if piece.square is not None:
                    break
            self.pieces[piece.square] = piece
        for piece in self.pieces_black:
            for board in self.boards:
                for tile in board.tiles:
                    if tile.position == piece.position:
                        piece.square = int(tile.index)
            self.pieces[piece.square] = piece
        board = self.draw_promotion_choices()
        for piece in self.pieces_to_promote:
            for tile in board.tiles:
                if tile.position == piece.position:
                    piece.square = int(tile.index)

    def draw_promotion_choices(self):
        board = Board(1, 100, 1, 1)
        board.mother_root = self.mother_root
        tiles = [Tile([1, 1, 104], (0.85, 0.8, 0.2, 1), 104, board, None, None),
                 Tile([1, 1, 102], (0.85, 0.8, 0.2, 1), 102, board, None, None),
                 Tile([1, 1, 100], (0.85, 0.8, 0.2, 1), 100, board, None, None),
                 Tile([1, 1, 98], (0.85, 0.8, 0.2, 1), 98, board, None, None)]
        board.tiles = tiles
        self.pieces_to_promote = [Queen([1, 1, 104], (0.7, 0.7, 0.7, 1), board),
                                  Rook([1, 1, 102], (0.7, 0.7, 0.7, 1), board, False),
                                  Knight([1, 1, 100], (0.7, 0.7, 0.7, 1), board),
                                  Bishop([1, 1, 98], (0.7, 0.7, 0.7, 1), board)]
        return board

    def square_color(self, i):
        return self.squares[i].color

    def tile_position(self, index):
        return self.squares[index].tile_position(self.squares[index].position)

    def change_board_position(self, tiles, stick, to, fr, number, is_not_cancel):
        sign = 1 * is_not_cancel if fr > to else -1 * is_not_cancel
        i = 0
        for tile in tiles:
            if abs(fr - to) == 1:
                pos = self.current_position + LPoint3(
                    ((1 - self.rotate_board) if i % 2 == 1 else self.rotate_board) - 0.5,
                    4 * sign + ((1 - self.rotate_board) if i > 1 else self.rotate_board) - 0.5, 1)
            elif abs(fr - to) == 2:
                pos = self.current_position + LPoint3(
                    ((1 - self.rotate_board) if i % 2 == 1 else self.rotate_board) + (-4 * sign) - 0.5,
                    ((1 - self.rotate_board) if i > 1 else self.rotate_board) - 0.5, 1)
            elif abs(fr - to) == 4:
                pos = self.current_position + LPoint3(
                    ((1 - self.rotate_board) if i % 2 == 1 else self.rotate_board) - 0.5,
                    -2 * sign + ((1 - self.rotate_board) if i > 1 else self.rotate_board) - 0.5, -4 * sign + 1)
            elif abs(fr - to) == 5:
                pos = self.current_position + LPoint3(
                    ((1 - self.rotate_board) if i % 2 == 1 else self.rotate_board) - 0.5,
                    2 * sign + ((1 - self.rotate_board) if i > 1 else self.rotate_board) - 0.5, -4 * sign + 1)
            tile.square.setPos(pos)
            self.update_position(number, tile.index, pos)
            i += 1
        if is_not_cancel == 1:
            if abs(fr - to) == 1:
                stick.setPos(self.current_position + LPoint3(0, 4 * sign, 0))
            elif abs(fr - to) == 2:
                stick.setPos(self.current_position + LPoint3(-4 * sign, 0, 0))
            elif abs(fr - to) == 4:
                stick.setPos(self.current_position + LPoint3(0, -2 * sign, -4 * sign))
            elif abs(fr - to) == 5:
                stick.setPos(self.current_position + LPoint3(0, 2 * sign, -4 * sign))

    def update_position(self, number, index, pos):
        if self.pieces[index]:
            self.pieces[index].position = [number, pos[1] + 1, pos[0] + 1]
            self.pieces[index].piece.setPos(pos)
        if self.squares[index]:
            self.squares[index].position = [number, pos[1] + 1, pos[0] + 1]

    def tile_board_number(self, index):
        return self.squares[index].board.number

    @staticmethod
    def point_at_z(z, point, vec):
        return point + vec * ((z - point.getZ()) / vec.getZ())

    def mouse_task(self, task):
        if self.highlighted is not False and self.is_promoting is False:
            if self.highlighted < 64:
                self.squares[self.highlighted].square.setColor(self.square_color(self.highlighted))
            elif self.highlighted in (500, 501, 502, 503):
                self.sticks[self.highlighted - 500].setColor(0.85, 0.75, 0.5, 1)
            elif self.highlighted > 999:
                self.adjacent_pins[self.highlighted - 1000].setColor(0.85, 0.75, 0.5, 1)
            self.highlighted = False
        if self.mouseWatcherNode.hasMouse():
            mouse_position = self.mouseWatcherNode.getMouse()
            self.pickerRay.setFromLens(self.camNode, mouse_position.getX(), mouse_position.getY())
            if self.dragging is not False:
                near_point = render.getRelativePoint(camera, self.pickerRay.getOrigin())
                near_vec = render.getRelativeVector(camera, self.pickerRay.getDirection())
                if self.dragging < 64:
                    self.pieces[self.dragging].piece.setPos(self.point_at_z(0.5, near_point, near_vec))
                elif self.dragging in (500, 501, 502, 503):
                    movable_level = self.boards[self.dragging - 497]
                    i = 0
                    for tile in movable_level.tiles:
                        tile_near_point = near_point + LPoint3(
                            ((1 - self.rotate_board) if i % 2 == 1 else self.rotate_board),
                            ((1 - self.rotate_board) if i > 1 else self.rotate_board) - 0.5, 1.5)
                        for piece in self.pieces:
                            if piece and piece.position == tile.position:
                                piece.piece.setPos(self.point_at_z(0.5, tile_near_point, near_vec))
                        tile.square.setPos(self.point_at_z(0.5, tile_near_point, near_vec))
                        self.update_position(movable_level.number, tile.index,
                                             self.point_at_z(0.5, tile_near_point, near_vec))
                        i += 1
                    movable_level.stick.setPos(self.point_at_z(0.5, near_point, near_vec))
            self.picker.traverse(self.mother_root)
            if self.pq.getNumEntries() > 0:
                self.pq.sortEntries()
                i = int(self.pq.getEntry(0).getIntoNode().getTag('object'))
                if i < 64:
                    self.squares[i].square.setColor(1, 0, 0, 1)
                elif i > 999:
                    self.adjacent_pins[i - 1000].setColor(1, 0, 0, 1)
                elif i in (500, 501, 502, 503):
                    self.sticks[i - 500].setColor(1, 0, 0, 1)
                self.highlighted = i
        return Task.cont

    def grab(self):
        self.grab_piece()
        self.grab_board()

    def grab_piece(self):
        if 64 < self.highlighted < 500:
            self.pieces[self.is_promoting].promote(self.is_promoting, self.highlighted, self.pieces,
                                                   self.squares, self.pieces_white, self.pieces_black)
            self.camera_position(self.current_camera_position)
            if not self.promoted_due_to_board_movement:
                self.rules.change_turn()
            self.highlighted = self.is_promoting
            self.is_promoting = False
        elif self.highlighted < 500 and self.highlighted is not False and self.pieces[self.highlighted]:
            king = self.find_king(self.pieces[self.highlighted].color)
            if not self.dragging and self.rules.legal_move_exist(self.pieces[self.highlighted], king, self.squares,
                                                                 self.pieces):
                if (self.pieces[self.highlighted] in self.pieces_white and self.rules.game_info.is_white_turn) \
                        or (
                        self.pieces[self.highlighted] in self.pieces_black and not self.rules.game_info.is_white_turn):
                    self.dragging = self.highlighted
                    self.highlighted = False
                    self.current_position = self.pieces[self.dragging].piece.getPos()

    def grab_board(self):
        if self.highlighted in (500, 501, 502, 503):
            movable_level = self.boards[self.highlighted - 497]
            if self.rules.game_info.is_white_turn:
                king = self.find_king((0.85, 0.75, 0.5, 1))
            else:
                king = self.find_king((0.4, 0.2, 0.0, 1))
            if not self.dragging and self.rules.legal_move_exist(movable_level, king, self.squares, self.pieces):
                self.dragging = self.highlighted
                self.current_position = movable_level.stick.getPos()
                self.highlighted = False

    def release(self):
        self.release_piece()
        self.release_board()

    def release_piece(self):
        if self.dragging is not False and self.is_promoting is False and self.dragging < 500:
            if self.pieces[self.dragging].piece.getPos() != self.current_position:
                if self.make_move_piece(self.dragging, self.highlighted):
                    self.dragging = False
                    self.pawn_release()
                    if not self.is_promoting:
                        self.after_turn()

    def release_board(self):
        if self.dragging is not False and self.dragging in (500, 501, 502, 503):
            movable_level = self.boards[self.dragging - 497]
            if movable_level.stick.getPos() != self.current_position:
                if self.make_move_board(self.dragging, self.highlighted):
                    self.dragging = False
                    self.was_rotated[movable_level.number - 3] = self.rotate_board
                    self.after_turn()

    def after_turn(self):
        self.rotate_board = 0
        self.rules.game_info.update_moves(self.pieces, self.boards)
        self.rules.check_for_repetitions()
        self.rules.check_for_50_moves()
        if not self.rules.game_info.is_white_turn:
            self.rules.en_passcant(self.pieces, (0.85, 0.75, 0.5, 1))
            king = self.find_king((0.85, 0.75, 0.5, 1))
            self.rules.check_mate_or_stalemate(1, king, self.squares, self.pieces, self.boards)
            self.rules.change_first_turn()
        else:
            self.rules.en_passcant(self.pieces, (0.4, 0.2, 0.0, 1))
            king = self.find_king((0.4, 0.2, 0.0, 1))
            self.rules.check_mate_or_stalemate(-1, king, self.squares, self.pieces, self.boards)
        result = self.rules.check_for_result()
        if result is not None:
            self.end_game(result)
        self.rules.change_turn()

    def make_move_piece(self, fr, to):
        if to > 499:
            return False
        temp = self.pieces[fr]
        self.pieces[fr] = self.pieces[to]
        self.pieces[to] = temp
        first_argument = True
        is_castling = False
        first_argument = self.pieces[to].is_legal(self.pieces[fr], self.squares[self.highlighted].position,
                                                  self.squares, self.pieces, False)
        if self.pieces[fr] and self.if_null(self.pieces[to], (1, 1, 1, 0)) == self.if_null(self.pieces[fr],
                                                                                           (0, 0, 0, 0)):
            if isinstance(self.pieces[to], King) and isinstance(self.pieces[fr], Rook):
                first_argument = self.pieces[to].try_castle(self.pieces[fr], self.pieces, self.squares,
                                                            self.rules.game_info, False)
                is_castling = first_argument
        if not first_argument or (self.if_null(self.pieces[to], (1, 1, 1, 0)) == self.if_null(self.pieces[fr], (
                0, 0, 0, 0)) and not is_castling):
            temp = self.pieces[fr]
            self.pieces[fr] = self.pieces[to]
            self.pieces[to] = temp
            return False
        self.rules.check_for_moves_without_pawn_move_or_capture(self.pieces[to])
        if self.pieces[fr] and not is_castling:
            self.place_piece(fr, LPoint3(-100, -100, -100), None, fr, self.squares)
            self.rules.check_for_moves_without_pawn_move_or_capture(self.pieces[fr])
        elif self.pieces[fr] and is_castling:
            old_rook_position = self.pieces[fr].position
            self.place_piece(fr, self.tile_position(fr), self.squares[fr].position, fr, self.squares)
        if self.pieces[to]:
            if is_castling and old_rook_position[0] in (3, 5):
                for i in range(64):
                    if self.squares[i].position[1:3] == [old_rook_position[1], old_rook_position[2] + 1]:
                        king_destination = i
                self.place_piece(to, self.tile_position(king_destination), self.squares[king_destination].position,
                                 king_destination, self.squares)
            else:
                self.place_piece(to, self.tile_position(to), self.squares[to].position, to, self.squares)
        return True

    def make_move_board(self, fr, to):
        if to < 999:
            return False
        movable_level = self.boards[fr - 497]
        color = (0.85, 0.75, 0.5, 1) if self.rules.game_info.is_white_turn else (0.4, 0.2, 0.0, 1)
        if self.rules.possible_moves_for_movable_level(movable_level, self.pieces, color) and \
                to - 1000 in self.rules.possible_moves_for_movable_level(movable_level, self.pieces, color):
            king = self.find_king((0.85, 0.75, 0.5, 1) if self.rules.game_info.is_white_turn else (0.4, 0.2, 0.0, 1))
            self.change_board_position(movable_level.tiles, movable_level.stick, to - 1000, movable_level.current_pin,
                                       movable_level.number, 1)
            if not king.is_checked(None, self.pieces, self.squares):
                movable_level.level = int(((movable_level.tiles[0].square.getPos()[2] + 2) / 2) // 1)
                for i in range(len(self.squares)):
                    if self.squares[i] and self.squares[i].position[1] in (1, 10):
                        self.promoted_due_to_board_movement = True
                        self.try_promote(self.squares[i], i)
                self.rules.swap_pins(movable_level.number, to - 1000)
                movable_level.current_pin = to - 1000
                return True
            else:
                self.change_board_position(movable_level.tiles, movable_level.stick, to - 1000,
                                           movable_level.current_pin, movable_level.number, -1)
                return False
        else:
            return False

    def pawn_release(self):
        if isinstance(self.pieces[self.highlighted], Pawn):
            self.promoted_due_to_board_movement = False
            self.try_promote(self.squares[self.dragging], self.highlighted)

    def try_promote(self, square, position):
        if self.pieces[position] and isinstance(self.pieces[position], Pawn) and self.pieces[position].try_promote(
                self.rules, square):
            camera.setPosHpr(100, 11, 1, 180, 0, 0)
            self.is_promoting = position

    def place_piece(self, piece_index, pos, position, square_index, squares):
        self.pieces[piece_index].position = position
        for square in squares:
            if square.square.getPos == self.pieces[piece_index].piece.getPos:
                self.pieces[piece_index].position[0] = self.tile_board_number(square_index)
        self.pieces[piece_index].piece.setPos(pos)
        if pos != LPoint3(-100, -100, -100):
            self.pieces[piece_index].square = square_index
        else:
            self.pieces[piece_index] = None

    def find_king(self, color):
        for piece in self.pieces:
            if piece and isinstance(piece, King) and piece.color == color:
                return piece

    def end_game(self, result):
        if result == 1:
            self.text_result = OnscreenText(text='White Won', pos=(0.0, 0.0), scale=0.5)
        elif result == 0:
            self.text_result = OnscreenText(text='Tie', pos=(0.0, 0.0), scale=0.5)
        elif result == -1:
            self.text_result = OnscreenText(text='Black Won', pos=(0.0, 0.0), scale=0.5)

    def start_new(self):
        if self.rules.game_info.final_result is not None:
            self.text_result.destroy()
            black = (0.4, 0.2, 0.0, 1)
            white = (0.85, 0.75, 0.5, 1)
            boards = np.array([Board(2, 0, 2, 2),
                               Board(4, 1, 4, 2),
                               Board(6, 2, 6, 2),
                               MovableLevel(True, 3, 3),
                               MovableLevel(False, 4, 3),
                               MovableLevel(True, 5, 7),
                               MovableLevel(False, 6, 7)])

            pieces_white = np.array([Pawn([3, 2, 1], white, boards[3], 0),
                                     Pawn([3, 2, 2], white, boards[3], 1),
                                     Pawn([0, 3, 2], white, boards[0], 2),
                                     Pawn([0, 3, 3], white, boards[0], 3),
                                     Pawn([0, 3, 4], white, boards[0], 4),
                                     Pawn([0, 3, 5], white, boards[0], 5),
                                     Pawn([4, 2, 5], white, boards[4], 6),
                                     Pawn([4, 2, 6], white, boards[4], 7),
                                     Rook([3, 1, 1], white, boards[3], True),
                                     Queen([3, 1, 2], white, boards[3]),
                                     Bishop([0, 2, 2], white, boards[0]),
                                     Knight([0, 2, 3], white, boards[0]),
                                     Knight([0, 2, 4], white, boards[0]),
                                     Bishop([0, 2, 5], white, boards[0]),
                                     King([4, 1, 5], white, boards[4]),
                                     Rook([4, 1, 6], white, boards[4], True)])

            pieces_black = np.array([Pawn([5, 9, 1], black, boards[5], 0),
                                     Pawn([5, 9, 2], black, boards[5], 1),
                                     Pawn([2, 8, 2], black, boards[2], 2),
                                     Pawn([2, 8, 3], black, boards[2], 3),
                                     Pawn([2, 8, 4], black, boards[2], 4),
                                     Pawn([2, 8, 5], black, boards[2], 5),
                                     Pawn([6, 9, 5], black, boards[6], 6),
                                     Pawn([6, 9, 6], black, boards[6], 7),
                                     Rook([5, 10, 1], black, boards[5], True),
                                     Queen([5, 10, 2], black, boards[5]),
                                     Bishop([2, 9, 2], black, boards[2]),
                                     Knight([2, 9, 3], black, boards[2]),
                                     Knight([2, 9, 4], black, boards[2]),
                                     Bishop([2, 9, 5], black, boards[2]),
                                     King([6, 10, 5], black, boards[6]),
                                     Rook([6, 10, 6], black, boards[6], True)])
            for piece in self.pieces:
                if piece:
                    piece.piece.setPos(LPoint3(-100, -100, -100))
            self.pieces = [None for i in range(64)]
            self.pieces_to_promote = [None for i in range(4)]
            self.squares = [None for i in range(64)]
            self.adjacent_pins = [None for i in range(12)]
            self.sticks = [None for i in range(4)]
            self.index = 0
            self.index_adjacent_pins = 0
            self.is_promoting = False
            self.base = None
            self.rotate_board = 0
            self.was_rotated = [0 for i in range(4)]
            self.current_camera_position = True
            self.promoted_due_to_board_movement = False
            self.time_white = 3600
            self.time_black = 3600
            self.text_white.destroy()
            self.text_black.destroy()
            self.boards = boards
            self.pieces_white = pieces_white
            self.pieces_black = pieces_black
            self.draw_boards()
            self.find_squares_for_pieces()
            self.rules = Rules(GameInfo())
            self.accept("mouse1", self.grab)
            self.accept("mouse1-up", self.release)
            self.accept('q', self.rotate_camera)
            self.accept('w', self.cancel_move)
            self.accept('e', self.change_rotate_board)
            self.accept('r', self.start_new)
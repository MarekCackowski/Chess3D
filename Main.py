from MovableLevel import MovableLevel
from Board import Board
from Stage import Stage
from Pawn import Pawn
from Rook import Rook
from Queen import Queen
from Knight import Knight
from Bishop import Bishop
from King import King
from Rules import Rules
from GameInfo import GameInfo
import numpy as np

BLACK = (0.4, 0.2, 0.0, 1)
WHITE = (0.85, 0.75, 0.5, 1)

stage = Stage(None, None, None, Rules(GameInfo()))

boards = np.array([Board(2, 0, 2, 2),
                   Board(4, 1, 4, 2),
                   Board(6, 2, 6, 2),
                   MovableLevel(True, 3, 3),
                   MovableLevel(False, 4, 3),
                   MovableLevel(True, 5, 7),
                   MovableLevel(False, 6, 7)])

pieces_white = np.array([Pawn([3, 2, 1], WHITE, boards[3], 0),
                        Pawn([3, 2, 2], WHITE, boards[3], 1),
                        Pawn([0, 3, 2], WHITE, boards[0], 2),
                        Pawn([0, 3, 3], WHITE, boards[0], 3),
                        Pawn([0, 3, 4], WHITE, boards[0], 4),
                        Pawn([0, 3, 5], WHITE, boards[0], 5),
                        Pawn([4, 2, 5], WHITE, boards[4], 6),
                        Pawn([4, 2, 6], WHITE, boards[4], 7),
                        Rook([3, 1, 1], WHITE, boards[3], True),
                        Queen([3, 1, 2], WHITE, boards[3]),
                        Bishop([0, 2, 2], WHITE, boards[0]),
                        Knight([0, 2, 3], WHITE, boards[0]),
                        Knight([0, 2, 4], WHITE, boards[0]),
                        Bishop([0, 2, 5], WHITE, boards[0]),
                        King([4, 1, 5], WHITE, boards[4]),
                        Rook([4, 1, 6], WHITE, boards[4], True)])

pieces_black = np.array([Pawn([5, 9, 1], BLACK, boards[5], 0),
                        Pawn([5, 9, 2], BLACK, boards[5], 1),
                        Pawn([2, 8, 2], BLACK, boards[2], 2),
                        Pawn([2, 8, 3], BLACK, boards[2], 3),
                        Pawn([2, 8, 4], BLACK, boards[2], 4),
                        Pawn([2, 8, 5], BLACK, boards[2], 5),
                        Pawn([6, 9, 5], BLACK, boards[6], 6),
                        Pawn([6, 9, 6], BLACK, boards[6], 7),
                        Rook([5, 10, 1], BLACK, boards[5], True),
                        Queen([5, 10, 2], BLACK, boards[5]),
                        Bishop([2, 9, 2], BLACK, boards[2]),
                        Knight([2, 9, 3], BLACK, boards[2]),
                        Knight([2, 9, 4], BLACK, boards[2]),
                        Bishop([2, 9, 5], BLACK, boards[2]),
                        King([6, 10, 5], BLACK, boards[6]),
                        Rook([6, 10, 6], BLACK, boards[6], True)])

stage.boards = boards
stage.pieces_white = pieces_white
stage.pieces_black = pieces_black
stage.draw_boards()
stage.find_squares_for_pieces()

stage.run()

# -*- coding: utf-8 -*-
import random


WHITE_KING    = "♔"
WHITE_QUEEN   = "♕"
WHITE_BISHOP  = "♗"
WHITE_KNIGHT  = "♘"
WHITE_ROOK    = "♖"
WHITE_PAWN    = "♙"
BLACK_KING    = "♚"
BLACK_QUEEN   = "♛"
BLACK_BISHOP  = "♝"
BLACK_KNIGHT  = "♞"
BLACK_ROOK    = "♜"
BLACK_PAWN    = "♟"


class Board(object):
  def __init__(self):
    self._board = []
    for _ in xrange(8):
      self._board.append([None] * 8)

    self._init_pieces()

  def _init_pieces(self):
    self._board[0][0] = BLACK_ROOK
    self._board[0][1] = BLACK_KNIGHT
    self._board[0][2] = BLACK_BISHOP
    self._board[0][3] = BLACK_QUEEN
    self._board[0][4] = BLACK_KING
    self._board[0][5] = BLACK_BISHOP
    self._board[0][6] = BLACK_KNIGHT
    self._board[0][7] = BLACK_ROOK
    for x in range(8):
      self._board[1][x] = BLACK_PAWN

    self._board[7][0] = WHITE_ROOK
    self._board[7][1] = WHITE_KNIGHT
    self._board[7][2] = WHITE_BISHOP
    self._board[7][3] = WHITE_QUEEN
    self._board[7][4] = WHITE_KING
    self._board[7][5] = WHITE_BISHOP
    self._board[7][6] = WHITE_KNIGHT
    self._board[7][7] = WHITE_ROOK
    for x in range(8):
      self._board[6][x] = WHITE_PAWN

  def is_in_bounds(self, x, y):
    return 0 <= x < 8 and 0 <= y < 8

  def get_piece(self, x, y):
    return self._board[x][y]

  def set_piece(self, piece, x, y):
    self._board[x][y] = piece

  def get_moves(self, x, y):
    if self._board[x][y] == None:
      return []

    elif self.is_king(self._board[x][y]):
      return [(x-1, y), (x+1, y), (x, y-1), (x,y+1)]

    elif self.is_queen(self._board[x][y]):
      # vertial/horizontal
      moves = []
      moves += [(queen_x, y) for queen_x in range(x, 8)]
      moves += [(queen_x, y) for queen_x in range(0, x)]
      moves += [(x, queen_x) for queen_x in range(y, 8)]
      moves += [(x, queen_x) for queen_x in range(0, y)]

      # diagonal
      queen_x = x + 1
      queen_y = y + 1
      while self.is_in_bounds(queen_x, queen_y):
        moves.append((queen_x, queen_y))
        queen_x += 1
        queen_y += 1

      queen_x = x - 1
      queen_y = y + 1
      while self.is_in_bounds(queen_x, queen_y):
        moves.append((queen_x, queen_y))
        queen_x -= 1
        queen_y += 1

      queen_x = x + 1
      queen_y = y - 1
      while self.is_in_bounds(queen_x, queen_y):
        moves.append((queen_x, queen_y))
        queen_x += 1
        queen_y -= 1

      queen_x = x - 1
      queen_y = y - 1
      while self.is_in_bounds(queen_x, queen_y):
        moves.append((queen_x, queen_y))
        queen_x -= 1
        queen_y -= 1
      return moves

    elif self.is_bishop(self._board[x][y]):
      moves = []
      # diagonal
      queen_x = x + 1
      queen_y = y + 1
      while self.is_in_bounds(queen_x, queen_y):
        moves.append((queen_x, queen_y))
        queen_x += 1
        queen_y += 1

      queen_x = x - 1
      queen_y = y + 1
      while self.is_in_bounds(queen_x, queen_y):
        moves.append((queen_x, queen_y))
        queen_x -= 1
        queen_y += 1

      queen_x = x + 1
      queen_y = y - 1
      while self.is_in_bounds(queen_x, queen_y):
        moves.append((queen_x, queen_y))
        queen_x += 1
        queen_y -= 1

      queen_x = x - 1
      queen_y = y - 1
      while self.is_in_bounds(queen_x, queen_y):
        moves.append((queen_x, queen_y))
        queen_x -= 1
        queen_y -= 1
      return moves

    elif self.is_knight(self._board[x][y]):
      return [(x-1, y+2), (x+1, y+2), (x-2, y+1), (x+2, y+1), (x-2, y-1), (x+2, y-1), (x-1, y-2), (x+1, y-2)]

    elif self.is_rook(self._board[x][y]):
      # vertial/horizontal
      moves = []
      moves += [(queen_x, y) for queen_x in range(x, 8)]
      moves += [(queen_x, y) for queen_x in range(0, x)]
      moves += [(x, queen_x) for queen_x in range(y, 8)]
      moves += [(x, queen_x) for queen_x in range(0, y)]
      return moves

    elif self.is_pawn(self._board[x][y]):
      if self.is_white(self._board[x][y]):
        if x == 7:
          moves = [(x, y-1), (x, y-2)]
        else:
          moves = [(x, y-1)]

        if self.is_black(self._board[x-1][y-1]):
          moves.append((x-1, y-1))
        if self.is_black(self._board[x+1][y-1]):
          moves.append((x+1, y-1))

      if self.is_black(self._board[x][y]):
        if x == 1:
          moves = [(x, y+1), (x, y+2)]
        else:
          moves = [(x, y+1)]

        if self.is_white(self._board[x-1][y+1]):
          moves.append((x-1, y+1))
        if self.is_white(self._board[x+1][y+1]):
          moves.append((x+1, y+1))

      return moves

  def to_human_display(self):
    s = ''
    for r in self._board:
      for c in r:
        if c:
          s += ' ' + c + ' '
        else:
          s += ' . '
      s += '\n'
    return s

  def shuffle(self):
    for a_x in xrange(8):
      for a_y in xrange(8):
        piece_a = self.get_piece(a_x, a_y)

        b_x = random.randint(0, 7)
        b_y = random.randint(0, 7)
        piece_b = self.get_piece(b_x, b_y)

        self.set_piece(piece_a, b_x, b_y)
        self.set_piece(piece_b, a_x, a_y)

  def is_white(self, piece):
    if piece in ["♔", "♕", "♗", "♘", "♖", "♙"]:
      return True
    else:
      return False

  def is_black(self, piece):
    if piece in ["♚", "♛", "♝", "♞", "♜", "♟"]:
      return True
    else:
      return False

  def is_king(self, piece):
    return True if piece == '♔' or piece == '♚' else False

  def is_queen(self, piece):
    return True if piece == '♕' or piece == '♛' else False

  def is_pawn(self, piece):
    return True if piece == '♙' or piece == '♟' else False

  def is_bishop(self, piece):
    return True if piece == '♗' or piece == '♝' else False

  def is_rook(self, piece):
    return True if piece == '♖' or piece == '♜' else False

  def is_knight(self, piece):
    return True if piece == '♘' or piece == '♞' else False


def main():
  board = Board()

  option = ''
  while option != 'q':
    print '(N)ew board'
    print '(S)huffle board'
    print '(D)isplay board'
    print '(A)vailable moves'
    print '(Q)uit'

    option = raw_input('Your choice: ')
    option = option.lower()

    if option == 'n':
      board = Board()
    elif option == 's':
      board.shuffle()
    elif option == 'd':
      print board.to_human_display()
    elif option == 'a':
      while True:
        x = raw_input('Row (0-7): ')
        y = raw_input('Column (0-7): ')
        try:
          x = int(x)
          y = int(y)
        except:
          print 'Invalid location'
          continue

        if not board.is_in_bounds(x, y):
          print 'Invalid location'
          continue

        print board.get_moves(x, y)
        break
    elif option == 'q':
      break


if __name__ == '__main__':
  main()

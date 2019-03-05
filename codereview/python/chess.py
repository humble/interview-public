import random


class Board(object):
  def __init__(self):
    self._board = []
    for _ in xrange(8):
      self._board.append([None] * 8)

    self._init_pieces()

  def _init_pieces(self):
    raise NotImplementedError

  def is_in_bounds(self, x, y):
    return 0 <= x < 8 and 0 <= y < 8

  def get_piece(self, x, y):
    return self._board[x][y]

  def set_piece(self, piece, x, y):
    self._board[x][y] = piece

  def get_moves(self, x, y):
    raise NotImplementedError

  def to_human_display(self):
    raise NotImplementedError

  def shuffle(self):
    for a_x in xrange(8):
      for a_y in xrange(8):
        piece_a = self.get_piece(a_x, a_y)

        b_x = random.randint(0, 7)
        b_y = random.randint(0, 7)
        piece_b = self.get_piece(b_x, b_y)

        self.set_piece(piece_a, b_x, b_y)
        self.set_piece(piece_b, a_x, a_y)


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

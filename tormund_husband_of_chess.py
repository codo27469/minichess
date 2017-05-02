#!/usr/bin/env python3

import sys


class State:
    '''White is capital letters, black is lowercase. White moves first'''
    NUM_ROW = 6
    NUM_COL = 5

    def __init__(self, board=None, move=None, turn=None):
        if board is None:
            self.board = []
            self.board.append(['k', 'q', 'b', 'n', 'r'])
            self.board.append(['.', '.', 'p', 'p', 'p'])
            self.board.append(['.', '.', '.', '.', '.'])
            self.board.append(['p', 'p', 'P', '.', '.'])
            self.board.append(['.', '.', '.', '.', 'P'])
            self.board.append(['R', 'N', 'B', 'Q', 'K'])
            self.move = 'W'
            self.turn = 1
        else:
            self.board = board
        self.move = 'W' if move is None else move
        self.turn = 1 if turn is None else turn

    def print_state(self, verbose=False):
        print(self.move, self.turn)  # print who's move/ what turn
        r_num = 6
        for row in range(self.NUM_ROW):
            for col in range(self.NUM_COL):
                print(self.board[row][col], end=' ')
            if verbose:
                print('{} '.format(r_num))  # print what rows
                r_num -= 1
            else:
                print('')
        if verbose:
            [print(chr(ord('a') + i), end=' ') for i in range(0, 5)]
            print('')

    def get_pieces(self):
        pieces = []
        for row in range(self.NUM_ROW):
            for col in range(self.NUM_COL):
                val = self.board[row][col]
                if str.isupper(val) and self.move == 'W':
                    pieces.append(Square(row, col, val))
                elif str.islower(val) and self.move == 'B':
                    pieces.append(Square(row, col, val))
        return pieces

    def scan(self, piece, dr, dc, stop_short, capture):
        row = piece.row
        col = piece.col
        moves = []
        while True:  # emulate do-until loop
            row = row + dr
            col = col + dc
            if row < 0 or row >= self.NUM_ROW:
                break
            if col < 0 or col >= self.NUM_COL:
                break
            val = self.board[row][col]
            if val != '.':  # there is a piece where we're trying to move
                if str.isupper(val) and self.move == 'W':
                    break
                if str.islower(val) and self.move == 'B':
                    break
                if str(capture) == 'false':
                    break
                stop_short = True
            elif str(capture) == 'only':
                break
            move = Move(piece, Square(row, col, val))
            moves.append(move)
            if stop_short is True:
                break
        return moves

    def sym_scan(self, piece, dr, dc, stop_short, capture):
        moves = []
        for i in range(0, 4):
            moves += self.scan(piece, dr, dc, stop_short, capture)
            # exchange dr and dc
            dr, dc = dc, dr
            # negate dr
            dr = dr * -1
        return moves

    def generate_moves_for_piece(self, piece):
        moves = []
        if piece.name == 'pawn':
            dr = 1
            if self.move == 'W':
                dr = -1
            moves += self.scan(piece, dr, -1, True, 'only')
            moves += self.scan(piece, dr, 1, True, 'only')
            moves += self.scan(piece, dr, 0, True, 'false')
        elif piece.name == 'knight':
            moves += self.sym_scan(piece, -1, 2, True, 'true')
            moves += self.sym_scan(piece, 1, 2, True, 'true')
        elif piece.name == 'rook' or piece.name == 'bishop':
            stop_short = True if piece.name == 'bishop' else False
            capture = 'true' if piece.name == 'rook' else 'false'
            moves += self.sym_scan(piece, 1, 0, stop_short, capture)
            if piece.name == 'bishop':
                stop_short = False
                capture = 'true'
                moves += self.sym_scan(piece, 1, 1, stop_short, capture)
        elif piece.name == 'king' or piece.name == 'queen':  # King or Queen
            stop_short = True if piece.name == 'king' else False
            moves += self.sym_scan(piece, 0, 1, stop_short, 'true')
            moves += self.sym_scan(piece, 1, 1, stop_short, 'true')
        return moves

    def generate_all_moves(self):
        moves = []
        move_strings = []
        pieces = self.get_pieces()
        for piece in pieces:
            moves += self.generate_moves_for_piece(piece)
        move_strings += [m.to_string() for m in moves]
        if move_strings:
            move_strings.sort()
        for m in move_strings:
            print(m)

    def apply_move(self, move):
        pass


class Square:
    def __init__(self, row, col, val):
        assert row <= 5 and row >= 0
        assert col <= 4 and col >= 0
        self.row = row
        self.col = col
        self.val = val
        if val == 'p' or val == 'P':
            self.name = 'pawn'
        elif val == 'n' or val == 'N':
            self.name = 'knight'
        elif val == 'b' or val == 'B':
            self.name = 'bishop'
        elif val == 'r' or val == 'R':
            self.name = 'rook'
        elif val == 'q' or val == 'Q':
            self.name = 'queen'
        elif val == 'k' or val == 'K':
            self.name = 'king'

    def to_string(self):
        return '{} (row: {}, col: {})'.format(self.val, self.row, self.col)

    def rank(self):
        return '{}{}'.format(chr(ord('a') + self.col), 6 - self.row)

    def print_square(self):
        print(self.to_string())


class Move:
    def __init__(self, from_square, to_square):
        self.to_square = to_square
        self.from_square = from_square

    def to_string(self):
        return '{}-{}'.format(self.from_square.rank(), self.to_square.rank())

    def print_move(self, verbose=False):
        if verbose:
            print('{} -> {}'.format(
                self.from_square.to_string(), self.to_square.to_string()
            ))
        else:
            print(self.to_string())


if __name__ == '__main__':
    if '-r' in sys.argv:
        # read from stdin
        input_lines = sys.stdin.readlines()
        turn = input_lines[0].split()[0]
        move = input_lines[0].split()[1]
        board_lines = input_lines[1:]
        board = [[val for val in line.strip()] for line in board_lines]
        state = State(board, move, turn)
    else:
        state = State()
    # state.print_state(verbose=True)
    state.generate_all_moves()

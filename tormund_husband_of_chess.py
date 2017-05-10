#!/usr/bin/env python3

import random
import sys


class State:
    '''White is capital letters, black is lowercase. White moves first'''
    NUM_ROW = 6
    NUM_COL = 5
    BLUE = '\033[94m'
    ENDC = '\033[0m'

    def __init__(self, board=None, move=None, turn=None):
        if board is None:
            self.board = []
            self.board.append(['k', 'q', 'b', 'n', 'r'])
            self.board.append(['p', 'p', 'p', 'p', 'p'])
            self.board.append(['.', '.', '.', '.', '.'])
            self.board.append(['.', '.', '.', '.', '.'])
            self.board.append(['P', 'P', 'P', 'P', 'P'])
            self.board.append(['R', 'N', 'B', 'Q', 'K'])
            self.move = 'W'
            self.turn = 1
        else:
            self.board = board
        self.move = 'W' if move is None else move
        self.turn = 1 if turn is None else turn
        self.moves = self.generate_all_moves()
        self.moves_strings = [m.to_string() for m in self.moves]

    def print_state(self, verbose=False):
        print(self.move, self.turn)  # print who's move/ what turn
        r_num = 6
        for row in range(self.NUM_ROW):
            for col in range(self.NUM_COL):
                print(self.board[row][col], end=' ')
            if verbose:
                print(self.BLUE + '{} '.format(r_num) + self.ENDC)
                r_num -= 1
            else:
                print('')
        if verbose:
            for i in range(0, 5):
                print(self.BLUE + chr(ord('a') + i) + self.ENDC, end=' ')
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
        pieces = self.get_pieces()
        for piece in pieces:
            moves += self.generate_moves_for_piece(piece)
        return moves

    def apply_move(self, move):
        piece = self.board[move.from_square.row][move.from_square.col]
        new_board = [[val for val in row] for row in self.board]
        new_board[move.from_square.row][move.from_square.col] = '.'
        new_board[move.to_square.row][move.to_square.col] = piece
        new_move = 'W' if self.move == 'B' else 'B'
        new_turn = self.turn
        new_turn += 1 if new_move == 'W' else 0
        return State(new_board, new_move, new_turn)

    def send_move(self, move):
        def get_square_from_rank(rank):
            assert len(rank) == 2
            col = ord(rank[0]) - ord('a')
            row = self.NUM_ROW - int(rank[1])
            val = self.board[row][col]
            return Square(row, col, val)
        from_rank = move.split('-')[0]
        to_rank = move.split('-')[1]
        from_square = get_square_from_rank(from_rank)
        to_square = get_square_from_rank(to_rank)
        move = Move(from_square, to_square)
        if move.to_string() in self.moves_strings:
            return self.apply_move(move)
        else:
            raise Exception('invalid move')

    def is_game_over(self):
        if self.turn > 40:
            return True
        if self.moves.count == 0:
            return True
        b_king = False
        w_king = False
        for row in range(self.NUM_ROW):
            for col in range(self.NUM_COL):
                if self.board[row][col] == 'k':
                    b_king = True
                elif self.board[row][col] == 'K':
                    w_king = True
        if b_king is False or w_king is False:
            return True
        return False

    def value_of_state(self):
        b_score = 0
        w_score = 0
        for row in range(self.NUM_ROW):
            for col in range(self.NUM_COL):
                val = self.board[row][col]
                if val == 'p':
                    b_score += 100
                elif val == 'P':
                    w_score += 100
                elif val == 'b' or val == 'n':
                    b_score += 300
                elif val == 'B' or val == 'N':
                    w_score += 300
                elif val == 'r':
                    b_score += 500
                elif val == 'R':
                    w_score += 500
                elif val == 'q':
                    b_score += 900
                elif val == 'Q':
                    w_score += 900
        if self.move == 'W':
            return w_score - b_score
        else:
            return b_score - w_score


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


def depth_limited_negamax(state, depth):
    if state.is_game_over() or depth <= 0:
        return state.value_of_state()
    moves = state.generate_all_moves()
    m = moves.pop(random.randint(0, len(moves) - 1))
    p_state = state.apply_move(m)
    p_val = -(depth_limited_negamax(p_state, depth - 1))
    for mv in moves:
        p_state = state.apply_move(mv)
        val = -(depth_limited_negamax(p_state, depth - 1))
        p_val = max(p_val, val)
    return p_val


def parse_input():
    # read from stdin
    input_lines = sys.stdin.readlines()
    turn = input_lines[0].split()[0]
    move = input_lines[0].split()[1]
    board_lines = input_lines[1:]
    board = [[val for val in line.strip()] for line in board_lines]
    state = State(board, move, turn)
    return state


def human_player(state):
    print("you are player W")
    while state.is_game_over() is False:
        print('________________________')
        state.print_state(verbose=True)
        if state.move == 'W':
            move = input("your move: ")
            try:
                state = state.send_move(move)
            except:
                print('invalid move, try again')
                continue
        else:
            best_score = 10000
            best_move = state.moves[0]
            for move in state.moves[1:]:
                potential_state = state.apply_move(move)
                d = 3  # for now
                s = depth_limited_negamax(potential_state, d)
                if s < best_score:
                    best_score = s
                    best_move = move
            print("computer's move: {} (score: {})".format(
                best_move.to_string(), best_score)
            )
            state = state.apply_move(best_move)
    print('game over')
    loser = state.move  # the winning move went last, changes whos on turn
    winner = 'B' if loser == 'W' else 'W'
    print('{} loses, {} wins'.format(loser, winner))


if __name__ == '__main__':
    if '-r' in sys.argv:
        state = parse_input()
    else:
        state = State()
    if '-p' in sys.argv:
        # play against human player
        human_player(state)
    else:
        # print generated moves for state
        for m in state.generate_all_moves():
            print(m.to_string())

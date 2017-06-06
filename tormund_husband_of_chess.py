#!/usr/bin/env python3

import random
import sys
import time


class State:
    '''White is capital letters, black is lowercase. White moves first'''
    NUM_ROW = 6
    NUM_COL = 5
    BLUE = '\033[94m'
    ENDC = '\033[0m'

    def __init__(self, board=None, move=None, turn=None):
        # basic state
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

        # used for state evaluation
        self.update_pieces_list()
        self.piece_values = {
            'k': 200, 'q': 9, 'r': 5, 'b': 3, 'n': 3, 'p': 1,
            'K': 200, 'Q': 9, 'R': 5, 'B': 3, 'N': 3, 'P': 1
        }
        self.moves = self.generate_all_moves()
        self.moves_strings = [m.to_string() for m in self.moves]

        self.previous_states = []

        # used for iterative deepening
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # the idea of using these variables and the time module came from
        # this repo: https://github.com/sorgtyler/minichess
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.time_spent = 0
        self.time_counter = 0
        self.time_limit = 0  # per move

    def update_pieces_list(self):
        ''' Update the list of black + white pieces for the current board'''
        self.black_pieces = []
        self.white_pieces = []
        for row in range(self.NUM_ROW):
            for col in range(self.NUM_COL):
                piece = self.board[row][col]
                if piece.isupper():
                    self.white_pieces.append(piece)
                elif piece.islower():
                    self.black_pieces.append(piece)

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
        from_square = move.from_square
        to_square = move.to_square
        piece = self.board[from_square.row][from_square.col]
        dest = self.board[to_square.row][to_square.col]
        # save move + pieces for undo
        self.previous_states.append((move, piece, dest))
        # move the piece to the dest
        self.board[from_square.row][from_square.col] = '.'
        self.board[to_square.row][to_square.col] = piece
        # update piece list if something was taken
        if dest != '.' and dest.islower():  # black piece
            self.black_pieces.remove(dest)
        elif dest != '.' and dest.isupper():  # white piece
            self.white_pieces.remove(dest)
        # handle pawn promotion
        if piece == 'p' and to_square.row == self.NUM_ROW - 1:
            # promote black
            self.board[to_square.row][to_square.col] = 'q'
            self.black_pieces.remove('p')
            self.black_pieces.append('q')
        elif piece == 'P' and to_square.row == 0:
            # promote white
            self.board[to_square.row][to_square.col] = 'Q'
            self.white_pieces.remove('P')
            self.white_pieces.append('Q')
        # change turns
        self.move = 'B' if self.move == 'W' else 'W'
        self.turn += 1 if self.move == 'W' else 0

    def undo_move(self):
        if len(self.previous_states) > 0:
            info = self.previous_states.pop()
            move = info[0]
            piece = info[1]
            dest = info[2]
            from_square = move.from_square
            to_square = move.to_square
            # unmake move
            self.board[from_square.row][from_square.col] = piece
            self.board[to_square.row][to_square.col] = dest
            # put pieces back in their list if they were taken
            if dest != '.' and dest.islower():
                self.black_pieces.append(dest)
            elif dest != '.' and dest.isupper():
                self.white_pieces.append(dest)
            # de-promote pawns
            if piece == 'p' and to_square.row == self.NUM_ROW - 1:
                self.black_pieces.append('p')
                self.black_pieces.remove('q')
            elif piece == 'P' and to_square.row == 0:
                self.white_pieces.append('P')
                self.white_pieces.remove('Q')
            self.turn -= 1 if self.move == 'W' else 0
            self.move = 'B' if self.move == 'W' else 'W'

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
        m_strings = [m.to_string() for m in self.generate_all_moves()]
        if move.to_string() in m_strings:
            return self.apply_move(move)
        else:
            raise Exception('invalid move')

    def winner(self):
        b_king = False
        w_king = False
        for row in range(self.NUM_ROW):
            for col in range(self.NUM_COL):
                if self.board[row][col] == 'k':
                    b_king = True
                elif self.board[row][col] == 'K':
                    w_king = True
        if b_king and w_king and self.turn <= 40:
            return '?'  # game is still going
        elif b_king and w_king and self.turn > 40:
            return '='  # game has drawn
        elif not b_king and w_king:
            return 'W'  # white wins
        elif b_king and not w_king:
            return 'B'  # black wins
        elif not b_king and not w_king:
            return '='

    def evaluate(self):
        player = 1 if self.move == 'W' else -1
        w_score = sum([self.piece_values[piece] for piece in self.white_pieces])
        b_score = sum([self.piece_values[piece] for piece in self.black_pieces])
        return (w_score - b_score) * player

    def better_evaluate(self):
        player = 1 if self.move == 'W' else -1
        w_score = sum([self.piece_values[piece] for piece in self.white_pieces])
        b_score = sum([self.piece_values[piece] for piece in self.black_pieces])
        material_score = ((w_score - b_score) * player) * 100
        dev_w = dev_b = 0  # how advanced are the pieces?
        for row in range(self.NUM_ROW):
            for col in range(self.NUM_COL):
                piece = self.board[row][col]
                if piece == 'P':
                    dev_w += self.NUM_ROW - row
                elif piece == 'p':
                    dev_b += row
                elif piece in ['N', 'B', 'R', 'Q'] and row != self.NUM_ROW - 1:
                    dev_w += 5
                elif piece in ['n', 'b', 'r', 'q'] and row != 0:
                    dev_b += 5
        developed_score = (dev_w * player) if self.move == 'W' else (dev_b * player)
        return material_score + developed_score

    def sorted_moves(self):
        moves = self.generate_all_moves()
        random.shuffle(moves)
        evaluated_moves = []
        for move in moves:
            self.apply_move(move)
            score = self.better_evaluate()
            self.undo_move()
            evaluated_moves.append((score, move))
        sorted_moves = sorted(evaluated_moves, key=lambda x: x[0])
        return [move[1] for move in sorted_moves]

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # idea of how to apply negamax/alpha beta search to a given state came
    # this repo: https://github.com/sorgtyler/minichess
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def negamax(self, depth):
        # check the time for iterative deepening
        self.time_counter += 1
        if self.time_counter > 1000:
            self.time_counter = 0
            self.time_spent = int(time.time() * 1000)
        if self.time_spent > self.time_limit:
            return 0
        if depth <= 0 or self.winner() != '?':
            return self.evaluate()
        score = float('-inf')
        moves = self.sorted_moves()
        for move in moves:
            self.apply_move(move)
            score = max(score, -self.negamax(depth - 1))
            self.undo_move()
        return score

    def apply_negamax(self, depth, duration):
        # iterative deepening
        self.time_spent = int(time.time() * 1000)
        self.time_limit = int(self.time_spent + duration)
        self.time_counter = 0

        moves = self.sorted_moves()
        best_move = ''
        for d in range(1, depth + 1):
            score = float('-inf')
            candidate = ''
            for move in moves:
                self.apply_move(move)
                temp = -self.negamax(d - 1)
                self.undo_move()
                if temp > score:
                    candidate = move
                    score = temp
            if self.time_spent > self.time_limit:
                break
            best_move = candidate
        if best_move == '':
            best_move = moves[0]
            print('ran out of time, making best guess for move')
        return best_move

    def alpha_beta(self, depth, alpha, beta):
        # iterative deepening
        self.time_counter += 1
        if self.time_counter > 1000:
            self.time_counter = 0
            self.time_spent = int(time.time() * 1000)
        if self.time_spent > self.time_limit:
            return 0
        if depth <= 0 or self.winner() != '?':
            return self.better_evaluate()
        score = float('-inf')
        for move in self.sorted_moves():
            self.apply_move(move)
            score = max(score, -self.alpha_beta(depth - 1, -beta, -alpha))
            self.undo_move()
            alpha = max(alpha, score)
            if alpha >= beta:
                break
        return score

    def apply_alpha_beta(self, depth, duration):
        self.time_spent = int(time.time() * 1000)
        self.time_limit = int(self.time_spent + duration)
        self.time_counter = 0
        best_move = ''
        moves = self.sorted_moves()
        for d in range(1, depth + 1):
            alpha = float('-inf')
            beta = float('inf')
            candidate = ''
            for move in moves:
                self.apply_move(move)
                temp = -self.alpha_beta(d - 1, -beta, -alpha)
                self.undo_move()
                if temp > alpha:
                    candidate = move
                    alpha = temp
            if self.time_spent > self.time_limit:
                print('ran out of time at depth: {}'.format(d))
                break
            best_move = candidate
        if best_move == '':
            best_move = moves[0]
            print('ran out of time, making best guess for move')
        return best_move


class Square:
    PIECE_NAMES = {
        'p': 'pawn', 'n': 'knight', 'b': 'bishop', 'r': 'rook', 'q': 'queen',
        'P': 'pawn', 'N': 'knight', 'B': 'bishop', 'R': 'rook', 'Q': 'queen',
        'k': 'king', 'K': 'king', '.': 'empty'
    }

    def __init__(self, row, col, val):
        assert row <= 5 and row >= 0
        assert col <= 4 and col >= 0
        self.row = row
        self.col = col
        self.val = val
        self.name = self.PIECE_NAMES[val]

    def __eq__(self, other):
        if self.row == other.row and self.col == other.col:
            if self.val == other.val:
                return True
        return False

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
    print("you are player W, tormund (husband of chess) is B")
    while state.winner() == '?':
        print('________________________')
        state.print_state(verbose=True)
        if state.move == 'W':
            move = input("your move: ")
            try:
                if move == 'moves':
                    [print(m.to_string()) for m in state.generate_all_moves()]
                else:
                    state.send_move(move)
            except:
                print('invalid move, try again')
                continue
        else:
            if '--alpha-beta' in sys.argv:
                print('alpha-beta')
                move = state.apply_alpha_beta(8, 3000)
            elif '--negamax' in sys.argv:
                move = state.apply_negamax(4, 3000)
            else:  # only look at the states of the next move, ie easy-2-beat
                move = state.sorted_moves()[0]
            print('making move {}'.format(move.to_string()))
            state.apply_move(move)
    print('game over')
    loser = state.move  # the winning move went last, changes whos on turn
    winner = 'B' if loser == 'W' else 'W'
    print('{} loses, {} wins'.format(loser, winner))
    state.print_state(verbose=True)


if __name__ == '__main__':
    if '-r' in sys.argv:
        state = parse_input()
    else:
        state = State()
    if '-p' in sys.argv:
        # play against human player
        human_player(state)
    else:
        pass
        # print generated moves for state
        for m in state.generate_all_moves():
            print(m.to_string())

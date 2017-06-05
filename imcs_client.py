#!/usr/bin/env python3

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This script is heavily inspired by Max Goodman's 'skirmish.py'.
# https://github.com/chromakode/skirmish/tree/master

# The functions that log into, and interact with, the imcs server are taken
# from that source. I used only what I needed to send moves to and from my
# player and modified some things accordingly. The main script is heavily
# simplified to only offer or accept games from a given user on imcs.
# ~Thank you Max
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import socket
import sys
from tormund_husband_of_chess import State


class Conversation:
    def __init__(self, in_stream, out_stream):
        self.in_stream = in_stream
        self.out_stream = out_stream

    def _parse_msg(self, resp):
        return resp.strip(' \r\n').split(' ', 2)

    def receive_line(self):
        return self.in_stream.readline()

    def receive_until(self, codes):
        msg = resp = code = linelist = None
        lines = ''
        while True:
            line = self.receive_line()
            if line:
                if not str(line).isspace():
                    lines += line
            else:
                return None, None, None, None
            try:
                code, msg, resp = self._parse_msg(line)
            except:
                code = self._parse_msg(line)[0]
            if code in codes:
                linelist = lines.splitlines()
                return code, msg, resp, linelist

    def send_line(self, line):
        self.out_stream.write(line+'\r\n')
        self.out_stream.flush()

    def expect(self, codes):
        line = self.receive_line()
        code, msg, resp = self._parse_msg(line)
        assert code in codes
        return code, msg, resp


class Client:
    def __init__(self, server, port, uname, pswd):
        self.server = server
        self.port = int(port)
        self.user = uname
        self.pswd = pswd
        self.send_line_ending = '\r\n'
        self.set_client()

    def set_client(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.server, self.port))
        self.stream = sock.makefile('rw')
        self.io = Conversation(self.stream, self.stream)
        self.expect_version(['2.3', '2.4', '2.5'])

    def expect_version(self, versions):
        code, msg, resp = self.io.expect(['100'])
        assert msg == 'imcs'
        assert resp in versions

    def login(self):
        self.io.send_line('me {} {}'.format(self.user, self.pswd))
        code, msg, resp = self.io.expect(['201', '401'])
        assert code == '201'
        print('successfully logged in as {}'.format(self.user))

    def list_games(self):
        self.io.send_line('list')
        self.io.expect(['211'])
        code, msg, resp, text = self.io.receive_until(['.'])
        game_lines = text[:-1]
        open_games = []
        for game in game_lines:
            game_id = game.split()[0]
            offering_player = game.split()[1]
            game_state = game.split()[-1]
            if game_state == '[offer]':  # game is open
                open_games.append((game_id, offering_player))
        return open_games

    def logout(self):
        self.io.send_line('quit')
        print('Goodbye')
        self.stream.close()

    def accept(self, id):
        self.io.send_line('accept {}'.format(id))
        code, msg, resp = self.io.expect(['105', '106', '408'])
        if code in ['105', '106']:
            if code == '105':
                print('you are color W')
            else:
                print('you are color B')
            print('accepted game: {}'.format(id))

    def offer(self, color):
        self.io.send_line('offer {}'.format(color))
        code, msg, resp = self.io.expect(['103', '107', '108'])
        print('offered new game as color {} (id: {})'.format(color, msg))
        # wait for acceptance
        self.io.expect(['102', '105', '106'])
        print('offer accepted!')

    def get_board(self):
        code, msg, resp, text = self.io.receive_until(['?', '='])
        if code[0] == '=':  # the game has ended
            if '= draw' in text:
                self.winner = 'draw game'
            else:
                self.winner = msg
            return None
        if str(text[0]).startswith('!'):  # first line is oppenent's last move
            text = text[1:]
        move = text[0].split()[1]
        turn = int(text[0].split()[0])
        board_lines = text[1:7]
        board = [[val for val in line.strip()] for line in board_lines]
        return State(board, move, turn)

    def send_move(self, move):
        self.io.send_line('! {}'.format(move))


if __name__ == '__main__':
    client = Client('imcs.svcs.cs.pdx.edu', 3589, 'tormund', 'amarant')
    client.login()
    if '-o' in sys.argv:
        # offer and play a game
        client.offer('')
        state = client.get_board()
        while state is not None:
            m = state.apply_alpha_beta(8, 7000)
            print('making move: {}'.format(m.to_string()))
            client.send_move(m.to_string())
            state = client.get_board()
        print(client.winner)
    elif '-p' in sys.argv:
        user = sys.argv[2]  # the user you want to play against
        games = client.list_games()
        for g in games:
            if g[1] == user:
                client.accept(g[0])
                state = client.get_board()
                while state is not None:
                    m = state.apply_alpha_beta(8, 7000)
                    print('making move: {}'.format(m.to_string()))
                    client.send_move(m.to_string())
                    state = client.get_board()
                print(client.winner)
                break
    client.logout()

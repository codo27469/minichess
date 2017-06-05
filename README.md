# minichess
A minichess player for CS442 at PSU. Implements negamax search with alpha-beta pruning and iterative deepening.

// accept a game from the player ‘TacklingDummy’ on imcs
$ python3 imcs_client.py <user> <password> -p TacklingDummy 
    
// offer a game as <user> on imcs
$ python3 imcs_client.py <user> <password> -o       

// play against ‘tormund' using alpha-beta
$ python3 tormund_husband_of_chess.py -p --alpha-beta 

// display white’s opening moves
$ python3 tormund_husband_of_chess.py
            
// display moves for board position described in random-39.in
$ cat genmoves-tests/random-39.in | python3 tormund_husband_of_chess.py -r

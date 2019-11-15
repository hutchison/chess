#!/usr/bin/env python3

import sys
from chess_stuff import (
    read_games,
    find_puzzles,
    print_puzzles,
)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("usage: parse_games.py games.pgn mate_in_nr [solutions? (yes)]")
        sys.exit(1)

    pgn_file = sys.argv[1]
    nr = int(sys.argv[2])
    if len(sys.argv) == 4:
        solutions = sys.argv[3] == 'yes'
    else:
        solutions = False

    if solutions:
        print("Computing solutions", file=sys.stderr)

    games = read_games(pgn_file)
    puzzles = find_puzzles(games, nr)
    print_puzzles(puzzles, nr, solution=solutions)

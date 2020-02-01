#!/usr/bin/env python3

import argparse
import sys

from chess_stuff import (
    read_games,
    find_puzzles,
    tex_puzzles,
    tex_solutions,
)

def main(input_file, nr, output_file, solutions=False):
    if solutions:
        print("Printing solutions", file=sys.stderr)

    games = read_games(input_file)
    puzzles = find_puzzles(games, nr)
    if solutions:
        t = tex_solutions(puzzles, nr)
    else:
        t = tex_puzzles(puzzles, nr)

    with open(output_file, 'w') as f:
        f.write(t)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate mate puzzles from a PGN file.'
    )

    parser.add_argument('input_file')
    parser.add_argument('nr', type=int, help='mate in ...?')
    parser.add_argument('-s', '--solutions', action='store_true')
    parser.add_argument('output_file')

    args = parser.parse_args()

    main(args.input_file, args.nr, args.output_file, args.solutions)

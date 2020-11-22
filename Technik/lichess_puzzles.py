#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
import sys
from operator import itemgetter
from pathlib import Path


lichess_url = 'https://lichess.org/training/'
l = 'LichessPuzzle('
script_end = ')})</script>'
puzzles_filename = 'puzzles.json'
sleep_duration = 0.25

def get_puzzle(i: int):
    r = requests.get(lichess_url + str(i))
    s = r.text.find(l)
    e = r.text.find(script_end, s)

    j = json.loads(r.text[s+len(l):e])

    p = dict()
    p = j['data']['puzzle']
    p['fen'] = j['data']['game']['treeParts'][-1]['fen']

    return p


def read_puzzles(input_filename: str):
    with open(input_filename, 'r') as f:
        puzzles = json.load(f)

    return puzzles


def puzzle_already_loaded(puzzles, i):
    return i in puzzles


def main(start: int, end: int):
    if Path(puzzles_filename).is_file():
        puzzles = read_puzzles(puzzles_filename)
    else:
        puzzles = {}

    for i in range(start, end):
        if not puzzle_already_loaded(puzzles, str(i)):
            try:
                puzzles[i] = get_puzzle(i)
                time.sleep(sleep_duration)
                print(f'{i} wird heruntergeladen')
            except Exception as inst:
                print(f'Problem bei {i}')
                print(inst)
        else:
            print(f'{i} wurde schon geladen')

    with open(puzzles_filename, 'w') as f:
        json.dump(puzzles, f, indent=2)


if __name__ == '__main__':
    if len(sys.argv) == 3:
        start = int(sys.argv[1])
        end = int(sys.argv[2])
        main(start, end)

    puzzle_list = list(read_puzzles(puzzles_filename).values())
    puzzles = sorted(puzzle_list, key=itemgetter('rating'))
    for p in puzzles:
        print(f"https://lichess.org/training/{p['id']}\t{p['rating']}\t{p['vote']}")

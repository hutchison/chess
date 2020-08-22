import requests
import json
import time
import sys
from operator import itemgetter


lichess_url = 'https://lichess.org/training/'
l = 'lichess.puzzle = '
script_end = '</script>'
puzzles_filename = 'puzzles.json'

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
    for p in puzzles:
        if p['id'] == i:
            return True
    else:
        return False


def sort_puzzles(puzzles, key: str):
    return [
        (p['id'], p[key])
        for p in sorted(puzzles, key=itemgetter(key))
    ]


def main(start: int, end: int):
    puzzles = read_puzzles(puzzles_filename)

    for i in range(start, end):
        if not puzzle_already_loaded(puzzles, i):
            try:
                p = get_puzzle(i)
                puzzles.append(p)
                time.sleep(1)
                print(f'{i} wird heruntergeladen')
            except:
                print(f'Problem bei {i}')
        else:
            print(f'{i} wurde schon geladen')

    with open(puzzles_filename, 'w') as f:
        json.dump(puzzles, f, indent=2)


if __name__ == '__main__':
    if len(sys.argv) == 3:
        start = int(sys.argv[1])
        end = int(sys.argv[2])
        main(start, end)

    puzzles = sort_puzzles(read_puzzles(puzzles_filename), 'rating')
    for i, rating in puzzles:
        print(f'{i}\t{rating}')

from statistics import mean, stdev, median
from humanize import precisedelta
import sys
from chess_stuff import time_duration, read_games


def describe(data, f=lambda x: x):
    print('min:', f(min(data)), sep='\t')
    print('median:', f(median(data)), sep='\t')
    mu = mean(data)
    print('mean:', f(mu), sep='\t')
    print('stdev:', f(stdev(data, mu)), sep='\t')
    print('max:', f(max(data)), sep='\t')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("I need a pgn-file.")
        sys.exit(1)

    games = read_games(sys.argv[1])

    for game in games:
        game.duration = time_duration(game)
        game.plys = game.end().ply()

    for game in sorted(games, key=lambda g: g.duration):
        print(
            f'{game.headers["White"]} vs. {game.headers["Black"]}',
            precisedelta(game.duration),
            game.plys,
            round(game.duration/game.plys, 2),
            sep='\t',
        )

    print('durations stats')
    durations = [game.duration for game in games]
    describe(durations, f=precisedelta)

    print('ply stats')
    plys = [game.plys for game in games]
    describe(plys)
    print('d/ply:', sum(durations) / sum(plys))

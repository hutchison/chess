import chess
import chess.pgn
import sys
from textwrap import dedent

def read_games(pgn_file):
    with open(pgn_file) as pgn:
        games = []

        game = chess.pgn.read_game(pgn)

        while game is not None:
            if game.headers['Termination'] == 'Normal':
                games.append(game)
            game = chess.pgn.read_game(pgn)

    return games


def mate_in_n(b, n):
    good_moves = {}

    if n > 0:
        for move in b.legal_moves:
            san_move = b.san(move)
            b.push(move)

            if b.is_checkmate():
                # ist es mate in 1?
                # dann ist es ein guter zug
                good_moves[san_move] = {}
            elif b.is_stalemate() or b.is_insufficient_material():
                # ist es ein draw?
                # dann probier den nächsten aus
                pass
            else:
                # Der Gegner versucht alle Züge zu finden,
                # die _nicht_ zu Matt führen:
                for opp_move in b.legal_moves:
                    san_opp_move = b.san(opp_move)
                    b.push(opp_move)
                    if b.is_stalemate() or b.is_insufficient_material():
                        # opp hat einen Remis-Zug gefunden
                        # die letzten beiden Halbzüge führen zum Remis, also
                        # ziehen wir sie zurück und der nächste Halbzug wird
                        # probiert
                        # der letzte Halbzug wird jetzt zurückgezogen und der
                        # davor hinter der for-Schleife
                        b.pop()
                        break
                    else:
                        # kann auf opp_move ein mate in n-1 gefunden werden?
                        continuation = mate_in_n(b, n-1)
                        if continuation:
                            # wenn ja, dann speichern wir das ab:
                            good_moves[san_move] = {san_opp_move: continuation}
                        b.pop()

            b.pop()

        return good_moves


def print_mate_solution(d, indent=0):
    for m in sorted(d):
        print('  ' * indent + m)
        if isinstance(d[m], dict):
            print_mate_solution(d[m], indent+1)
        else:
            print('  ' * (indent+1) + d[m])


def find_mate_moves(node):
    mate_moves = []

    board = node.board()
    for move in board.legal_moves:
        board.push(move)
        if board.is_checkmate():
            mate_moves.append(move)
        board.pop()

    return mate_moves


def find_mate_in(game, nr):
    eval_w = "[%eval #" + str(nr) + "]"
    eval_b = "[%eval #-" + str(nr) + "]"

    puzzles = []

    for node in game.mainline():
        b = node.board()
        if (node.comment == eval_w and b.turn == True
            or node.comment == eval_b and b.turn == False):
            node.url = game.headers["Site"]
            puzzles.append(node)

    return puzzles


def number_of_pieces(board):
    return len(board.piece_map())


def find_puzzles(games, nr):
    puzzles = []
    for i, game in enumerate(games):
        nodes = find_mate_in(game, nr)
        print(
            f"\r{i}/{len(games)}: {len(nodes)}\t{len(puzzles)}",
            file=sys.stderr,
            end="\r"
        )
        puzzles.extend(nodes)

    puzzles = sorted(puzzles, key=lambda p: number_of_pieces(p.board()))

    return puzzles


def print_puzzle(node, solution=False):
    board = node.board()
    move_number = board.fullmove_number
    color = 'w' if board.turn else 'b'
    from_sq = chess.SQUARE_NAMES[node.move.from_square]
    to_sq = chess.SQUARE_NAMES[node.move.to_square]
    last_move = f"{from_sq},{to_sq}"
    inverse = 'false' if board.turn else 'true'

    solution_moves = []
    if solution:
        mate_moves = find_mate_moves(node)
        for move in mate_moves:
            mate_from_sq = chess.SQUARE_NAMES[move.from_square]
            mate_to_sq = chess.SQUARE_NAMES[move.to_square]
            solution_moves.append(f"{mate_from_sq}-{mate_to_sq}")
    solution_moves_str = ','.join(solution_moves)

    puzzle_tex = "\\chesspuzzle{%s}{%s %s}{%s}{%s}{%s}" % (
        board.fen(), move_number, color, inverse, last_move, solution_moves_str
    )
    print(dedent(puzzle_tex))


def print_puzzles(puzzles, nr, solution=False):
    zeile = 0
    spalte = 0
    urls = []

    for node in puzzles:
        if zeile == 0 and spalte == 0:
            print(r"\subsection*{Matt in " + str(nr), end="")
            if solution:
                print(" – Lösung", end="")
            print("}")
            print(r"\begin{tabular}{ccc}")

        print_puzzle(node, solution)
        urls.append(node.url)

        if spalte == 2:
            print(r"\\" + "\n")

            print_urls(urls)
            urls = []

            if zeile == 3:
                print(r"\end{tabular}" + "\n")
                print(r"\pagebreak" + "\n")

            zeile = (zeile+1) % 4
        else:
            print("&")

        spalte = (spalte+1) % 3

    print(r"\\")
    print_urls(urls)
    print(r"\end{tabular}")


def print_urls(urls):
    for i, url in enumerate(urls):
        print(r"\href{", end="")
        print(url, end="")
        print(r"}{\texttt{", end="")
        print(url[8:], end="")
        print("}}")
        if i < len(urls)-1:
            print("& ", end="")
        else:
            print(r"\\")


b = chess.Board(fen='7K/8/8/5kq1/8/8/8/8 b - - 6 62')
m1 = chess.Board(fen='8/7K/5k2/6q1/8/8/8/8 b - - 8 63')
m2 = chess.Board(fen='8/8/8/8/8/5k1K/6p1/4q3 b - - 1 79')

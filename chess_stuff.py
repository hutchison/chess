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


def generate_variations(board, depth):
    if board.is_checkmate():
        print(board.move_stack)
        return True
    elif board.is_stalemate():
        return False
    elif board.is_insufficient_material():
        return False
    elif depth == 0:
        # print(board.move_stack)
        return {}
    else:
        variations = {}
        for move in board.legal_moves:
            move_san = board.san(move)
            board.push(move)
            variations[move_san] = generate_variations(board, depth-1)
            board.pop()
        return variations


def mate_in_n(b, n):
    if n == 0:
        return []
    else:
        good_moves = []
        for move in b.legal_moves:
            b.push(move)
            if b.is_checkmate():
                good_moves.append(b.san(move))
            elif b.is_stalemate() or b.is_insufficient_material():
                pass
            else:
                # Der Gegner versucht alle Züge zu finden, die _nicht_ zu Matt
                # führen:
                opp_moves = list(b.legal_moves)
                for opp_move in opp_moves:
                    board.push(opp_move)

                    if not mate_in_n(b, n-1):
                        break

            b.pop()
        return good_moves


def m(board, depth):
    if board.is_checkmate():
        print(board.move_stack, '→ mate!')
    elif board.is_stalemate() or board.is_insufficient_material():
        print(board.move_stack, '→ remis')
    elif depth == 0:
        print(board.move_stack, '→ no mate')
    else:
        print(list(board.legal_moves))


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


b1 = chess.Board(fen='7K/8/8/5kq1/8/8/8/8 b - - 6 62')

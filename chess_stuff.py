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


def check_opp_turn(board, depth):
    if board.is_stalemate():
        return False
    for opp_move in board.legal_moves:
        board.push(opp_move)
        result = mate_in_n(board, depth-1)
        board.pop()
        if result == False:
            return False
    return True


def mate_in_n(board, depth):
    if board.is_checkmate():
        return True
    if depth == 0:
        return False
    for move in board.legal_moves:
        board.push(move)
        result = check_opp_turn(board, depth)
        if result:
            print(board.move_stack)
            return True
        else:
            board.pop()
    return False


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
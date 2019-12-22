import chess
import chess.pgn
import sys


nl = '\n'
br = r'\\'
pagebreak = r'\pagebreak' + nl


class Puzzle:
    def __init__(self, board, depth, white, black, url):
        self.board = board
        self.depth = depth
        self.white = white
        self.black = black
        self.url = url + '\\#' + str(len(board.move_stack))

        self.solution = mate_in_n(board, depth)
        self.length = number_of_solutions(self.solution)

    def __len__(self):
        # Gibt die Anzahl der Lösungen zurück
        return self.length

    def __abs__(self):
        # Gibt die Anzahl der Figuren auf dem Brett zurück
        return len(self.board.piece_map())

    def __str__(self):
        return f'{self.white} vs. {self.black} {self.url} #{self.depth} {self.length}'

    def __repr__(self):
        return f'<Puzzle {self.white} vs. {self.black} {self.url} #{self.depth} {self.length}>'


def read_games(pgn_file):
    with open(pgn_file) as pgn:
        games = []

        game = chess.pgn.read_game(pgn)
        nr_games = 0

        while game is not None:
            if game.headers['Termination'] == 'Normal':
                games.append(game)
            game = chess.pgn.read_game(pgn)

            nr_games += 1
            print(
                f"\rreading games: {len(games)}/{nr_games}",
                file=sys.stderr,
                end="\r"
            )
        print()

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
                b.pop()
                continue

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
                        if san_move in good_moves:
                            good_moves[san_move].update(
                                {san_opp_move: continuation}
                            )
                        else:
                            good_moves[san_move] = {san_opp_move: continuation}
                    else:
                        # wenn nicht, dann ist anfängliche Zug nicht gut
                        # und wir müssen alles löschen:
                        if san_move in good_moves:
                            del good_moves[san_move]
                        b.pop()
                        break
                    b.pop()

            b.pop()

    return good_moves


def number_of_solutions(mate_tree):
    if len(mate_tree) == 0:
        return 1
    else:
        return sum([number_of_solutions(mate_tree[m]) for m in mate_tree])


def number_of_possible_moves(board, depth):
    legal_moves = list(board.legal_moves)
    if depth == 0:
        return 0
    elif depth == 1:
        return len(legal_moves)
    else:
        m = 0
        for move in legal_moves:
            board.push(move)
            m += number_of_possible_moves(board, depth-1)
            board.pop()
        return m


def print_solution(solution, indent=0):
    for m in sorted(solution):
        print('  ' * indent + m)
        if isinstance(solution[m], dict):
            print_solution(solution[m], indent+1)
        else:
            print('  ' * (indent+1) + solution[m])


def serialize(T, cur_path=None, variations=None):
    if variations is None:
        variations = []
    if cur_path is None:
        cur_path = []

    if len(T) == 0:
        variations.append(cur_path)
    else:
        for move in T:
            serialize(T[move], cur_path + [move], variations)
        return variations


def pgn_variation(variation, turn):
    n = 1
    if turn:
        s = ''
        start = 0
    else:
        s = '1...'
        start = 1

    for h, move in enumerate(variation, start):
        if h % 2 == 0:
            s += f' {n}. {move}'
        else:
            s += f' {move}'
            n += 1

    return s.strip()


def print_variations(solution, turn):
    s = ''

    for variation in serialize(solution):
        s += pgn_variation(variation, turn)
        s += '\n'

    return s


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
            p = Puzzle(
                b,
                nr,
                game.headers['White'],
                game.headers['Black'],
                game.headers['Site'],
            )
            puzzles.append(p)

    return puzzles


def number_of_pieces(board):
    return len(board.piece_map())


def find_puzzles(games, nr, sort_func=abs):
    # sort_func sortiert die Puzzle. abs sortiert nach Anzahl Figuren und len
    # sortiert nach Anzahl der Lösungen.
    puzzles = []
    for i, game in enumerate(games):
        ps = find_mate_in(game, nr)
        print(
            f"\r{i}/{len(games)}: {len(ps)}\t{len(puzzles)}",
            file=sys.stderr,
            end="\r"
        )
        puzzles.extend(ps)

    puzzles = sorted(puzzles, key=sort_func)

    return puzzles


def tex_puzzle(puzzle, solution=False):
    board = puzzle.board
    move_number = board.fullmove_number
    color = 'w' if board.turn else 'b'
    last_move = board.move_stack[-1]
    from_sq = chess.SQUARE_NAMES[last_move.from_square]
    to_sq = chess.SQUARE_NAMES[last_move.to_square]
    last_move_str = f"{from_sq},{to_sq}"
    inverse = 'false' if board.turn else 'true'
    solution_moves = []
    solution_moves_str = ''

    if solution:
        if puzzle.depth == 1:
            for san_move in puzzle.solution:
                move = puzzle.board.push_san(san_move)
                mate_from_sq = chess.SQUARE_NAMES[move.from_square]
                mate_to_sq = chess.SQUARE_NAMES[move.to_square]
                solution_moves.append(f"{mate_from_sq}-{mate_to_sq}")
                puzzle.board.pop()
            solution_moves_str = ','.join(solution_moves)

    puzzle_tex = "\\matepuzzle{%s}{%s %s}{%s}{%s}{%s}" % (
        board.fen(), move_number, color, inverse,
        last_move_str, solution_moves_str
    )
    return puzzle_tex


def tex_puzzles(puzzles, nr, solution=False):
    zeile = 0
    spalte = 0
    urls = []

    t = ''

    """
    Wenn wir ein #1 Rätsel haben, dann können wir die Lösung gleich in das
    Puzzle reinmalen. Ansonsten müssen wir alle Variationen einzeln in SAN
    aufschreiben.
    """

    heading = r'\subsection*{Matt in ' + str(nr)
    if solution:
        heading += ' – Lösung'
    heading += '}' + nl

    if nr == 1:
        table_start = r'\begin{tabular}{ccc}' + nl
        table_end = r'\end{tabular}' + nl

        for puzzle in puzzles:
            if zeile == 0 and spalte == 0:
                t += heading
                t += table_start

            puzzle_str = tex_puzzle(puzzle, solution)
            t += puzzle_str + nl

            urls.append(puzzle.url)

            if spalte == 2:
                t += br + nl

                url_str = tex_urls(urls) + nl
                t += url_str

                urls = []

                if zeile == 3:
                    t += table_end
                    t += pagebreak + nl

                zeile = (zeile+1) % 4
            else:
                t += '& '

            spalte = (spalte+1) % 3

        # Wenn wir bei der allerletzten Tabelle sind, müssen wir den Rest noch
        # wegflushen:
        t += br + nl
        url_str = tex_urls(urls) + nl
        t += url_str
        t += table_end
    else: # nr > 1
        for n, puzzle in enumerate(puzzles):
            if n % 4 == 0:
                t += heading

            t += r'\begin{tabular}{c}' + nl
            t += tex_puzzle(puzzle) + br + nl
            t += tex_url(puzzle.url) + nl
            t += r'\end{tabular}' + nl

            t += r'\begin{tabular}{lll}' + nl
            for i, s in enumerate(serialize(puzzle.solution)):
                var = pgn_variation(s, puzzle.board.turn)
                t += r'\variation[invar]{' + var + '}'
                if i % 3 == 2:
                    t += br + nl
                else:
                    t += ' &' + nl

            t += r'\end{tabular}' + br + nl

            if n % 4 == 3:
                t += pagebreak

    return t


def tex_url(url):
    return r'\href{' + url + r'}{\texttt{' + url[8:] + '}}'


def tex_urls(urls):
    t = ''

    for i, url in enumerate(urls):
        t += tex_url(url) + nl
        if i < len(urls)-1:
            t += '& '
        else:
            t += br

    return t


b = chess.Board(fen='7K/8/8/5kq1/8/8/8/8 b - - 6 62')
m1 = chess.Board(fen='8/7K/5k2/6q1/8/8/8/8 b - - 8 63')
m21 = chess.Board(fen='8/8/8/8/8/5k1K/6p1/4q3 b - - 1 79')
m22 = chess.Board('8/8/5N2/p7/6Q1/P3K3/8/5k2 w - - 5 78')
morphy_puzzle = chess.Board('kbK5/pp6/1P6/8/8/8/8/R7 w - - 0 1')
test_2 = chess.Board(fen='8/1K6/8/8/6k1/2q5/8/3q4 b - - 5 65')

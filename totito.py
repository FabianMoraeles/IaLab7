"""
Lab 07 - Búsqueda Adversaria
Punto 1: Tic-Tac-Toe (3x3 y 4x4)

Clases:
  - TicTacToeEngine: estado y algoritmos (minimax, alpha-beta, MCTS).
  - GameLoop: orquestador de partidas H-H, H-IA, IA-IA.
"""

import math
import time
import random
from typing import List, Tuple, Optional, Dict


class TicTacToeEngine:
    # Símbolos y tamaño del tablero

    EMPTY = '.'

    def __init__(self, size: int = 3, board: Optional[List[List[str]]] = None):
        assert size in (3, 4), "size debe ser 3 o 4"
        self.size = size
        self.win_len = size
        if board is None:
            self.board = [[self.EMPTY] * size for _ in range(size)]
        else:
            self.board = [row[:] for row in board]
        self.nodes_visited = 0

    # Copia profunda del estado
    def clone(self) -> "TicTacToeEngine":
        new = TicTacToeEngine(self.size)
        new.board = [row[:] for row in self.board]
        return new

    # Verifica si una celda está vacía
    def is_empty(self, row: int, col: int) -> bool:
        return self.board[row][col] == self.EMPTY

    # Retorna lista de movimientos disponibles
    def get_moves(self) -> List[Tuple[int, int]]:
        return [(r, c) for r in range(self.size)
                       for c in range(self.size) if self.is_empty(r, c)]

    # Coloca símbolo en celda
    def make_move(self, row: int, col: int, player: str) -> None:
        if not self.is_empty(row, col):
            raise ValueError(f"Celda ({row},{col}) ocupada")
        self.board[row][col] = player

    # Deshace último movimiento
    def undo_move(self, row: int, col: int) -> None:
        self.board[row][col] = self.EMPTY

    # Retorna símbolo del oponente
    def opponent(self, player: str) -> str:
        return 'O' if player == 'X' else 'X'

    # Verifica victoria en filas, columnas y diagonales
    def is_winner(self, player: str) -> bool:
        n = self.size
        for i in range(n):
            if all(self.board[i][j] == player for j in range(n)):
                return True
            if all(self.board[j][i] == player for j in range(n)):
                return True
        if all(self.board[i][i] == player for i in range(n)):
            return True
        if all(self.board[i][n - 1 - i] == player for i in range(n)):
            return True
        return False

    # Tablero lleno sin ganador
    def is_full(self) -> bool:
        return all(self.board[r][c] != self.EMPTY
                   for r in range(self.size) for c in range(self.size))

    # Estado terminal: alguien ganó o tablero lleno
    def is_terminal(self) -> bool:
        return self.is_winner('X') or self.is_winner('O') or self.is_full()

    # Heurística: suma líneas exclusivas del jugador, resta del oponente
    def evaluate(self, ai_player: str = 'X') -> int:
        opp = self.opponent(ai_player)
        if self.is_winner(ai_player):
            return 10_000
        if self.is_winner(opp):
            return -10_000
        score = 0
        for line in self._all_lines():
            cnt_ai = sum(1 for v in line if v == ai_player)
            cnt_op = sum(1 for v in line if v == opp)
            if cnt_ai > 0 and cnt_op == 0:
                score += 10 ** cnt_ai
            elif cnt_op > 0 and cnt_ai == 0:
                score -= 10 ** cnt_op
        return score

    # Extrae todas las líneas: filas, columnas, diagonales
    def _all_lines(self) -> List[List[str]]:
        n = self.size
        lines = []
        for i in range(n):
            lines.append([self.board[i][j] for j in range(n)])
            lines.append([self.board[j][i] for j in range(n)])
        lines.append([self.board[i][i] for i in range(n)])
        lines.append([self.board[i][n - 1 - i] for i in range(n)])
        return lines

    # Minimax exhaustivo sin límite de profundidad
    def minimax_pure(self, ai_player: str = 'X') -> Tuple[int, Optional[Tuple[int, int]]]:
        return self._minimax_pure_rec(ai_player, ai_player)

    # Recursión minimax puro
    def _minimax_pure_rec(self, current: str, ai_player: str
                          ) -> Tuple[int, Optional[Tuple[int, int]]]:
        self.nodes_visited += 1
        opp = self.opponent(ai_player)

        if self.is_winner(ai_player):
            return 10_000, None
        if self.is_winner(opp):
            return -10_000, None
        if self.is_full():
            return 0, None

        moves = self.get_moves()
        best_move = None

        if current == ai_player:
            best_val = -math.inf
            for (r, c) in moves:
                self.make_move(r, c, current)
                val, _ = self._minimax_pure_rec(opp, ai_player)
                self.undo_move(r, c)
                if val > best_val:
                    best_val, best_move = val, (r, c)
            return best_val, best_move
        else:
            best_val = math.inf
            for (r, c) in moves:
                self.make_move(r, c, current)
                val, _ = self._minimax_pure_rec(ai_player, ai_player)
                self.undo_move(r, c)
                if val < best_val:
                    best_val, best_move = val, (r, c)
            return best_val, best_move

    # Minimax con horizonte limitado
    def minimax_limit(self, depth: int, ai_player: str = 'X'
                      ) -> Tuple[int, Optional[Tuple[int, int]]]:
        return self._minimax_limit_rec(depth, ai_player, ai_player)

    # Recursión minimax limitado: corta con evaluate() al alcanzar depth
    def _minimax_limit_rec(self, depth: int, current: str, ai_player: str
                           ) -> Tuple[int, Optional[Tuple[int, int]]]:
        self.nodes_visited += 1
        opp = self.opponent(ai_player)

        if self.is_winner(ai_player):
            return 10_000, None
        if self.is_winner(opp):
            return -10_000, None
        if self.is_full() or depth == 0:
            return self.evaluate(ai_player), None

        moves = self.get_moves()
        best_move = None

        if current == ai_player:
            best_val = -math.inf
            for (r, c) in moves:
                self.make_move(r, c, current)
                val, _ = self._minimax_limit_rec(depth - 1, opp, ai_player)
                self.undo_move(r, c)
                if val > best_val:
                    best_val, best_move = val, (r, c)
            return best_val, best_move
        else:
            best_val = math.inf
            for (r, c) in moves:
                self.make_move(r, c, current)
                val, _ = self._minimax_limit_rec(depth - 1, ai_player, ai_player)
                self.undo_move(r, c)
                if val < best_val:
                    best_val, best_move = val, (r, c)
            return best_val, best_move

    # Alpha-beta pruning: poda de ramas inútiles
    def alpha_beta(self, depth: int, alpha: float = -math.inf,
                   beta: float = math.inf, ai_player: str = 'X'
                   ) -> Tuple[int, Optional[Tuple[int, int]]]:
        return self._alpha_beta_rec(depth, alpha, beta, ai_player, ai_player)

    # Recursión alpha-beta: poda cuando alpha >= beta
    def _alpha_beta_rec(self, depth: int, alpha: float, beta: float,
                        current: str, ai_player: str
                        ) -> Tuple[int, Optional[Tuple[int, int]]]:
        self.nodes_visited += 1
        opp = self.opponent(ai_player)

        if self.is_winner(ai_player):
            return 10_000, None
        if self.is_winner(opp):
            return -10_000, None
        if self.is_full() or depth == 0:
            return self.evaluate(ai_player), None

        moves = self.get_moves()
        best_move = None

        if current == ai_player:
            best_val = -math.inf
            for (r, c) in moves:
                self.make_move(r, c, current)
                val, _ = self._alpha_beta_rec(depth - 1, alpha, beta, opp, ai_player)
                self.undo_move(r, c)
                if val > best_val:
                    best_val, best_move = val, (r, c)
                alpha = max(alpha, best_val)
                if alpha >= beta:
                    break
            return best_val, best_move
        else:
            best_val = math.inf
            for (r, c) in moves:
                self.make_move(r, c, current)
                val, _ = self._alpha_beta_rec(depth - 1, alpha, beta, ai_player, ai_player)
                self.undo_move(r, c)
                if val < best_val:
                    best_val, best_move = val, (r, c)
                beta = min(beta, best_val)
                if alpha >= beta:
                    break
            return best_val, best_move

    # MCTS con UCT: selección balanceada exploración-explotación
    def mcts(self, iterations: int = 500, C: float = math.sqrt(2),
             ai_player: str = 'X') -> Tuple[float, Optional[Tuple[int, int]]]:
        def new_node(state, move, player_to_move, parent=None):
            return {
                'state': state,
                'move': move,
                'player_to_move': player_to_move,
                'parent': parent,
                'children': [],
                'untried_moves': state.get_moves() if not state.is_terminal() else [],
                'visits': 0,
                'wins': 0.0,
            }

        # UCT: mean_win_rate + C * sqrt(ln(parent_visits) / node_visits)
        def best_uct_child(node, C):
            ln_parent = math.log(node['visits']) if node['visits'] > 0 else 0.0
            def uct_score(ch):
                if ch['visits'] == 0:
                    return math.inf
                return (ch['wins'] / ch['visits']) + C * math.sqrt(ln_parent / ch['visits'])
            return max(node['children'], key=uct_score)

        # Crea nodo hijo con movimiento aleatorio no explorado
        def expand(node, ai_player):
            move = node['untried_moves'].pop()
            new_state = node['state'].clone()
            new_state.make_move(move[0], move[1], node['player_to_move'])
            next_player = new_state.opponent(node['player_to_move'])
            child = new_node(new_state, move, next_player, parent=node)
            node['children'].append(child)
            return child

        # Simulación: juego aleatorio hasta terminal
        def rollout(node, ai_player):
            sim = node['state'].clone()
            current = node['player_to_move']
            while not sim.is_terminal():
                moves = sim.get_moves()
                r, c = random.choice(moves)
                sim.make_move(r, c, current)
                current = sim.opponent(current)
            if sim.is_winner(ai_player):
                return 1.0
            if sim.is_winner(sim.opponent(ai_player)):
                return 0.0
            return 0.5

        root = new_node(self.clone(), None, ai_player)

        # Iteraciones: selección, expansión, simulación, retropropagación
        for _ in range(iterations):
            self.nodes_visited += 1
            node = root
            # Selecciona hijo con máximo UCT hasta hoja completamente expandida
            while not node['state'].is_terminal() and len(node['untried_moves']) == 0:
                node = best_uct_child(node, C)
            # Expande un hijo si el estado no es terminal
            if not node['state'].is_terminal():
                node = expand(node, ai_player)
            # Simula juego aleatorio desde el nodo
            result = rollout(node, ai_player)
            # Retropropaga resultado hacia la raíz, invirtiendo según turno
            while node is not None:
                node['visits'] += 1
                if node['player_to_move'] == ai_player:
                    node['wins'] += result
                else:
                    node['wins'] += (1.0 - result)
                node = node['parent']

        # Retorna el hijo con más visitas
        if not root['children']:
            return 0.0, None
        best = max(root['children'], key=lambda ch: ch['visits'])
        return (best['wins'] / best['visits'] if best['visits'] else 0.0), best['move']


class GameLoop:
    # Orquestador de partidas: controla modo, turnos, entrada/salida

    def __init__(self,
                 size: int = 3,
                 mode: str = "H-IA",
                 starting_player: str = 'H',
                 ia_configs: Optional[Dict] = None,
                 verbose: bool = True):
        assert size in (3, 4)
        assert mode in ("H-H", "H-IA", "IA-IA")
        assert starting_player in ('H', 'IA')

        self.size = size
        self.mode = mode
        self.starting_player = starting_player
        self.verbose = verbose
        self.ia_configs = ia_configs or {}
        self.engine = TicTacToeEngine(size)

    # Imprime tablero con índices de filas y columnas
    def _print_board(self) -> None:
        n = self.engine.size
        header = "    " + "   ".join(str(c) for c in range(n))
        print(header)
        for r in range(n):
            row_str = "  ".join(self.engine.board[r])
            print(f"{r}   {row_str}")
        print()

    # Selecciona movimiento IA según algoritmo configurado
    def _ia_move(self, ia_key: str, player_symbol: str) -> Tuple[int, int]:
        cfg = self.ia_configs.get(ia_key, {})
        algo = cfg.get('algorithm', 'alpha_beta')
        depth = cfg.get('depth', 4 if self.size == 4 else 9)
        N = cfg.get('N', 500)
        C = cfg.get('C', math.sqrt(2))

        self.engine.nodes_visited = 0
        t0 = time.perf_counter()

        if algo == 'minimax':
            if self.size == 3:
                _, move = self.engine.minimax_pure(ai_player=player_symbol)
            else:
                _, move = self.engine.minimax_limit(depth, ai_player=player_symbol)
        elif algo == 'minimax_limit':
            _, move = self.engine.minimax_limit(depth, ai_player=player_symbol)
        elif algo == 'alpha_beta':
            _, move = self.engine.alpha_beta(depth, ai_player=player_symbol)
        elif algo == 'mcts':
            _, move = self.engine.mcts(iterations=N, C=C, ai_player=player_symbol)
        else:
            raise ValueError(f"Algoritmo desconocido: {algo}")

        elapsed = time.perf_counter() - t0

        # Nodos y tiempo siempre se imprimen tras cada jugada IA
        print(f"[{ia_key} | {algo}] jugada={move}  "
              f"nodos={self.engine.nodes_visited}  "
              f"tiempo={elapsed:.4f}s")

        if move is None:
            move = self.engine.get_moves()[0]
        return move

    # Lee entrada humana: fila y columna
    def _human_move(self, symbol: str) -> Tuple[int, int]:
        while True:
            try:
                raw = input(f"Turno de Humano ({symbol}). Ingrese 'fila col': ").strip()
                r, c = map(int, raw.split())
                if 0 <= r < self.size and 0 <= c < self.size and self.engine.is_empty(r, c):
                    return r, c
                print("Movimiento inválido, intente de nuevo.")
            except (ValueError, IndexError):
                print("Formato inválido. Use: '1 2'")

    # Ejecuta partida completa hasta terminal
    def play(self) -> str:
        if self.verbose:
            print(f"\n=== Tic-Tac-Toe {self.size}x{self.size} | "
                  f"Modo: {self.mode} | Inicia: {self.starting_player} ===\n")
            self._print_board()

        # Asigna símbolos X y O según modo
        if self.mode == "H-H":
            agents = [('H1', 'X'), ('H2', 'O')]
        elif self.mode == "H-IA":
            if self.starting_player == 'H':
                agents = [('H', 'X'), ('IA1', 'O')]
            else:
                agents = [('IA1', 'X'), ('H', 'O')]
        else:
            agents = [('IA1', 'X'), ('IA2', 'O')]

        # Alternancia de turnos
        turno = 0
        while not self.engine.is_terminal():
            agent_id, symbol = agents[turno % 2]
            if agent_id.startswith('H'):
                r, c = self._human_move(symbol)
            else:
                r, c = self._ia_move(agent_id, symbol)
            self.engine.make_move(r, c, symbol)
            # Tablero siempre se imprime tras cada movimiento
            print(f"-> {agent_id} ({symbol}) juega ({r},{c})")
            self._print_board()
            turno += 1

        # Determina resultado
        if self.engine.is_winner('X'):
            result = 'X'
        elif self.engine.is_winner('O'):
            result = 'O'
        else:
            result = 'EMPATE'
        if self.verbose:
            print(f"=== Resultado: {result} ===")
        return result
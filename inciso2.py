"""
Lab 07 - Inciso 2: Explosión Combinatoria
Medición de nodos visitados, tiempo y factor de ramificación.
"""

import time
import math
from totito import TicTacToeEngine


def measure_search(size: int, algorithm: str, depth: int) -> dict:
    # Crea tablero vacío y ejecuta búsqueda
    engine = TicTacToeEngine(size)
    engine.nodes_visited = 0
    t0 = time.perf_counter()

    if algorithm == 'minimax':
        _, _ = engine.minimax_limit(depth, ai_player='X')
    elif algorithm == 'alpha_beta':
        _, _ = engine.alpha_beta(depth, ai_player='X')

    elapsed = time.perf_counter() - t0
    nodes = engine.nodes_visited

    # Factor de ramificación efectivo: depth√nodos
    branching_factor = None
    if nodes > 0 and depth > 0:
        branching_factor = nodes ** (1 / depth)

    return {
        'depth': depth,
        'nodes': nodes,
        'time': elapsed,
        'branching_factor': branching_factor,
    }


# Inciso 2(a): 3x3 con minimax
print("INCISO 2(a): totito 3×3 - Minimax (sin poda)")

print(f"{'Depth':<6} {'Nodos Visitados':<18} {'Tiempo (s)':<15}")


results_3x3_minimax = []
for d in range(1, 10):
    result = measure_search(3, 'minimax', d)
    results_3x3_minimax.append(result)
    print(f"{d:<6} {result['nodes']:<18} {result['time']:<15.6f}")

# Inciso 2(a): 3x3 con alpha-beta

print("INCISO 2(a): totito 3×3 - Alpha-Beta (con poda)")
print(f"{'Depth':<6} {'Nodos Visitados':<18} {'Tiempo (s)':<15}")


results_3x3_ab = []
for d in range(1, 10):
    result = measure_search(3, 'alpha_beta', d)
    results_3x3_ab.append(result)
    print(f"{d:<6} {result['nodes']:<18} {result['time']:<15.6f}")

# Comparación 3x3

print("COMPARACIÓN 3×3: Minimax vs Alpha-Beta")
print(f"{'Depth':<6} {'Minimax (nodos)':<20} {'AB (nodos)':<20} {'Ratio (MM/AB)':<15}")


for d in range(1, 10):
    mm_nodes = results_3x3_minimax[d-1]['nodes']
    ab_nodes = results_3x3_ab[d-1]['nodes']
    ratio = mm_nodes / ab_nodes if ab_nodes > 0 else float('inf')
    print(f"{d:<6} {mm_nodes:<20} {ab_nodes:<20} {ratio:<15.2f}")

# Inciso 2(b): 4x4 con alpha-beta

print("INCISO 2: totito 4×4 ")

print(f"{'Depth':<6} {'Nodos':<18} {'Tiempo (s)':<15} {'Factor Ramif. (d√n)':<20}")


results_4x4_ab = []
for d in range(1, 7):
    result = measure_search(4, 'alpha_beta', d)
    results_4x4_ab.append(result)
    bf = result['branching_factor']
    bf_str = f"{bf:.4f}" if bf is not None else "N/A"
    print(f"{d:<6} {result['nodes']:<18} {result['time']:<15.6f} {bf_str:<20}")


print("RESUMEN")
print("\n3×3 Minimax: profundidad 9 alcanzada sin problemas")
print(f"  Nodos en depth=9: {results_3x3_minimax[8]['nodes']}")
print(f"  Tiempo en depth=9: {results_3x3_minimax[8]['time']:.6f}s")

print("\n3×3 Alpha-Beta: poda significativa vs minimax puro")
print(f"  Nodos en depth=9: {results_3x3_ab[8]['nodes']}")
print(f"  Reducción: {results_3x3_minimax[8]['nodes'] / results_3x3_ab[8]['nodes']:.2f}x")

print("\n4×4 Alpha-Beta: profundidad 6 alcanzada")
print(f"  Nodos en depth=6: {results_4x4_ab[5]['nodes']}")
print(f"  Tiempo en depth=6: {results_4x4_ab[5]['time']:.6f}s")
print(f"  Factor ramificación en depth=6: {results_4x4_ab[5]['branching_factor']:.4f}")
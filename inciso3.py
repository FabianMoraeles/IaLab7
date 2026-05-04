"""
Lab 07 - Inciso 3: Duelo de Algoritmos (IA-IA)
20 partidas: MCTS (N=500, C=√2) vs Minimax AB (depth=4)
"""

import math
import time
from totito import  GameLoop


def ejecutar_duelo(numero_partidas: int = 20) -> None:
    # Configuración de ambas IAs
    configuracion_ias = {
        'IA1': {'algorithm': 'mcts',       'N': 500, 'C': math.sqrt(2)},
        'IA2': {'algorithm': 'alpha_beta', 'depth': 4},
    }

    # Registra resultados y tiempos de cada partida
    resultados_partidas = []
    tiempo_acumulado_ia1 = []
    tiempo_acumulado_ia2 = []

    
    print("INCISO 3: Duelo IA-IA (20 partidas, tablero 3×3)")
    print("  IA1: MCTS        N=500, C=√2")
    print("  IA2: AB  depth=4")
    
    print(f"{'Partida':<10} {'Resultado':<12} {'Ganador':<10} {'T_IA1 (s)':<14} {'T_IA2 (s)':<14}")
    print("-" * 70)

    # Ejecuta todas las partidas
    for num_partida in range(1, numero_partidas + 1):
        # Crea nueva partida IA contra IA
        bucle_partida = GameLoop(
            size=3,
            mode="IA-IA",
            starting_player='IA',
            ia_configs=configuracion_ias,
            verbose=False,
        )

        # Mide tiempo acumulado de cada IA durante la partida
        tiempo_ia1_partida = 0.0
        tiempo_ia2_partida = 0.0
        tablero = bucle_partida.engine
        
        # IA1 siempre usa X, IA2 siempre usa O
        agentes = [('IA1', 'X'), ('IA2', 'O')]
        turno_actual = 0

        # Simula la partida movimiento a movimiento
        while not tablero.is_terminal():
            id_agente, simbolo_jugador = agentes[turno_actual % 2]
            config_agente = configuracion_ias[id_agente]
            algoritmo = config_agente.get('algorithm')
            tablero.nodes_visited = 0

            # Ejecuta búsqueda del algoritmo y mide tiempo
            tiempo_inicio = time.perf_counter()
            if algoritmo == 'mcts':
                _, movimiento = tablero.mcts(
                    iterations=config_agente['N'], 
                    C=config_agente['C'], 
                    ai_player=simbolo_jugador)
            else:
                _, movimiento = tablero.alpha_beta(
                    config_agente['depth'], 
                    ai_player=simbolo_jugador)
            tiempo_transcurrido = time.perf_counter() - tiempo_inicio

            # Acumula tiempo según la IA
            if id_agente == 'IA1':
                tiempo_ia1_partida += tiempo_transcurrido
            else:
                tiempo_ia2_partida += tiempo_transcurrido

            # Aplica movimiento si es válido
            if movimiento is None:
                movimiento = tablero.get_moves()[0]
            tablero.make_move(movimiento[0], movimiento[1], simbolo_jugador)
            turno_actual += 1

        # Determina ganador de la partida
        if tablero.is_winner('X'):
            ganador = 'IA1 (MCTS)'
            resultado_texto = 'X gana'
        elif tablero.is_winner('O'):
            ganador = 'IA2 (AB)'
            resultado_texto = 'O gana'
        else:
            ganador = 'EMPATE'
            resultado_texto = 'Empate'

        # Guarda resultado
        resultados_partidas.append(ganador)
        tiempo_acumulado_ia1.append(tiempo_ia1_partida)
        tiempo_acumulado_ia2.append(tiempo_ia2_partida)

        print(f"{num_partida:<10} {resultado_texto:<12} {ganador:<10} {tiempo_ia1_partida:<14.4f} {tiempo_ia2_partida:<14.4f}")

    # Calcula estadísticas finales
    victorias_ia1 = resultados_partidas.count('IA1 (MCTS)')
    victorias_ia2 = resultados_partidas.count('IA2 (AB)')
    numero_empates = resultados_partidas.count('EMPATE')
    tiempo_promedio_ia1 = sum(tiempo_acumulado_ia1) / numero_partidas
    tiempo_promedio_ia2 = sum(tiempo_acumulado_ia2) / numero_partidas

    
    print("RESUMEN")
    
    print(f"IA1 MCTS      victorias: {victorias_ia1:>3} / {numero_partidas}   "
          f"tiempo promedio por partida: {tiempo_promedio_ia1:.4f}s")
    print(f"IA2 AlphaBeta victorias: {victorias_ia2:>3} / {numero_partidas}   "
          f"tiempo promedio por partida: {tiempo_promedio_ia2:.4f}s")
    print(f"Empates:                 {numero_empates:>3} / {numero_partidas}")

    # Responde pregunta del enunciado
    
    print("ANÁLISIS")
    

    ia_mas_inteligente = "IA1 (MCTS)" if victorias_ia1 > victorias_ia2 else \
                         "IA2 (AB)" if victorias_ia2 > victorias_ia1 else "Empate estadístico"
    ia_mas_eficiente = "IA1 (MCTS)" if tiempo_promedio_ia1 < tiempo_promedio_ia2 else "IA2 (AB)"

    print(f"Más inteligente: {ia_mas_inteligente}")
    print(f"Más eficiente: {ia_mas_eficiente}")
    print(f"Tiempo promedio IA1 MCTS     : {tiempo_promedio_ia1:.4f}s")
    print(f"Tiempo promedio IA2 AB: {tiempo_promedio_ia2:.4f}s")


if __name__ == "__main__":
    ejecutar_duelo(20)
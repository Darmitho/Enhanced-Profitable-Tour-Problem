# -*- coding: utf-8 -*-
import sys
import time
import itertools
import functions as f

def nombre_funcion(func):
    return func.__name__

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(f"{sys.argv[0]} Rechazado")
        sys.exit(1)

    filename_tour = sys.argv[1] + ".txt"
    filename_users = sys.argv[2] + ".txt"
    iterations = int(sys.argv[3])

    instance_data = f.read_instance_file(filename_tour)
    num_nodes = instance_data.numNodes
    user_data_list = f.read_user_data_file(filename_users, num_nodes)

    print(f"Se leyeron {len(user_data_list)} usuarios correctamente.")

    # Movimiento obligatorio
    base_move = f.insert_move

    # Movimientos opcionales
    other_moves = [
        f.remove_move,
        f.swap_move,
        f.two_opt_move,
        f.move_node_forward,
        f.move_node_backward,
        f.replace_node
    ]

    results = []
    combinaciones = []
    for r in range(0, len(other_moves)+1):  # Incluye combinación vacía
        combinaciones.extend(itertools.combinations(other_moves, r))

    total_combis = len(combinaciones)

    print(f"Probando {total_combis} combinaciones con insert_move obligatorio...")

    for idx, combo in enumerate(combinaciones):
        selected_moves = [base_move] + list(combo)

        start_time = time.time()
        total_score = 0

        for user_data in user_data_list:
            initial_solution = f.generate_solution(instance_data, user_data)
            improved_solution = f.hill_climbing(initial_solution, instance_data, user_data, selected_moves)
            total_score += improved_solution.totalScore

        avg_score = total_score / len(user_data_list)
        elapsed = time.time() - start_time

        results.append({
            "combination": [nombre_funcion(m) for m in selected_moves],
            "avg_score": avg_score,
            "time": elapsed
        })

        print(f"[{idx+1}/{total_combis}] Progreso - Puntaje: {avg_score:.2f} | Tiempo: {elapsed:.2f}s     ", end='\r')

    print("\n\nTop 20 combinaciones por puntuación promedio:\n")

    top_20 = sorted(results, key=lambda x: x["avg_score"], reverse=True)[:20]

    for i, r in enumerate(top_20, 1):
        print(f"{i:02d}) Puntaje: {r['avg_score']:.2f} | Tiempo: {r['time']:.2f}s | Movimientos: {', '.join(r['combination'])}")
# -*- coding: utf-8 -*-
import sys
import time
import itertools
import numpy as np
from multiprocessing import Pool, cpu_count
import functions as f

def nombre_funcion(func):
    return func.__name__

def evaluate_single_configuration(args):
    """
    Evalúa una única configuración de parámetros SA sobre todos los usuarios y retorna estadísticas.
    """
    temp, cooling, max_iter, repetitions, instance_data, user_data_list, moves = args
    total_score = 0
    start_time = time.time()

    for user_data in user_data_list:
        initial_solution = f.generate_solution(instance_data, user_data)

        # Evaluar varias veces por usuario (repeticiones)
        for _ in range(repetitions):
            sa_result, _ = f.simulated_annealing(
                initial_solution,
                instance_data,
                user_data,
                moves,
                initial_temperature=temp,
                cooling_rate=cooling,
                min_temperature=1e-3,
                max_iterations=max_iter
            )
            total_score += sa_result.totalScore

    elapsed = time.time() - start_time
    avg_score = total_score / (len(user_data_list) * repetitions)

    return {
        "temperature": temp,
        "cooling": cooling,
        "max_iter": max_iter,
        "avg_score": avg_score,
        "time": elapsed
    }

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(f"Uso: {sys.argv[0]} <nombre_instancia> <nombre_usuarios> <repeticiones>")
        sys.exit(1)

    filename_tour = sys.argv[1] + ".txt"
    filename_users = sys.argv[2] + ".txt"
    repetitions = int(sys.argv[3])  # repeticiones por combinación por usuario

    instance_data = f.read_instance_file(filename_tour)
    num_nodes = instance_data.numNodes
    user_data_list = f.read_user_data_file(filename_users, num_nodes)

    print(f"Se leyeron {len(user_data_list)} usuarios correctamente.")

    base_move = f.insert_move
    other_moves = [
        f.remove_move,
        f.swap_move,
        f.two_opt_move,
        f.move_node_forward,
        f.move_node_backward,
        f.replace_node
    ]
    moves = [base_move] + other_moves

    # Parámetros del Grid Search
    temperatures = [5, 10, 20]
    cooling_rates = [0.985, 0.99]
    max_iterations_list = [100, 200, 300]

    param_grid = list(itertools.product(temperatures, cooling_rates, max_iterations_list))
    print(f"Ejecutando Grid Search con {len(param_grid)} combinaciones...")

    # Armar argumentos por combinación para multiprocesamiento
    args_list = [
        (temp, cooling, max_iter, repetitions, instance_data, user_data_list, moves)
        for (temp, cooling, max_iter) in param_grid
    ]

    # Ejecutar en paralelo usando todos los núcleos disponibles
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(evaluate_single_configuration, args_list)

    print("\n\nTop 10 configuraciones por score promedio:\n")
    top_results = sorted(results, key=lambda x: x["avg_score"], reverse=True)[:10]

    for i, r in enumerate(top_results, 1):
        print(f"{i:02d}) Score: {r['avg_score']:.2f} | Tiempo: {r['time']:.2f}s | T={r['temperature']} | α={r['cooling']} | Iters={r['max_iter']}")

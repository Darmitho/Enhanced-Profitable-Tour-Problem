# grid_search_tabu.py

import sys
import time
import itertools
from multiprocessing import Pool, cpu_count
import functions as f

def evaluate_tabu_configuration(args):
    """
    Evalúa una única configuración de Tabu Search.
    """
    tabu_tenure, max_iters, max_no_improve, instance_data, user_data_list, moves = args
    total_score = 0
    start_time = time.time()

    for user_data in user_data_list:
        initial_solution = f.generate_solution(instance_data, user_data)
        best_solution, _ = f.tabu_search(
            solution=initial_solution,
            instance_data=instance_data,
            user_data=user_data,
            moves=moves,
            max_iterations=max_iters,
            tabu_tenure=tabu_tenure,
            max_no_improve=max_no_improve,
            verbose=False
        )
        total_score += best_solution.totalScore

    elapsed = time.time() - start_time
    avg_score = total_score / len(user_data_list)

    return {
        "tabu_tenure": tabu_tenure,
        "max_iter": max_iters,
        "max_no_improve": max_no_improve,
        "avg_score": avg_score,
        "time": elapsed
    }

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Uso: {sys.argv[0]} <nombre_instancia> <nombre_usuarios>")
        sys.exit(1)

    filename_tour = sys.argv[1] + ".txt"
    filename_users = sys.argv[2] + ".txt"

    instance_data = f.read_instance_file(filename_tour)
    user_data_list = f.read_user_data_file(filename_users, instance_data.numNodes)

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

    # Definición del grid
    tabu_tenures = [5, 10, 15]
    max_iterations_list = [50, 100, 150]
    max_no_improve_list = [10, 20, 30]

    param_grid = list(itertools.product(tabu_tenures, max_iterations_list, max_no_improve_list))
    print(f"Ejecutando Grid Search con {len(param_grid)} combinaciones...")

    args_list = [
        (tenure, max_iter, max_no_improve, instance_data, user_data_list, moves)
        for (tenure, max_iter, max_no_improve) in param_grid
    ]

    with Pool(processes=cpu_count()) as pool:
        results = pool.map(evaluate_tabu_configuration, args_list)

    print("\nTop configuraciones por score promedio:\n")
    top_results = sorted(results, key=lambda x: x["avg_score"], reverse=True)[:10]

    for i, r in enumerate(top_results, 1):
        print(f"{i:02d}) Score: {r['avg_score']:.2f} | Tiempo: {r['time']:.2f}s | Tenure={r['tabu_tenure']} | MaxIters={r['max_iter']} | NoImprove={r['max_no_improve']}")

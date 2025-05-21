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
    user_data_list = f.read_user_data_file(filename_users, instance_data.numNodes)
    print(f"Se leyeron {len(user_data_list)} usuarios correctamente.")

    # Lista base de movimientos (todos deberían aceptar first_improvement=True)
    move_pool = [
        f.insert_move,
        f.swap_move,
        f.remove_move,
        f.two_opt_move,
        f.move_node_forward,
        f.move_node_backward,
        f.replace_node
    ]

    # Elegir subconjunto de movimientos a permutar (por ejemplo 4)
    selected = move_pool  # Cambia este número según lo que quieras probar
    permutaciones = list(itertools.permutations(selected))

    resultados = []
    total = len(permutaciones)

    print(f"Evaluando {total} permutaciones de orden con first improvement...\n")

    for idx, orden in enumerate(permutaciones):
        inicio = time.time()
        total_score = 0

        for user in user_data_list:
            initial_solution = f.generate_solution(instance_data, user)
            improved_solution = f.hill_climbing_first_improvement(initial_solution, instance_data, user, list(orden))
            total_score += improved_solution.totalScore

        promedio = total_score / len(user_data_list)
        duracion = time.time() - inicio

        resultados.append({
            "orden": [nombre_funcion(m) for m in orden],
            "score": promedio,
            "tiempo": duracion
        })

        print(f"[{idx+1}/{total}] Puntaje: {promedio:.2f} Tiempo: {duracion:.2f}s Orden: {', '.join(nombre_funcion(m) for m in orden)}", end='\r')

    print("\n\n🔝 Mejores 100 órdenes de movimientos (first improvement):\n")

    top_10 = sorted(resultados, key=lambda x: x["score"], reverse=True)[:100]
    for i, r in enumerate(top_10, 1):
        print(f"{i:02d}) Puntaje: {r['score']:.2f} | Tiempo: {r['tiempo']:.2f}s | Orden: {', '.join(r['orden'])}")

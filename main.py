# -*- coding: utf-8 -*-
import sys
import time
import functions as f

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(f"{sys.argv[0]} Rechazado")
        sys.exit(1)

    # Leer argumentos de línea de comandos
    filename_tour = sys.argv[1] + ".txt"
    filename_users = sys.argv[2] + ".txt"
    iterations = int(sys.argv[3])

    # Leer datos de la instancia
    instance_data = f.read_instance_file(filename_tour)
    num_nodes = instance_data.numNodes

    # Leer datos de usuarios
    user_data_list = f.read_user_data_file(filename_users, num_nodes)

    print(f"Se leyeron {len(user_data_list)} usuarios correctamente.")

    inicio = time.time()

    # Lista con soluciones iniciales por usuario
    initial_solutions = []

    for user_index, user_data in enumerate(user_data_list):
        initial_solution = f.generate_solution(instance_data, user_data)
        initial_solutions.append(initial_solution)

        #Hill Climbing
        selected_moves = [
                            f.insert_move,
                            f.remove_move,
                            f.swap_move,
                            #f.two_opt_move,
                            #f.move_node_forward,
                            #f.move_node_backward,
                            #f.replace_node
                        ]
        improved_solution = f.hill_climbing(initial_solution, instance_data, user_data, selected_moves)
        
        #print(f"  Tiempo usado: {improved_solution.totalTimeUsed}")
        #print(f"Valor/Puntaje final del Tour: {improved_solution.totalScore}")
        #print(f"Tiempo disponible, Tiempo del Tour: {user_data.totalTime, improved_solution.totalTimeUsed}")
        #print(f"Nodos pertenecientes al Tour, en orden: {improved_solution.orderNodesVisited} \n \n")

        print(f"{improved_solution.totalScore}")
    fin = time.time()

    print(f"Tiempo total de ejecución: {fin - inicio:.2f} segundos")

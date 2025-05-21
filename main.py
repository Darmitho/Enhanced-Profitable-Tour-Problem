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

    print(f"Se leyeron {len(user_data_list)} usuarios correctamente. \n")

    inicio = time.time()

    # Lista con soluciones iniciales por usuario
    initial_solutions = []
    total_score = 0

    for user_index, user_data in enumerate(user_data_list):
        initial_solution = f.generate_solution(instance_data, user_data)
        initial_solutions.append(initial_solution)

        #Hill Climbing
        #selected_moves = [f.insert_move, f.remove_move, f.swap_move] #original
        #selected_moves = [f.insert_move, f.swap_move, f.two_opt_move, f.move_node_forward, f.move_node_backward, f.replace_node] #best_improvement
        selected_moves = [f.replace_node, f.move_node_backward, f.swap_move, f.insert_move, f.move_node_forward] #first_improvement
        
        #improved_solution, list_moves_found = f.hill_climbing(initial_solution, instance_data, user_data, selected_moves)
        improved_solution, list_moves_found = f.hill_climbing_first_improvement(initial_solution, instance_data, user_data, selected_moves)
    
        print(f"Valor/Puntaje final del Tour: {improved_solution.totalScore}")
        print(f"Tiempo disponible, Tiempo del Tour: {user_data.totalTime, improved_solution.totalTimeUsed}")
        print(f"Nodos pertenecientes al Tour, en orden: {improved_solution.orderNodesVisited} \n \n")

        #print(list_moves_found)
        total_score += improved_solution.totalScore
    fin = time.time()
    print(f"Promedio de puntaje: {total_score / len(user_data_list)}")
    print(f"Tiempo total de ejecución: {fin - inicio:.2f}[s]")

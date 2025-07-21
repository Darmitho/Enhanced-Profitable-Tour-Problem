import numpy as np
from dataclasses import dataclass
from typing import Callable, Tuple, List
import sys
import random
from collections import deque
from models import UserData, InstanceData, Solution
import random


def read_instance_file(filename: str) -> InstanceData:
    """
    Lee un archivo de instancia y construye un objeto InstanceData.

    Args:
    - filename: Ruta del archivo .txt de la instancia.

    Return:
    - InstanceData: instancia con nodos, tiempos de estadía y matriz de tiempos.
    """
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()

            # Leer el número de nodos
            num_nodes = int(lines[0].strip())

            # Leer los tiempos de estadía por nodo (segunda línea)
            node_times = np.array(list(map(int, lines[1].strip().split())), dtype=int)
            if node_times.shape[0] != num_nodes:
                raise ValueError("Cantidad de tiempos de nodos no coincide con el número de nodos")

            # Leer la matriz de tiempos entre arcos (siguientes num_nodes líneas)
            arc_lines = lines[2:2 + num_nodes]
            arc_times = np.array([list(map(int, line.strip().split())) for line in arc_lines], dtype=int)

            return InstanceData(numNodes=num_nodes, nodeTimes=node_times, arcTimes=arc_times)

    except FileNotFoundError:
        print(f"Error al abrir el archivo: {filename}")
        sys.exit(1)
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        sys.exit(1)

def read_user_data_file(filename: str, num_nodes: int) -> List[UserData]:
    """
    Lee un archivo con datos de usuarios y construye una lista de UserData.

    Args:
    - filename: Ruta del archivo de usuarios.
    - num_nodes: Número de nodos (tamaño de las matrices esperadas).

    Return:
    - Lista de instancias de UserData.
    """
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()

            num_users = int(lines[0].strip())
            users: List[UserData] = []
            current_line = 1

            for _ in range(num_users):
                # Leer el tiempo total disponible
                total_time = int(lines[current_line].strip())
                current_line += 1

                # Leer valorización por nodo
                node_prefs = np.array(
                    list(map(int, lines[current_line].strip().split())),
                    dtype=int
                )
                current_line += 1

                if node_prefs.size != num_nodes:
                    raise ValueError("Cantidad de preferencias de nodos no coincide con el número de nodos.")

                # Leer matriz de valorización de arcos (num_nodes líneas)
                arc_matrix = []
                for _ in range(num_nodes):
                    arc_line = list(map(int, lines[current_line].strip().split()))
                    if len(arc_line) != num_nodes:
                        raise ValueError("Tamaño de fila en arcPreferences inválido.")
                    arc_matrix.append(arc_line)
                    current_line += 1

                arc_prefs = np.array(arc_matrix, dtype=int)
                users.append(UserData(total_time, node_prefs, arc_prefs))

            return users

    except FileNotFoundError:
        print(f"Error al abrir el archivo: {filename}")
        sys.exit(1)
    except Exception as e:
        print(f"Error al leer el archivo de usuarios: {e}")
        sys.exit(1)

def extract_user_features(user_data: UserData, instance_data: InstanceData) -> dict:
    """
    Extrae características del usuario para análisis.

    Args:
    - user_data: instancia UserData.
    - instance_data: datos de la instancia (para calcular densidad de arcos).

    Return:
    - Diccionario con características del usuario.
    """
    node_scores = user_data.nodePreferences
    arc_scores = user_data.arcPreferences

    arc_validos = arc_scores[arc_scores != -1]

    # Densidad de arcos de la instancia, no del usuario
    arc_instancia = instance_data.arcTimes
    densidad_instancia = np.count_nonzero(arc_instancia != -1) / arc_instancia.size

    return {
        "total_time": user_data.totalTime,
        "avg_node_score": int(np.mean(node_scores)),
        "std_node_score": int(np.std(node_scores)),
        "max_node_score": np.max(node_scores),
        "min_node_score": np.min(node_scores),
        "score_range": np.max(node_scores) - np.min(node_scores),
        "avg_arc_score": int(np.mean(arc_validos)),
        "std_arc_score": int(np.std(arc_validos)),
        "density_arcs": round(densidad_instancia, 3)
    }

def search_node(node: int, order_nodes_visited: List[int]) -> bool:
    """
    Verifica si un nodo ya fue visitado.

    Args:
    - node: nodo a verificar.
    - order_nodes_visited: lista de nodos ya visitados.

    Return:
    - True si el nodo ya está en la lista, False si no.
    """
    return node in order_nodes_visited

def generate_solution(instance_data: InstanceData, user_data: UserData) -> Solution:
    """
    Genera una solución inicial greedy basada en eficiencia de puntuación-tiempo.

    Args:
    - instance_data: datos del grafo.
    - user_data: preferencias de un usuario.

    Return:
    - Instancia de Solution con el recorrido inicial.
    """
    solution = Solution(orderNodesVisited=[0],
                        totalScore=user_data.nodePreferences[0],
                        totalTimeUsed=instance_data.nodeTimes[0])
    
    current_node = 0
    num_nodes = instance_data.numNodes

    while True:
        best_node = -1
        best_combined_efficiency = -1

        for next_node in range(num_nodes):
            if (next_node == current_node or
                search_node(next_node, solution.orderNodesVisited) or
                instance_data.arcTimes[current_node][next_node] == -1):
                continue

            travel_time = instance_data.arcTimes[current_node][next_node] + instance_data.nodeTimes[next_node]
            return_time = instance_data.arcTimes[next_node][0]
            total_travel_time = travel_time + return_time + solution.totalTimeUsed

            if total_travel_time <= user_data.totalTime:
                node_efficiency = (
                    user_data.nodePreferences[next_node] +
                    user_data.arcPreferences[current_node][next_node]
                ) / travel_time

                accessible_efficiencies = []
                for accessible_node in range(num_nodes):
                    if (accessible_node != next_node and 
                        instance_data.arcTimes[next_node][accessible_node] != -1):
                        
                        acc_time = (instance_data.arcTimes[next_node][accessible_node] +
                                    instance_data.nodeTimes[accessible_node])
                        acc_score = (user_data.nodePreferences[accessible_node] +
                                     user_data.arcPreferences[next_node][accessible_node])
                        
                        if acc_time > 0:
                            accessible_efficiencies.append(acc_score / acc_time)

                avg_accessible_efficiency = (
                    sum(accessible_efficiencies) / len(accessible_efficiencies)
                    if accessible_efficiencies else 0.0
                )

                combined_efficiency = node_efficiency + avg_accessible_efficiency
                if combined_efficiency > best_combined_efficiency:
                    best_combined_efficiency = combined_efficiency
                    best_node = next_node

        if best_node == -1:
            break

        solution.totalTimeUsed += (
            instance_data.nodeTimes[best_node] +
            instance_data.arcTimes[current_node][best_node]
        )
        solution.totalScore += (
            user_data.nodePreferences[best_node] +
            user_data.arcPreferences[current_node][best_node]
        )
        solution.orderNodesVisited.append(best_node)
        current_node = best_node

    # Volver al nodo inicial
    solution.totalTimeUsed += instance_data.arcTimes[current_node][0]
    solution.totalScore += user_data.arcPreferences[current_node][0]

    return solution

def calculate_score_and_time(instance_data: InstanceData, user_data: UserData, order_nodes_visited: List[int]) -> List[int]:
    """
    Calcula el tiempo total y la puntuación total de una solución, y verifica restricciones.

    Args:
    - instance_data: instancia del grafo
    - user_data: datos de un usuario
    - order_nodes_visited: recorrido propuesto

    Return:
    - [tiempo_total, puntuacion_total], o [MAX_INT, -1] si hay arcos no conectados.
    """
    total_time = 0
    total_score = 0
    num_nodes = len(order_nodes_visited)

    # Verificación de arcos entre nodos
    for i in range(num_nodes - 1):
        u = order_nodes_visited[i]
        v = order_nodes_visited[i + 1]
        if instance_data.arcTimes[u][v] == -1:
            return [np.iinfo(np.int32).max, -1]
        total_time += instance_data.arcTimes[u][v]
        total_score += user_data.arcPreferences[u][v]

    # Verificar regreso al nodo inicial
    last = order_nodes_visited[-1]
    first = order_nodes_visited[0]
    if instance_data.arcTimes[last][first] == -1:
        return [np.iinfo(np.int32).max, -1]
    total_time += instance_data.arcTimes[last][first]
    total_score += user_data.arcPreferences[last][first]

    # Agregar tiempo y score de los nodos
    for node in order_nodes_visited:
        total_time += instance_data.nodeTimes[node]
        total_score += user_data.nodePreferences[node]

    return [total_time, total_score]


def insert_move(route: List[int], instance_data: InstanceData, user_data: UserData,
                best_score: int, best_time: int, first_improvement: bool = False
               ) -> Tuple[List[int], int, int, bool]:
    """
    Realiza un movimiento de inserción de un nodo en la ruta.

    Args:
    - route: ruta actual.
    - instance_data: datos del grafo.
    - user_data: preferencias del usuario.
    - best_score: mejor puntuación encontrada.
    - best_time: mejor tiempo encontrado.
    - best_move_found: indica si se encontró un movimiento mejor.
    - best_route: mejor ruta encontrada.

    Return:
    - mejor ruta, mejor puntuación, mejor tiempo, si se encontró un movimiento mejor.
    """
    best_route = route
    best_move_found = False

    for i in range(1, len(route)):
        for node in range(instance_data.numNodes):
            if node not in route:
                new_route = route[:i] + [node] + route[i:]
                new_time, new_score = calculate_score_and_time(instance_data, user_data, new_route)
                if new_score > best_score and new_time <= user_data.totalTime:
                    best_score = new_score
                    best_time = new_time
                    best_route = new_route
                    best_move_found = True
                    if first_improvement:
                        return best_route, best_score, best_time, True
    return best_route, best_score, best_time, best_move_found


def remove_move(route: List[int], instance_data: InstanceData, user_data: UserData,
                best_score: int, best_time: int, first_improvement: bool = False
               ) -> Tuple[List[int], int, int, bool]:
    """
    Realiza un movimiento de eliminación de un nodo en la ruta.

    Args:
    - route: ruta actual.
    - instance_data: datos del grafo.
    - user_data: preferencias del usuario.
    - best_score: mejor puntuación encontrada.
    - best_time: mejor tiempo encontrado.
    - best_move_found: indica si se encontró un movimiento mejor.
    - best_route: mejor ruta encontrada.

    Return:
    - mejor ruta, mejor puntuación, mejor tiempo, si se encontró un movimiento mejor.
    """
    best_route = route
    best_move_found = False

    for i in range(1, len(route)):
        new_route = route[:i] + route[i+1:]
        new_time, new_score = calculate_score_and_time(instance_data, user_data, new_route)
        if new_score > best_score and new_time <= user_data.totalTime:
            best_score = new_score
            best_time = new_time
            best_route = new_route
            best_move_found = True
            if first_improvement:
                return best_route, best_score, best_time, True
    return best_route, best_score, best_time, best_move_found


def swap_move(route: List[int], instance_data: InstanceData, user_data: UserData,
                best_score: int, best_time: int, first_improvement: bool = False
               ) -> Tuple[List[int], int, int, bool]:
    """
    Realiza un movimiento de intercambio entre dos nodos en la ruta.

    Args:
    - route: ruta actual.
    - instance_data: datos del grafo.
    - user_data: preferencias del usuario.
    - best_score: mejor puntuación encontrada.
    - best_time: mejor tiempo encontrado.
    - best_move_found: indica si se encontró un movimiento mejor.
    - best_route: mejor ruta encontrada.

    Return:
    - mejor ruta, mejor puntuación, mejor tiempo, si se encontró un movimiento mejor.
    """
    best_route = route
    best_move_found = False

    for i in range(1, len(route)):
        for j in range(i + 1, len(route)):
            new_route = route[:]
            new_route[i], new_route[j] = new_route[j], new_route[i]
            new_time, new_score = calculate_score_and_time(instance_data, user_data, new_route)
            if new_score > best_score and new_time <= user_data.totalTime:
                best_score = new_score
                best_time = new_time
                best_route = new_route
                best_move_found = True
                if first_improvement:
                    return best_route, best_score, best_time, True
    return best_route, best_score, best_time, best_move_found


def two_opt_move(route: List[int], instance_data: InstanceData, user_data: UserData,
                best_score: int, best_time: int, first_improvement: bool = False
               ) -> Tuple[List[int], int, int, bool]:
    best_route = route
    best_move_found = False

    for i in range(1, len(route) - 1):
        for j in range(i + 1, len(route)):
            new_route = route[:i] + route[i:j+1][::-1] + route[j+1:]
            new_time, new_score = calculate_score_and_time(instance_data, user_data, new_route)
            if new_score > best_score and new_time <= user_data.totalTime:
                best_score = new_score
                best_time = new_time
                best_route = new_route
                best_move_found = True
                if first_improvement:
                    return best_route, best_score, best_time, True
    return best_route, best_score, best_time, best_move_found


def move_node_forward(route: List[int], instance_data: InstanceData, user_data: UserData,
                best_score: int, best_time: int, first_improvement: bool = False
               ) -> Tuple[List[int], int, int, bool]:
    best_route = route
    best_move_found = False

    for i in range(2, len(route)):  # solo mover desde posición 2 en adelante
        for j in range(1, i):
            new_route = route[:]
            node = new_route.pop(i)
            new_route.insert(j, node)
            new_time, new_score = calculate_score_and_time(instance_data, user_data, new_route)
            if new_score > best_score and new_time <= user_data.totalTime:
                best_score = new_score
                best_time = new_time
                best_route = new_route
                best_move_found = True
                if first_improvement:
                    return best_route, best_score, best_time, True
    return best_route, best_score, best_time, best_move_found


def move_node_backward(route: List[int], instance_data: InstanceData, user_data: UserData,
                best_score: int, best_time: int, first_improvement: bool = False
               ) -> Tuple[List[int], int, int, bool]:
    best_route = route
    best_move_found = False

    for i in range(1, len(route) - 1):
        for j in range(i + 1, len(route)):
            new_route = route[:]
            node = new_route.pop(i)
            new_route.insert(j, node)
            new_time, new_score = calculate_score_and_time(instance_data, user_data, new_route)
            if new_score > best_score and new_time <= user_data.totalTime:
                best_score = new_score
                best_time = new_time
                best_route = new_route
                best_move_found = True
                if first_improvement:
                    return best_route, best_score, best_time, True
    return best_route, best_score, best_time, best_move_found


def replace_node(route: List[int], instance_data: InstanceData, user_data: UserData,
                best_score: int, best_time: int, first_improvement: bool = False
               ) -> Tuple[List[int], int, int, bool]:
    best_route = route
    best_move_found = False

    for i in range(1, len(route)):
        for candidate in range(instance_data.numNodes):
            if candidate not in route:
                new_route = route[:]
                new_route[i] = candidate
                new_time, new_score = calculate_score_and_time(instance_data, user_data, new_route)
                if new_score > best_score and new_time <= user_data.totalTime:
                    best_score = new_score
                    best_time = new_time
                    best_route = new_route
                    best_move_found = True
                    if first_improvement:
                        return best_route, best_score, best_time, True
    return best_route, best_score, best_time, best_move_found




def hill_climbing(solution: Solution, instance_data: InstanceData, user_data: UserData, moves: List[Callable]) -> Tuple[Solution, List[str]]:
    """
    Ejecuta Hill Climbing con las funciones de movimiento especificadas.

    Args:
    - solution: solución inicial.
    - instance_data: datos del grafo.
    - user_data: preferencias del usuario.
    - moves: lista de funciones de movimiento a aplicar.

    Return:
    - Solución mejorada.
    """
    improved = True
    list_moves_found = []
    best_move = None
    while improved:
        improved = False

        current_score = solution.totalScore
        current_time = solution.totalTimeUsed
        current_route = solution.orderNodesVisited[:]

        best_score = current_score
        best_time = current_time
        best_route = current_route
        best_move_found = False

        for move in moves:
            candidate_route, candidate_score, candidate_time, move_found = move(
                current_route, instance_data, user_data, best_score, best_time
            )
            if move_found and candidate_score > best_score:
                best_score = candidate_score
                best_time = candidate_time
                best_route = candidate_route
                best_move_found = True
                best_move = move.__name__

        if best_move_found:
            improved = True
            solution.totalScore = best_score
            solution.totalTimeUsed = best_time
            solution.orderNodesVisited = best_route
            list_moves_found.append(best_move)
            

    return solution, list_moves_found


def hill_climbing_first_improvement(solution: Solution, instance_data: InstanceData, user_data: UserData, moves: List[Callable]) -> Tuple[Solution, List[str]]:
    """
    Algoritmo Hill Climbing usando alguna mejora (first improvement).

    Retorna la primera mejora encontrada por los movimientos dados.
    """
    improved = True
    list_moves_found = []
    while improved:
        improved = False

        current_score = solution.totalScore
        current_time = solution.totalTimeUsed
        current_route = solution.orderNodesVisited[:]

        for move in moves:
            new_route, new_score, new_time, move_found = move(
                current_route, instance_data, user_data, current_score, current_time, first_improvement=True
            )
            if move_found:
                solution.totalScore = new_score
                solution.totalTimeUsed = new_time
                solution.orderNodesVisited = new_route
                improved = True
                list_moves_found.append(move.__name__)
                break  # Reinicia desde el primer movimiento

    return solution, list_moves_found


def simulated_annealing(solution: Solution,
                        instance_data: InstanceData,
                        user_data: UserData,
                        moves: List[Callable],
                        initial_temperature: float = 100.0,
                        cooling_rate: float = 0.995,
                        min_temperature: float = 1e-3,
                        max_iterations: int = 1000) -> Tuple[Solution, List[str]]:
    """
    Ejecuta el algoritmo Simulated Annealing sobre una solución dada.

    Retorna:
    - Tupla con la mejor solución encontrada y lista de movimientos que causaron mejoras.
    """
    current_solution = solution
    best_solution = solution
    move_history = []

    current_temp = initial_temperature
    iteration = 0

    while current_temp > min_temperature and iteration < max_iterations:
        move = random.choice(moves)
        new_route, new_score, new_time, improved = move(
            current_solution.orderNodesVisited,
            instance_data,
            user_data,
            current_solution.totalScore,
            current_solution.totalTimeUsed,
            first_improvement=True  # se usa estilo de alguna mejora
        )

        if improved:
            delta = new_score - current_solution.totalScore
            if delta > 0 or random.random() < np.exp(delta / current_temp):
                current_solution.orderNodesVisited = new_route
                current_solution.totalScore = new_score
                current_solution.totalTimeUsed = new_time
                move_history.append(move.__name__)
                if new_score > best_solution.totalScore:
                    best_solution = current_solution

        current_temp *= cooling_rate
        iteration += 1

    return best_solution, move_history


def tabu_search(solution: Solution,
                instance_data: InstanceData,
                user_data: UserData,
                moves: List[Callable],
                max_iterations: int = 100,
                tabu_tenure: int = 10,
                max_no_improve: int = 20,
                verbose: bool = False) -> Tuple[Solution, List[str]]:
    """
    Ejecuta el algoritmo Tabu Search.

    Args:
    - solution: solución inicial.
    - instance_data: datos de la instancia.
    - user_data: preferencias del usuario.
    - moves: lista de funciones de movimiento.
    - max_iterations: número máximo de iteraciones.
    - tabu_tenure: número de iteraciones que una solución permanece en la lista tabu.
    - max_no_improve: número máximo de iteraciones sin mejora antes de detener.
    - verbose: si es True, imprime información detallada por consola.

    Return:
    - Mejor solución encontrada y lista de movimientos aplicados.
    """
    current_solution = Solution(
        orderNodesVisited=solution.orderNodesVisited[:],
        totalScore=solution.totalScore,
        totalTimeUsed=solution.totalTimeUsed
    )
    best_solution = current_solution
    tabu_list = deque(maxlen=tabu_tenure)
    move_history = []

    no_improve_count = 0
    iteration = 0

    while iteration < max_iterations and no_improve_count < max_no_improve:
        best_candidate = None
        best_candidate_score = -1
        best_candidate_move = None

        if verbose:
            print(f"\n--- Iteración {iteration} ---")
            print(f"Score actual: {current_solution.totalScore} | Mejor global: {best_solution.totalScore}")

        for move in moves:
            candidate_route, candidate_score, candidate_time, move_found = move(
                current_solution.orderNodesVisited,
                instance_data,
                user_data,
                current_solution.totalScore,
                current_solution.totalTimeUsed
            )

            if not move_found:
                continue

            # Mostrar el mejor vecino por tipo de movimiento
            if verbose:
                print(f"Vecino generado con {move.__name__}: score={candidate_score}")

            # Aplicar criterios Tabú y global
            is_tabu = candidate_route in tabu_list
            improves_best = candidate_score > best_solution.totalScore

            if is_tabu and not improves_best:
                continue

            if candidate_score > best_candidate_score and candidate_time <= user_data.totalTime:
                best_candidate = Solution(candidate_route, candidate_score, candidate_time)
                best_candidate_score = candidate_score
                best_candidate_move = move.__name__

        if best_candidate is not None:
            current_solution = best_candidate
            tabu_list.append(best_candidate.orderNodesVisited)
            move_history.append(best_candidate_move)

            if verbose:
                print(f"Aplicando movimiento: {best_candidate_move}")
                print(f"Nuevo score actual: {current_solution.totalScore}")
                print(f"Lista Tabú actual: {list(tabu_list)}")

            if current_solution.totalScore > best_solution.totalScore:
                best_solution = current_solution
                no_improve_count = 0
                if verbose:
                    print("¡Nueva mejor solución encontrada!")
            else:
                no_improve_count += 1
        else:
            if verbose:
                print("No se encontraron vecinos válidos. Aumentando contador de no mejora.")
            no_improve_count += 1

        iteration += 1

    return best_solution, move_history

import numpy as np
from dataclasses import dataclass
from typing import List
import sys
from models import UserData, InstanceData, Solution

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

    Argumentos:
    - filename: Ruta del archivo de usuarios.
    - num_nodes: Número de nodos (tamaño de las matrices esperadas).

    Retorna:
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

from dataclasses import dataclass
from typing import List
import numpy as np

@dataclass
class Solution:
    orderNodesVisited: List[int]
    totalScore: int
    totalTimeUsed: int

def search_node(node: int, order_nodes_visited: List[int]) -> bool:
    """
    Verifica si un nodo ya fue visitado.

    Argumentos:
    - node: nodo a verificar.
    - order_nodes_visited: lista de nodos ya visitados.

    Retorna:
    - True si el nodo ya está en la lista, False si no.
    """
    return node in order_nodes_visited

def generate_solution(instance_data: InstanceData, user_data: UserData) -> Solution:
    """
    Genera una solución inicial greedy basada en eficiencia de puntuación-tiempo.

    Argumentos:
    - instance_data: datos del grafo.
    - user_data: preferencias de un usuario.

    Retorna:
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

    Argumentos:
    - instance_data: instancia del grafo
    - user_data: datos de un usuario
    - order_nodes_visited: recorrido propuesto

    Retorna:
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


def hill_climbing(solution: Solution, instance_data: InstanceData, user_data: UserData) -> Solution:
    """
    Mejora una solución utilizando Hill Climbing con estrategia de mejor mejora.

    Argumentos:
    - solution: solución inicial
    - instance_data: datos del grafo
    - user_data: preferencias del usuario

    Retorna:
    - Solución mejorada o la misma si no hay mejoras.
    """
    improved = True
    while improved:
        improved = False

        current_score = solution.totalScore
        current_time = solution.totalTimeUsed
        current_route = solution.orderNodesVisited[:]

        best_score = current_score
        best_time = current_time
        best_route = current_route[:]
        best_move_found = False

        # INSERT
        for i in range(1, len(current_route)):
            for node in range(instance_data.numNodes):
                if node not in current_route:
                    new_route = current_route[:i] + [node] + current_route[i:]
                    new_time, new_score = calculate_score_and_time(instance_data, user_data, new_route)
                    if new_score > best_score and new_time <= user_data.totalTime:
                        best_score = new_score
                        best_time = new_time
                        best_route = new_route
                        best_move_found = True

        # REMOVE
        for i in range(1, len(current_route)):
            new_route = current_route[:i] + current_route[i+1:]
            new_time, new_score = calculate_score_and_time(instance_data, user_data, new_route)
            if new_score > best_score and new_time <= user_data.totalTime:
                best_score = new_score
                best_time = new_time
                best_route = new_route
                best_move_found = True

        # SWAP
        for i in range(1, len(current_route)):
            for j in range(i + 1, len(current_route)):
                new_route = current_route[:]
                new_route[i], new_route[j] = new_route[j], new_route[i]
                new_time, new_score = calculate_score_and_time(instance_data, user_data, new_route)
                if new_score > best_score and new_time <= user_data.totalTime:
                    best_score = new_score
                    best_time = new_time
                    best_route = new_route
                    best_move_found = True

        if best_move_found:
            improved = True
            solution.totalScore = best_score
            solution.totalTimeUsed = best_time
            solution.orderNodesVisited = best_route

    return solution
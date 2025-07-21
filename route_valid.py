from typing import List
from models import InstanceData, UserData
import functions as f
import sys


def is_route_valid(route: List[int],
                   instance_data: InstanceData,
                   user_data: UserData,
                   verbose: bool = False
                  ) -> bool:
    """
    Valida si una ruta es factible para un usuario dado.

    Args:
    - route: lista de nodos visitados.
    - instance_data: datos de la instancia.
    - user_data: datos del usuario (incluye tiempo máximo).
    - verbose: si True, imprime detalles de los errores encontrados.

    Return:
    - True si la ruta es válida, False en caso contrario.
    """
    if not route or route[0] != 0:
        if verbose:
            print("❌ Ruta inválida: no comienza en el nodo inicial 0.")
        return False

    if any(node < 0 or node >= instance_data.numNodes for node in route):
        if verbose:
            print("❌ Ruta inválida: contiene nodos fuera del rango válido.")
        return False

    total_time, total_score = f.calculate_score_and_time(instance_data, user_data, route)

    if total_time > user_data.totalTime:
        if verbose:
            print(f"❌ Ruta inválida: tiempo total {total_time} > máximo permitido {user_data.totalTime}.")
        return False

    if len(route) != len(set(route)):
        if verbose:
            print("⚠️ Advertencia: la ruta contiene nodos repetidos.")
        # Dependiendo del problema, esto puede ser válido o no.
        # Aquí no lo invalidamos pero se advierte.

    if verbose:
        print(f"✅ Ruta válida: score = {total_score}, tiempo = {total_time}")

    return True



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

    routes =[
    [0, 40, 36, 37],
[0, 4, 2, 15, 40, 42, 45, 44, 41, 47, 46, 43],
[0, 20, 27, 52, 50, 49, 48, 51, 33, 5, 8, 22, 21, 19, 28, 4, 2, 17, 11, 36, 40, 38, 45, 44, 41, 46, 43, 47, 42, 37, 10, 12, 13, 34, 32, 31, 26, 29, 3],
[0, 40, 44, 34, 52, 48, 50, 49, 33, 32, 26, 27, 7, 5, 9, 8, 6, 14, 13, 10, 36, 21, 39, 4, 2, 20, 22, 41, 47, 42, 46, 45, 43, 28, 29, 17, 37, 18, 1, 12, 11, 3, 38],
[0, 40, 38, 4, 2],
[0, 40, 19, 26, 7, 5, 6, 9, 8, 51, 52, 1, 46, 37, 38, 44, 34, 50, 48, 49, 10, 14, 15, 17, 22, 20, 21, 47, 41, 42, 43, 45, 13, 11, 12, 36, 18, 27, 29, 28, 32, 33, 31, 30, 39, 4, 2, 16, 3],
[0, 36, 32, 26, 27, 29, 28, 31, 21, 23, 5, 6, 8, 2, 4, 15, 50, 48, 49, 52, 51, 24, 20, 39, 38, 37, 44, 43, 41, 46, 17, 11, 3, 1, 42, 47, 45, 10, 12, 9, 33, 30, 14, 22, 40],
[0, 4, 34, 50, 52, 51, 49, 48, 15, 40, 35, 29, 26, 27, 28, 20, 7, 6, 33, 31, 30, 9, 8, 12, 17, 2, 3, 38, 19, 18, 11, 10, 16, 23, 21, 24, 22, 44, 41, 42, 45, 46, 43, 47, 37, 39, 36, 14, 13],
[0, 44, 34, 43, 9, 38, 4, 25, 33, 28, 49, 18, 31, 19, 30, 40, 35, 22, 21, 42, 3, 37, 14, 20, 12, 13, 36, 1, 41, 5, 10, 45, 2, 47, 15, 11, 39, 17, 46, 24, 32, 16, 6, 51, 52, 29, 26, 7, 27, 23, 50, 48, 8],
[0, 11, 34, 52, 51, 48, 49, 50, 32, 31, 26, 29, 27, 28, 20, 21, 23, 46, 41, 44, 39, 38, 36, 37, 40, 4, 22, 3, 2, 42, 47, 43, 45],
[0, 8, 32, 44, 39, 41, 36, 38, 52, 49, 1, 16, 45, 34, 40, 11, 21, 25, 35, 12, 47, 17, 30, 3, 13, 15, 7, 6, 31, 27, 37, 4, 50, 2, 23, 46, 20, 24, 22, 51, 26, 14, 19, 43, 42, 28, 9, 18, 33, 29, 5, 10, 48],
[0, 3, 42, 41, 43, 46, 45, 47, 44, 34, 50, 52, 48, 29, 28, 26, 12, 35, 40, 21, 20, 36, 38, 37, 18, 9, 7, 5, 10, 4, 22, 19, 1, 2],
[0, 4, 9, 33, 30, 3, 2, 36, 37, 40, 42, 47, 43, 7, 51, 48, 52, 50, 12, 45, 46, 44, 34, 32, 31, 26, 29, 20, 21, 24, 22],
[0, 11, 14, 17, 20, 6, 9, 8, 5, 34, 50, 48, 51, 49, 52, 29, 12, 35, 32, 31, 33, 26, 28, 25, 27, 45, 47, 44, 41, 46, 43, 42, 3, 16, 15, 37, 40, 38, 36, 23, 22, 21, 39, 1, 2, 13, 10, 4, 18],
[0, 44, 51, 3, 40, 16, 46, 47, 34, 35, 20, 27, 41, 21, 38, 50, 6, 49, 12, 1, 18, 37, 8, 43, 31, 22, 36, 45, 25, 19, 39, 24, 11, 13, 17, 32, 4, 42, 5, 28, 9, 29, 2, 10, 30, 15, 26, 14, 23, 48, 52, 7, 33],
[0, 18, 36, 19, 12, 1, 31, 50, 29, 7, 48, 27, 35, 3, 44, 52, 34, 32, 47, 24, 9, 37, 6, 21, 39, 8, 42, 10, 23, 30, 11, 51, 41, 20, 26, 46, 49, 45, 43, 25, 13, 5, 2, 38, 28, 16, 4, 40, 17, 15, 33, 14, 22],
[0, 11, 2, 32, 21, 14, 36, 17, 33, 25, 29, 28, 27, 7, 12, 38, 18, 39, 40, 13, 41, 43, 44, 45, 3, 16, 9, 48, 52, 37, 8, 24, 20, 22, 47, 23, 31, 26, 1, 4, 10, 15, 50, 49, 51, 46, 42, 35, 19, 6, 5, 34, 30],
[0, 36, 32, 33, 31, 26, 27, 29, 28, 3, 2, 17, 10, 12, 38, 45, 41, 42, 46, 37, 40, 4],
[0, 17, 5, 34, 16, 36, 46, 32, 40, 38, 44, 23, 52, 13, 11, 18, 19, 50, 20, 9, 27, 51, 48, 37, 49, 45, 12, 6, 39, 21, 22, 7, 8, 1, 25, 33, 41, 15, 42, 10, 14, 24, 2, 28, 30, 29, 35, 47, 3, 31, 26, 4, 43],
[0, 36, 32, 33, 31, 26, 27, 29, 28, 52, 51, 49, 24, 22, 42, 41, 47, 46, 20, 39, 37, 40, 4, 3, 2, 1, 7, 6, 5, 9]
]

    for user_index, user_data in enumerate(user_data_list):
        route = routes[user_index % len(routes)]
        is_route_valid(route, instance_data, user_data, verbose=True)
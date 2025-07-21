# -*- coding: utf-8 -*-
import sys
import time
import numpy as np
import pandas as pd
import functions as f
from typing import Dict
from models import Solution


def run_all_metaheuristics(instance_data, user_data) -> Dict[str, int]:
    """
    Ejecuta todas las combinaciones deseadas de metaheurísticas y movimientos.

    Args:
    - initial_solution: solución inicial (tipo Solution).
    - instance_data: instancia de datos del problema.
    - user_data: datos del usuario.

    Return:
    - Diccionario con nombre de configuración y puntuación resultante.
    """
    results = {}

    # Combinaciones ejemplo
    configs = {
        "HC_MM1": (f.hill_climbing, [f.insert_move, f.remove_move, f.swap_move]),
        "HC_MM2": (f.hill_climbing, [ f.insert_move, f.remove_move, f.swap_move, f.two_opt_move, f.move_node_forward, f.move_node_backward, f.replace_node]),
        "HC_FI1": (f.hill_climbing_first_improvement,  [f.two_opt_move, f.move_node_forward, f.insert_move, f.swap_move, f.move_node_backward, f.remove_move, f.replace_node]),
        "HC_FI2": (f.hill_climbing_first_improvement,  [f.replace_node, f.remove_move, f.move_node_backward, f.swap_move, f.insert_move, f.move_node_forward, f.two_opt_move]),
        "HC_FI3": (f.hill_climbing_first_improvement,  [f.replace_node, f.remove_move, f.move_node_backward,  f.move_node_forward, f.swap_move, f.insert_move, f.two_opt_move]),

        
    }

    for name, meta in configs.items():
        func = meta[0]
        moves = meta[1]
        params = meta[2] if len(meta) > 2 else {}
        initial_solution = f.generate_solution(instance_data, user_data)

        improved_solution, _ = func(initial_solution, instance_data, user_data, moves, **params)
        results[name] = improved_solution.totalScore

    return results


def main():
    if len(sys.argv) < 3:
        print(f"Uso: python {sys.argv[0]} <instancia> <usuarios>")
        sys.exit(1)

    instancia_path = sys.argv[1] + ".txt"
    usuarios_path = sys.argv[2] + ".txt"

    print("Cargando datos...")
    instance_data = f.read_instance_file(instancia_path)
    user_data_list = f.read_user_data_file(usuarios_path, instance_data.numNodes)
    print(f"{len(user_data_list)} usuarios cargados.")

    resultados = []

    for user_id, user_data in enumerate(user_data_list):

        print(f"Usuario {user_id} con datos: {len(user_data.nodePreferences)} nodos.")

        features = f.extract_user_features(user_data, instance_data)
        metaheuristic_results = run_all_metaheuristics(instance_data, user_data)

        initial_solution = f.generate_solution(instance_data, user_data)
        row = {"user_id": user_id}
        row.update(features)
        row["initial_solution"] = initial_solution.totalScore
        row.update(metaheuristic_results)

        resultados.append(row)

    df = pd.DataFrame(resultados)
    output_name = f"analisis_{instance_data.numNodes}_instancias.csv"
    df.to_csv(output_name, index=False, sep=";")
    print(f"\nArchivo generado: {output_name}")


if __name__ == "__main__":
    main()

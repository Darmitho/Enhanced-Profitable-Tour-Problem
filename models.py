import numpy as np
from dataclasses import dataclass

@dataclass
class UserData:
    """
    Datos asociados a un usuario.
    
    Atributos:
        -totalTime: Tiempo total disponible del usuario (Integer).
        -nodePreference: Valorarión de cada nodo (array de enteros).
        - arcPreference: Valorarión de cada arco (array 2D de enteros).
    """
    totalTime: int
    nodePreferences: np.ndarray
    arcPreferences: np.ndarray

@dataclass
class InstanceData:
    """
    Datos asociado al grafo de la instancia.

    Atributos:
        -numNodes: Cantidad de nodos (Integer).
        -nodeTime: Tiempo de cada nodo (array de enteros).
        -arcTime: Tiempo de cada arco (array 2D de enteros).
    """
    numNodes: int
    nodeTimes: np.ndarray
    arcTimes: np.ndarray

@dataclass
class Solution:
    """
    Solución del problema de optimización.
    
    Atributos:
        -orderVisitedNodes: Orden de nodos visitados (array de enteros).
        -totalScore: Puntaje total de la solución (Integer).
        -totalTimeUsed: Tiempo total de la solución (Integer).
    """
    orderNodesVisited: np.ndarray
    totalScore: int
    totalTimeUsed: int
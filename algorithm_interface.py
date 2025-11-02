"""
8-Puzzle Solver Interface
This module provides a unified interface to run all search algorithms
and compare their performance including search depth metrics.
"""

import time
import os
from datetime import datetime

# Import all algorithm modules
import BFS
import DFS
import IDS
import AStar

def bfs(start, goal):
    """Wrapper around BFS.bfs that augments the result with search depth info."""
    result = BFS.bfs(start, goal)
    return result


def dfs(start, goal):
    """Wrapper around DFS.dfs that augments the result with search depth info."""
    result = DFS.dfs(start, goal)
    return result


def ids(start, goal):
    """Wrapper around IDS.ids that augments the result with search depth info."""
    result = IDS.ids(start, goal)
    return result


def astar(start, goal, heuristic):
    """Wrapper around AStar.astar that augments the result with search depth info."""
    result = AStar.astar(start, goal, heuristic)
    return result

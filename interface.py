"""
This module previously defined a Solver base class for the 8-puzzle solvers.
The solvers have been refactored to use standalone functions instead of classes.

All solver functions now accept (start, goal) tuples in 1D format (9 elements)
and return a dictionary with keys: 'path', 'cost', 'nodes_expanded', 'depth', 'time'

Available solvers:
- dfs: Depth-First Search (in puzzle_solver.py)
- ids: Iterative Deepening Search (in puzzle_solver.py)
- bfs: Breadth-First Search (in BFS.py)
- astar: A* Search with Manhattan or Euclidean heuristic (in AStar.py)
"""

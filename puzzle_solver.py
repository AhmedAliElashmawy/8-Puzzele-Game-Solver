import time
from collections import deque
from BFS import bfs
from AStar import astar


def get_neighbors(state):
    neighbors = []
    zero_index = state.index(0)
    row, col = divmod(zero_index, 3)

    moves = {
        'up': (row - 1, col),
        'down': (row + 1, col),
        'left': (row, col - 1),
        'right': (row, col + 1)
    }

    for move, (new_row, new_col) in moves.items():
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            new_state = list(state)
            new_state[zero_index], new_state[new_row * 3 + new_col] = new_state[new_row * 3 + new_col], new_state[zero_index]
            neighbors.append(tuple(new_state))
    return neighbors


def dfs(start, goal):
    start_time = time.time()
    start = tuple(start)
    goal = tuple(goal)

    if start == goal:
        end_time = time.time()
        return {
            'path': [start],
            'cost': 0,
            'nodes_expanded': 1,
            'depth': 0,
            'time': end_time - start_time
        }

    visited = set()
    nodes_expanded = 0
    stack = [start]
    parent = {start: None}

    found = False
    while stack:
        state = stack.pop()
        if state in visited:
            continue
        visited.add(state)
        nodes_expanded += 1

        if state == goal:
            found = True
            break

        for neighbor in get_neighbors(state):
            if neighbor not in visited and neighbor not in parent:
                parent[neighbor] = state
                stack.append(neighbor)

    path = []
    if found:
        cur = goal
        while cur is not None:
            path.append(cur)
            cur = parent.get(cur)
        path.reverse()

    end_time = time.time()
    return {
        'path': path,
        'cost': len(path) - 1 if path else -1,
        'nodes_expanded': nodes_expanded,
        'depth': len(path) - 1 if path else -1,
        'time': end_time - start_time
    }

def depth_limited_search(state, goal, limit, visited, nodes):
    nodes[0] += 1
    visited.add(state)
    if state == goal:
        return [state]
    if limit <= 0:
        return None

    for neighbor in get_neighbors(state):
        if neighbor not in visited:
            result = depth_limited_search(neighbor, goal, limit - 1, visited, nodes)
            if result is not None:
                return [state] + result
    return None

def ids(start, goal):
    start_time = time.time()
    depth = 0
    nodes_expanded = 0
    while True:
        start_t = tuple(start)
        goal_t = tuple(goal)
        visited = set()
        nodes = [0]
        path = depth_limited_search(start_t, goal_t, depth, visited, nodes)
        nodes_expanded += nodes[0]
        if path:
            end_time = time.time()
            return {
                'path': path,
                'cost': len(path) - 1,
                'nodes_expanded': nodes_expanded,
                'depth': depth,
                'time': end_time - start_time
            }
        depth += 1

import time
import heapq
import math


def get_neighbors(state):
    """Generate neighboring states by moving the blank tile (1D tuple format)."""
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


def _goal_positions(goal):
    """Map tile value -> (row, col) for goal state (1D tuple)."""
    position_map = {}
    for i, val in enumerate(goal):
        row, col = divmod(i, 3)
        position_map[val] = (row, col)
    return position_map


def _manhattan(state, goal_positions):
    """Calculate Manhattan distance heuristic (1D tuple)."""
    total_distance = 0
    for i, tile_value in enumerate(state):
        if tile_value == 0:
            continue
        row, col = divmod(i, 3)
        goal_row, goal_col = goal_positions[tile_value]
        total_distance += abs(row - goal_row) + abs(col - goal_col)
    return total_distance


def _euclidean(state, goal_positions):
    """Calculate Euclidean distance heuristic (1D tuple)."""
    total_distance = 0.0
    for i, tile_value in enumerate(state):
        if tile_value == 0:
            continue
        row, col = divmod(i, 3)
        goal_row, goal_col = goal_positions[tile_value]
        total_distance += math.hypot(row - goal_row, col - goal_col)
    return total_distance


def astar(start, goal, heuristic='manhattan'):
    """Solve using A* algorithm.

    Args:
        start: tuple (1D, 9 elements) representing the initial puzzle state
        goal: tuple (1D, 9 elements) representing the goal state
        heuristic: 'manhattan' or 'euclidean'
    
    Returns:
        dict with keys: 'path', 'cost', 'nodes_expanded', 'depth', 'time'
    """
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

    goal_positions = _goal_positions(goal)

    if heuristic == 'manhattan':
        heuristic_func = lambda state: _manhattan(state, goal_positions)
    elif heuristic == 'euclidean':
        heuristic_func = lambda state: _euclidean(state, goal_positions)
    else:
        raise ValueError("Unknown heuristic: {}".format(heuristic))

    open_heap = []  # elements are (f_score, g_score, state)
    g_score_map = {start: 0}
    f_score_map = {start: heuristic_func(start)}
    parent_map = {start: None}

    heapq.heappush(open_heap, (f_score_map[start], 0, start))

    closed_set = set()
    nodes_expanded = 0
    solution_found = False
    final_state = None

    while open_heap:
        f_score, g_score, current_state = heapq.heappop(open_heap)
        # skip if we've already processed a better g_score
        if current_state in closed_set:
            continue

        closed_set.add(current_state)
        nodes_expanded += 1

        if current_state == goal:
            solution_found = True
            final_state = current_state
            break

        for neighbor_state in get_neighbors(current_state):
            tentative_g_score = g_score + 1
            if neighbor_state in closed_set:
                continue
            if tentative_g_score < g_score_map.get(neighbor_state, float('inf')):
                parent_map[neighbor_state] = current_state
                g_score_map[neighbor_state] = tentative_g_score
                neighbor_f_score = tentative_g_score + heuristic_func(neighbor_state)
                heapq.heappush(open_heap, (neighbor_f_score, tentative_g_score, neighbor_state))

    end_time = time.time()

    if not solution_found:
        return {
            'path': [],
            'cost': -1,
            'nodes_expanded': nodes_expanded,
            'depth': -1,
            'time': end_time - start_time
        }

    # reconstruct path
    solution_path = []
    current_node = final_state
    while current_node is not None:
        solution_path.append(current_node)
        current_node = parent_map.get(current_node)
    solution_path.reverse()

    solution_cost = len(solution_path) - 1
    search_depth = solution_cost

    return {
        'path': solution_path,
        'cost': solution_cost,
        'nodes_expanded': nodes_expanded,
        'depth': search_depth,
        'time': end_time - start_time
    }


if __name__ == '__main__':
    # Test with 1D tuple format
    start_state = (1, 4, 2, 6, 5, 8, 7, 3, 0)
    goal_state = (0, 1, 2, 3, 4, 5, 6, 7, 8)
    
    print("Testing A* with Manhattan heuristic:")
    result = astar(start_state, goal_state, heuristic='manhattan')
    print(f"Cost: {result['cost']}, Nodes: {result['nodes_expanded']}, Time: {result['time']:.4f}s")
    print(f"Path length: {len(result['path'])}")
    
    print("\nTesting A* with Euclidean heuristic:")
    result = astar(start_state, goal_state, heuristic='euclidean')
    print(f"Cost: {result['cost']}, Nodes: {result['nodes_expanded']}, Time: {result['time']:.4f}s")
    print(f"Path length: {len(result['path'])}")


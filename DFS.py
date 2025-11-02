import time


def get_neighbors(state):
    """Generate neighboring states by moving the blank tile (1D tuple format)."""
    neighbors = []
    zero_index = state.index(0)
    row, col = divmod(zero_index, 3)

    moves = {
        'Up': (row - 1, col),
        'Down': (row + 1, col),
        'Left': (row, col - 1),
        'Right': (row, col + 1)
    }

    for move, (new_row, new_col) in moves.items():
        if 0 <= new_row < 3 and 0 <= new_col < 3:
            new_state = list(state)
            new_state[zero_index], new_state[new_row * 3 + new_col] = new_state[new_row * 3 + new_col], new_state[zero_index]
            neighbors.append((tuple(new_state), move))
    return neighbors


def dfs(start, goal, max_depth=50):
    """Solve the 8-puzzle using DFS with depth limit.

    Args:
        start: tuple (1D, 9 elements) representing the initial puzzle state
        goal: tuple (1D, 9 elements) representing the goal state
        max_depth: maximum depth to search (default 50)

    Returns:
        dict with keys: 'path', 'cost', 'nodes_expanded', 'depth', 'time', 'moves'
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
            'search_depth': 0,
            'time': end_time - start_time,
            "moves": []
        }

    visited = set()
    nodes_expanded = -1
    # Stack contains: (state, depth)
    stack = [(start, 0)]
    parent = {start: None}
    move_map = {start: None}
    depth_map = {start: 0}
    max_depth_reached = 0

    found = False
    final_state = None

    while stack:
        state, depth = stack.pop()
        
        if state in visited:
            continue
        
        visited.add(state)
        nodes_expanded += 1
        max_depth_reached = max(max_depth_reached, depth)

        if state == goal:
            found = True
            final_state = state
            break

        # Don't expand beyond max_depth
        if depth >= max_depth:
            continue

        for neighbor, move in get_neighbors(state):
            if neighbor not in visited and neighbor not in parent:
                parent[neighbor] = state
                move_map[neighbor] = move
                depth_map[neighbor] = depth + 1
                stack.append((neighbor, depth + 1))

    end_time = time.time()

    if not found:
        return {
            'path': [],
            'cost': -1,
            'nodes_expanded': nodes_expanded,
            'search_depth': max_depth_reached,
            'time': end_time - start_time,
            'moves': []
        }

    # Reconstruct path and moves
    path = []
    moves = []
    cur = final_state
    while cur is not None:
        path.append(cur)
        if move_map.get(cur) is not None:
            moves.append(move_map[cur])
        cur = parent.get(cur)
    path.reverse()
    moves.reverse()

    solution_cost = len(path) - 1

    return {
        'path': path,
        'cost': solution_cost,
        'nodes_expanded': nodes_expanded,
        'search_depth': max_depth_reached,
        'time': end_time - start_time,
        'moves': moves
    }


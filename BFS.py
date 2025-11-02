from collections import deque
import time


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
            neighbors.append((tuple(new_state), move))
    return neighbors


def bfs(start, goal):
    """Solve the 8-puzzle using BFS.

    Args:
        start: tuple (1D, 9 elements) representing the initial puzzle state
        goal: tuple (1D, 9 elements) representing the goal state

    Returns:
        dict with keys: 'path', 'cost', 'nodes_expanded', 'depth', 'search_depth', 'time'
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
            'moves': []
        }

    frontier = deque([(start, 0)])  # (state, depth)
    parent_map = {start: None}
    move_map = {start: None}
    depth_map = {start: 0}
    nodes_expanded = -1
    solution_found = False
    max_depth_reached = 0

    while frontier:
        print(frontier)
        current_state, current_depth = frontier.popleft()
        print(current_depth)
        nodes_expanded += 1

        # update max depth with the node being expanded
        max_depth_reached = max(max_depth_reached, current_depth)

        for neighbor_state, move in get_neighbors(current_state):
            if neighbor_state not in parent_map:
                parent_map[neighbor_state] = current_state
                move_map[neighbor_state] = move
                neighbor_depth = current_depth + 1
                depth_map[neighbor_state] = neighbor_depth

                # update max depth with newly generated child (captures whole tree depth)
                max_depth_reached = max(max_depth_reached, neighbor_depth)

                frontier.append((neighbor_state, neighbor_depth))

        if current_state == goal:
            solution_found = True
            final_state = current_state
            frontier.clear()
            break

    end_time = time.time()

    if not solution_found:
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
        cur = parent_map.get(cur)
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

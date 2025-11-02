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
    start_time = time.time()
    start, goal = tuple(start), tuple(goal)

    if start == goal:
        return {
            'path': [start], 'cost': 0, 'nodes_expanded': 0,
            'search_depth': 0, 'time': 0, 'moves': []
        }

    frontier = deque([(start, 0)])
    parent_map = {start: None}
    move_map = {start: None}
    nodes_expanded = 0
    max_depth_reached = 0

    while frontier:
        current_state, current_depth = frontier.popleft()

        if current_state == goal:
            final_state = current_state
            break

        nodes_expanded += 1
        max_depth_reached = max(max_depth_reached, current_depth)

        for neighbor_state, move in get_neighbors(current_state):
            if neighbor_state not in parent_map:
                parent_map[neighbor_state] = current_state
                move_map[neighbor_state] = move
                frontier.append((neighbor_state, current_depth + 1))
                max_depth_reached = max(max_depth_reached, current_depth + 1)
    else:
        # goal not found
        return {
            'path': [], 'cost': -1, 'nodes_expanded': nodes_expanded,
            'search_depth': max_depth_reached, 'time': time.time() - start_time,
            'moves': []
        }

    # reconstruct path
    path, moves = [], []
    cur = final_state
    while cur is not None:
        path.append(cur)
        if move_map[cur]:
            moves.append(move_map[cur])
        cur = parent_map[cur]
    path.reverse()
    moves.reverse()

    return {
        'path': path,
        'cost': len(path) - 1,
        'nodes_expanded': nodes_expanded,
        'search_depth': max_depth_reached,
        'time': time.time() - start_time,
        'moves': moves
    }
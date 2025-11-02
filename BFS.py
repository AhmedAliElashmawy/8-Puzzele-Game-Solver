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
            neighbors.append(tuple(new_state))
    return neighbors


def bfs(start, goal):
    """Solve the 8-puzzle using BFS.

    Args:
        start: tuple (1D, 9 elements) representing the initial puzzle state
        goal: tuple (1D, 9 elements) representing the goal state

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

    frontier = deque([start])
    parent_map = {start: None}
    nodes_expanded = 0
    solution_found = False

    while frontier:
        current_state = frontier.popleft()
        nodes_expanded += 1
        for neighbor_state in get_neighbors(current_state):
            if neighbor_state not in parent_map:
                parent_map[neighbor_state] = current_state
                if neighbor_state == goal:
                    solution_found = True
                    final_state = neighbor_state
                    frontier.clear()
                    break
                frontier.append(neighbor_state)

    end_time = time.time()

    if not solution_found:
        return {
            'path': [],
            'cost': -1,
            'nodes_expanded': nodes_expanded,
            'depth': -1,
            'time': end_time - start_time
        }

    # Reconstruct path
    solution_path = []
    current_node = final_state
    while current_node is not None:
        solution_path.append(current_node)
        current_node = parent_map[current_node]
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
    
    print("Testing BFS:")
    result = bfs(start_state, goal_state)
    print(f"Cost: {result['cost']}, Nodes: {result['nodes_expanded']}, Time: {result['time']:.4f}s")
    print(f"Path length: {len(result['path'])}")

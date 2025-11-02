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


def depth_limited_search(state, goal, limit, visited, parent, move_map, nodes_count):
    """Depth-limited search helper function."""
    nodes_count[0] += 1
    
    if state == goal:
        return True
    
    if limit <= 0:
        return False
    
    visited.add(state)
    
    for neighbor, move in get_neighbors(state):
        if neighbor not in visited:
            parent[neighbor] = state
            move_map[neighbor] = move
            if depth_limited_search(neighbor, goal, limit - 1, visited, parent, move_map, nodes_count):
                return True
            # Backtrack: remove from parent if not on solution path
            if neighbor in parent and parent[neighbor] == state:
                del parent[neighbor]
                del move_map[neighbor]
    
    return False


def ids(start, goal, max_depth=50):
    """Solve the 8-puzzle using Iterative Deepening Search.

    Args:
        start: tuple (1D, 9 elements) representing the initial puzzle state
        goal: tuple (1D, 9 elements) representing the goal state
        max_depth: maximum depth to search (default 50)

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
            'search_depth': 0,
            'time': end_time - start_time,
            'moves': []
        }

    total_nodes_expanded = -1
    
    for depth_limit in range(max_depth + 1):
        visited = set()
        parent = {start: None}
        move_map = {start: None}
        nodes_count = [0]
        
        found = depth_limited_search(start, goal, depth_limit, visited, parent, move_map, nodes_count)
        total_nodes_expanded += nodes_count[0]
        
        if found:
            # Reconstruct path and moves
            path = []
            moves = []
            cur = goal
            while cur is not None:
                path.append(cur)
                if move_map.get(cur) is not None:
                    moves.append(move_map[cur])
                cur = parent.get(cur)
            path.reverse()
            moves.reverse()
            
            end_time = time.time()
            solution_cost = len(path) - 1
            
            return {
                'path': path,
                'cost': solution_cost,
                'nodes_expanded': total_nodes_expanded,
                'search_depth': depth_limit,
                'time': end_time - start_time,
                'moves': moves
            }
    
    
    end_time = time.time()
    return {
        'path': [],
        'cost': -1,
        'nodes_expanded': total_nodes_expanded,
        'search_depth': max_depth,
        'time': end_time - start_time,
        'moves': []
    }


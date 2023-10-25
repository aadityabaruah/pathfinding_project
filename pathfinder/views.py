from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.shortcuts import render
from queue import PriorityQueue
import math


def home(request):
    return render(request, 'pathfinder/home.html')


def parse_grid_data(grid):
    start, target, pickup, walls = None, None, None, set()
    n = int(len(grid) ** 0.5)
    for cell in grid:
        position = (cell['id'] // n, cell['id'] % n)
        if cell["isStart"]:
            start = position
        elif cell["isTarget"]:
            target = position
        elif cell["isPickup"]:
            pickup = position
        elif cell["isWall"]:
            walls.add(position)
    return start, target, pickup, walls, n


def compute_path_with_pickup(grid, algorithm_func):
    start, target, pickup, walls, n = parse_grid_data(grid)
    if not pickup:
        return algorithm_func(grid, start, target, walls)
    visited_cells_1, path_to_pickup = algorithm_func(grid, start, pickup, walls)
    visited_cells_2, path_from_pickup = algorithm_func(grid, pickup, target, walls)
    visited_cells = visited_cells_1 + visited_cells_2
    final_path = path_to_pickup + path_from_pickup
    return visited_cells, final_path


def reconstruct_path(came_from, current, n):
    path = []
    while current in came_from:
        path.append(current)
        current = came_from[current]
    path = [cell[0] * n + cell[1] for cell in path]
    return path


def get_neighbors(position, n):
    """Return the neighbors of a given position on the grid."""
    row, col = position
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    neighbors = [(row + dr, col + dc) for dr, dc in directions]
    valid_neighbors = [(r, c) for r, c in neighbors if 0 <= r < n and 0 <= c < n]
    return valid_neighbors


def heuristic(p1, p2):
    """Return the Euclidean distance between two points."""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def run_dijkstra_from_to(grid, start, end, walls):
    n = int(len(grid) ** 0.5)
    distances = {(row, col): float('inf') for row in range(n) for col in range(n)}
    distances[start] = 0
    priority_queue = PriorityQueue()
    priority_queue.put((0, start))
    came_from = {}
    visited_cells = []

    while not priority_queue.empty():
        _, current = priority_queue.get()

        if current == end:
            break

        for neighbor in get_neighbors(current, n):
            if neighbor in walls or neighbor in visited_cells:
                continue
            tentative_distance = distances[current] + 1
            if tentative_distance < distances[neighbor]:
                came_from[neighbor] = current
                distances[neighbor] = tentative_distance
                priority_queue.put((tentative_distance, neighbor))
                visited_cells.append(neighbor)

    path = reconstruct_path(came_from, end, n)
    visited_cells = [cell[0] * n + cell[1] for cell in visited_cells]
    return visited_cells, path


def run_astar_from_to(grid, start, end, walls):
    n = int(len(grid) ** 0.5)
    open_set = PriorityQueue()
    open_set.put((0, start))
    came_from = {}
    g_score = {(row, col): float('inf') for row in range(n) for col in range(n)}
    g_score[start] = 0
    f_score = {(row, col): float('inf') for row in range(n) for col in range(n)}
    f_score[start] = heuristic(start, end)
    visited_cells = []

    while not open_set.empty():
        _, current = open_set.get()

        if current == end:
            break

        for neighbor in get_neighbors(current, n):
            if neighbor in walls or neighbor in visited_cells:
                continue
            tentative_g_score = g_score[current] + 1
            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)
                open_set.put((f_score[neighbor], neighbor))
                visited_cells.append(neighbor)

    path = reconstruct_path(came_from, end, n)
    visited_cells = [cell[0] * n + cell[1] for cell in visited_cells]
    return visited_cells, path


def run_dijkstra(grid):
    return compute_path_with_pickup(grid, run_dijkstra_from_to)


def run_astar(grid):
    return compute_path_with_pickup(grid, run_astar_from_to)


@csrf_exempt
def compute_path(request):
    data = json.loads(request.body)
    grid = data.get('grid')
    algorithm = data.get('algorithm')
    visited_cells, final_path = [], []

    if algorithm == "dijkstra":
        visited_cells, final_path = run_dijkstra(grid)
    elif algorithm == "a_star":
        visited_cells, final_path = run_astar(grid)
    # Add more algorithms as needed

    return JsonResponse({
        'visited_cells': visited_cells,
        'final_path': final_path
    })

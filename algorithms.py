import heapq
from collections import deque
# 4-direction movement
DIRS = [(1,0),(-1,0),(0,1),(0,-1)]
# ------------- BFS -------------
def bfs(grid, start, end, draw_step):
    queue = deque([start])
    visited = {start}
    parent = {start: None}
    while queue:
        r, c = queue.popleft()
        draw_step((r, c), "open")
        if (r, c) == end:
            break
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                if grid[nr][nc] != 1 and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append((nr, nc))
                    parent[(nr, nc)] = (r, c)
    return reconstruct(parent, end)
# ------------- DFS -------------

def dfs(grid, start, end, draw_step):
    stack = [start]
    visited = {start}
    parent = {start: None}

    while stack:
        r, c = stack.pop()
        draw_step((r, c), "open")
        if (r, c) == end:
            break
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                if grid[nr][nc] != 1 and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    stack.append((nr, nc))
                    parent[(nr, nc)] = (r, c)

    return reconstruct(parent, end)
# ------------- A* -------------
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
def astar(grid, start, end, draw_step):
    pq = [(0, start)]
    g_cost = {start: 0}
    parent = {start: None}
    while pq:
        _, (r, c) = heapq.heappop(pq)
        draw_step((r, c), "open")
        if (r, c) == end:
            break
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                if grid[nr][nc] != 1:
                    new_g = g_cost[(r, c)] + 1
                    if new_g < g_cost.get((nr, nc), float('inf')):
                        g_cost[(nr, nc)] = new_g
                        f_cost = new_g + heuristic((nr, nc), end)
                        parent[(nr, nc)] = (r, c)
                        heapq.heappush(pq, (f_cost, (nr, nc)))
    return reconstruct(parent, end)
# ------------- Hill Climbing (Greedy Best-First) -------------

def hill_climbing(grid, start, end, draw_step):
    # Priority Queue stores only (heuristic, (r, c))
    # It ignores the cost to get there from the start!
    pq = [(heuristic(start, end), start)]
    visited = {start}
    parent = {start: None}
    while pq:
        # Always pop the node that strictly looks closest to the end
        _, (r, c) = heapq.heappop(pq)
        draw_step((r, c), "open")
        if (r, c) == end:
            break
        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                if grid[nr][nc] != 1 and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    parent[(nr, nc)] = (r, c)
                    # The Score is ONLY the distance to the end
                    h_score = heuristic((nr, nc), end)

                    heapq.heappush(pq, (h_score, (nr, nc)))

    return reconstruct(parent, end)

# ------------- RECONSTRUCT PATH -------------

def reconstruct(parent, end):
    path = []
    cur = end
    while cur in parent and cur is not None:
        path.append(cur)
        cur = parent[cur]
    path.reverse()
    return path
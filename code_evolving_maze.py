import random
from collections import deque

MAZE_SIZE = 10
WALL = 1
PATH = 0
PLAYER = 'P'
TREASURE = 'T'
POPULATION_SIZE = 10
MUTATION_RATE = 0.05

class Maze:
    def __init__(self, grid=None):
        self.grid = grid or self.generate_maze()
        self.start = (0, 0)
        self.end = (MAZE_SIZE - 1, MAZE_SIZE - 1)

    def generate_maze(self):
        return [[random.choice([WALL, PATH]) for _ in range(MAZE_SIZE)] for _ in range(MAZE_SIZE)]

    def is_valid(self, x, y):
        return 0 <= x < MAZE_SIZE and 0 <= y < MAZE_SIZE and self.grid[x][y] == PATH

    def display(self, player_pos):
        for i in range(MAZE_SIZE):
            row = ""
            for j in range(MAZE_SIZE):
                if (i, j) == player_pos:
                    row += PLAYER
                elif (i, j) == self.end:
                    row += TREASURE
                else:
                    row += "." if self.grid[i][j] == PATH else "#"
            print(row)
        print()

class GeneticMazeAI:
    def __init__(self):
        self.population = [Maze() for _ in range(POPULATION_SIZE)]

    def fitness(self, maze):
        return -self.bfs_distance(maze)

    def bfs_distance(self, maze):
        visited = set()
        queue = deque([(maze.start, 0)])
        while queue:
            (x, y), dist = queue.popleft()
            if (x, y) == maze.end:
                return dist
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x + dx, y + dy
                if maze.is_valid(nx, ny) and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), dist + 1))
        return float('inf')

    def evolve(self):
        while True:
            scored_population = [(self.fitness(m), m) for m in self.population]
            scored_population.sort(reverse=True, key=lambda x: x[0])
            best = [m for _, m in scored_population[:2]]
            new_population = best[:]
            while len(new_population) < POPULATION_SIZE:
                parent1, parent2 = random.sample(best, 2)
                child = self.crossover(parent1, parent2)
                self.mutate(child)
                new_population.append(child)
            self.population = new_population
            best_maze = scored_population[0][1]
            if self.has_valid_path(best_maze):
                return best_maze

    def crossover(self, m1, m2):
        new_grid = []
        for i in range(MAZE_SIZE):
            row = [random.choice([m1.grid[i][j], m2.grid[i][j]]) for j in range(MAZE_SIZE)]
            new_grid.append(row)
        return Maze(new_grid)

    def mutate(self, maze):
        for _ in range(5):  
            backup_grid = [row[:] for row in maze.grid]
            for i in range(MAZE_SIZE):
                for j in range(MAZE_SIZE):
                    if random.random() < MUTATION_RATE:
                        maze.grid[i][j] = PATH if maze.grid[i][j] == WALL else WALL
            maze.grid[0][0] = PATH
            maze.grid[MAZE_SIZE - 1][MAZE_SIZE - 1] = PATH
            if self.has_valid_path(maze):
                return
            else:
                maze.grid = backup_grid  

    def has_valid_path(self, maze):
        visited = set()
        queue = deque([maze.start])
        visited.add(maze.start)
        while queue:
            x, y = queue.popleft()
            if (x, y) == maze.end:
                return True
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                nx, ny = x + dx, y + dy
                if maze.is_valid(nx, ny) and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))
        return False

def manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def play_game():
    ai = GeneticMazeAI()
    maze = ai.evolve()
    player_pos = list(maze.start)
    last_distance = manhattan_distance(tuple(player_pos), maze.end)

    print("\nMaze generated! Use W/A/S/D to move. Reach the 'T'!")

    while True:
        maze.display(tuple(player_pos))
        move = input("Move (W/A/S/D): ").strip().upper()
        dx, dy = 0, 0
        if move == 'W': dx = -1
        elif move == 'S': dx = 1
        elif move == 'A': dy = -1
        elif move == 'D': dy = 1
        else:
            print("Invalid input! Use W, A, S, or D.")
            continue

        nx, ny = player_pos[0] + dx, player_pos[1] + dy
        if maze.is_valid(nx, ny):
            player_pos = [nx, ny]
            new_distance = manhattan_distance(tuple(player_pos), maze.end)
            if new_distance < last_distance:
                print("You're getting close... maze evolving!")
                ai.mutate(maze)
            last_distance = new_distance
        else:
            print("Can't move there! Wall or out of bounds.")

        if tuple(player_pos) == maze.end:
            maze.display(tuple(player_pos))
            print("\nYou reached the treasure! Game complete!")
            break

if __name__ == "__main__":
    play_game()

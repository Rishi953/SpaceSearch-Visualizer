# maze_generator.py
from mazelib import Maze
from mazelib.generate.BacktrackingGenerator import BacktrackingGenerator
def generate_maze(width=30, height=30):
    m = Maze()
    m.generator = BacktrackingGenerator(width, height)
    m.generate()
    return m.grid  # returns a 2D numpy array

if __name__ == "__main__":
    maze = generate_maze(10, 10)
    print(maze)
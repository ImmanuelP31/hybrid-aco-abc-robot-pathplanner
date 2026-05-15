"""
environment.py

This is basically the "world" the robot lives in.
Think of it like a big grid — some cells are open, some have obstacles.
The robot needs to get from Start to Goal without hitting anything.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches


class GridEnvironment:
    def __init__(self, size=50, obstacle_seed=42):
        self.size = size
        self.grid = np.zeros((size, size))  # 0 = open, 1 = obstacle

        # seed this so you get the same environment every run
        # (reproducibility — good science habit)
        np.random.seed(obstacle_seed)

        # default start and goal — bottom-left to top-right
        self.start = (5, 5)
        self.goal = (45, 45)

        self._place_obstacles()

    def _place_obstacles(self):
        """
        Plop some rectangular obstacles onto the grid.
        These are hardcoded to match the paper's test scenarios,
        but feel free to change them or randomize them.
        """
        obstacles = [
            # (x, y, width, height) — like bounding boxes
            (10, 10, 8, 18),   # left cluster
            (20, 20, 10, 10),  # middle blocker
            (30, 30, 12, 12),  # upper-right blocker
        ]

        for (x, y, w, h) in obstacles:
            # mark each cell inside the box as blocked
            for i in range(x, min(x + w, self.size)):
                for j in range(y, min(y + h, self.size)):
                    self.grid[i][j] = 1

        # make sure start and goal aren't accidentally blocked
        sx, sy = self.start
        gx, gy = self.goal
        self.grid[sx][sy] = 0
        self.grid[gx][gy] = 0

    def is_free(self, x, y):
        """Is this cell walkable? (i.e., not a wall)"""
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.grid[x][y] == 0
        return False  # out of bounds = no good

    def is_path_valid(self, path):
        """
        Check if an entire list of (x, y) waypoints is obstacle-free.
        If any point is in a wall, the whole path fails.
        """
        return all(self.is_free(x, y) for (x, y) in path)

    def distance(self, a, b):
        """
        Straight-line (Euclidean) distance between two grid points.
        Used as the heuristic — closer = more attractive.
        """
        return np.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

    def random_free_cell(self):
        """Pick a random cell that isn't blocked. Used for initializing bees/ants."""
        while True:
            x = np.random.randint(0, self.size)
            y = np.random.randint(0, self.size)
            if self.is_free(x, y):
                return (x, y)

    def plot(self, ax=None, show=True):
        """
        Draw the grid — obstacles in gray, start in green, goal in red star.
        Pass ax if you want to layer paths on top of this later.
        """
        if ax is None:
            fig, ax = plt.subplots(figsize=(8, 8))

        # draw obstacles
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == 1:
                    rect = patches.Rectangle(
                        (i, j), 1, 1,
                        linewidth=0, facecolor='#e0e0e0'
                    )
                    ax.add_patch(rect)

        # mark start and goal
        sx, sy = self.start
        gx, gy = self.goal
        ax.plot(sx, sy, 'go', markersize=12, label='Start', zorder=5)
        ax.plot(gx, gy, 'r*', markersize=15, label='Goal', zorder=5)

        ax.set_xlim(0, self.size)
        ax.set_ylim(0, self.size)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.2)
        ax.legend()

        if show:
            plt.show()

        return ax

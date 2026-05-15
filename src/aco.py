"""
aco.py

Ant Colony Optimization — the "ant" part of our hybrid.

Real ants find food by wandering around and leaving a chemical trail (pheromone).
Other ants sniff those trails and prefer stronger ones.
Over time, the best path gets reinforced and suboptimal ones fade away.

That's literally what we're doing here, but with code.
"""

import numpy as np
from src.fitness import evaluate


class AntColonyOptimizer:
    def __init__(self, env, config):
        self.env = env
        self.n_ants = config.get("num_ants", 20)
        self.alpha = config.get("alpha", 1.0)   # how much ants trust pheromone
        self.beta  = config.get("beta", 2.0)    # how much they trust "closer = better"
        self.rho   = config.get("evaporation_rate", 0.5)  # how fast pheromone evaporates
        self.Q     = config.get("Q", 100)        # how much pheromone a good ant deposits
        self.max_iter = config.get("max_iterations", 100)
        self.n_waypoints = config.get("n_waypoints", 20)  # intermediate stops on the path

        # start everyone off with equal pheromone (nobody knows anything yet)
        self.pheromone = {}
        self.best_path = None
        self.best_cost = float('inf')
        self.convergence_history = []

    def _random_waypoints(self):
        """
        Build a random candidate path from start → (random intermediate points) → goal.
        Each ant starts with a totally random path, then we refine from there.
        """
        path = [self.env.start]

        for _ in range(self.n_waypoints):
            # pick a random free cell anywhere in the grid
            cell = self.env.random_free_cell()
            path.append(cell)

        path.append(self.env.goal)
        return path

    def _pheromone_level(self, a, b):
        """Get pheromone on the edge from a to b. Default to 1.0 (neutral)."""
        key = (a, b)
        return self.pheromone.get(key, 1.0)

    def _heuristic(self, current, next_cell):
        """
        Closer to the goal = more attractive.
        This is the "common sense" part — ants prefer cells that seem useful.
        """
        dist = self.env.distance(next_cell, self.env.goal)
        return 1.0 / (dist + 1e-9)  # avoid division by zero

    def _build_path_for_ant(self):
        """
        One ant builds one path, probabilistically.
        At each step it picks the next waypoint based on:
          - how much pheromone is on that edge (learned from good ants before)
          - how close that cell is to the goal (built-in common sense)

        Roulette-wheel selection — cells with higher scores get picked more often,
        but it's still random. This keeps diversity in the population.
        """
        # start with some random candidates to choose between
        candidates = [self.env.random_free_cell() for _ in range(10)]
        path = [self.env.start]

        for _ in range(self.n_waypoints):
            current = path[-1]
            scores = []

            for c in candidates:
                tau = self._pheromone_level(current, c) ** self.alpha
                eta = self._heuristic(current, c) ** self.beta
                scores.append(tau * eta)

            total = sum(scores) + 1e-9
            probs = [s / total for s in scores]
            # numpy is picky — probabilities must sum to exactly 1.0
            # floating point rounding can throw it off, so we normalize again
            probs = np.array(probs, dtype=np.float64)
            probs /= probs.sum()

            # roulette wheel pick
            chosen_idx = np.random.choice(len(candidates), p=probs)
            chosen = candidates[chosen_idx]
            path.append(chosen)

            # refresh candidates for next step (new random options)
            candidates = [self.env.random_free_cell() for _ in range(10)]

        path.append(self.env.goal)
        return path

    def _update_pheromones(self, all_paths, all_costs):
        """
        After all ants are done:
        1. Evaporate existing pheromone (it fades over time — like in real life)
        2. Deposit new pheromone on edges used by good ants
           (Better path = more pheromone deposited)
        """
        # decay everything
        for key in self.pheromone:
            self.pheromone[key] *= (1 - self.rho)

        # reward the good ants
        for path, cost in zip(all_paths, all_costs):
            if cost > 0 and cost < float('inf'):
                deposit = self.Q / cost  # cheaper path → more pheromone
                for i in range(len(path) - 1):
                    key = (path[i], path[i+1])
                    self.pheromone[key] = self.pheromone.get(key, 1.0) + deposit

    def run(self, verbose=True):
        """
        Main loop. Each iteration:
          - Every ant builds a path
          - We score all paths
          - Update pheromones
          - Remember the best one seen so far
        """
        for iteration in range(self.max_iter):
            paths = []
            costs = []

            for _ in range(self.n_ants):
                path = self._build_path_for_ant()
                cost = evaluate(path, self.env)
                paths.append(path)
                costs.append(cost)

                # is this the best we've seen yet?
                if cost < self.best_cost:
                    self.best_cost = cost
                    self.best_path = path

            self._update_pheromones(paths, costs)
            self.convergence_history.append(self.best_cost)

            if verbose and iteration % 10 == 0:
                print(f"  [ACO] Iter {iteration:3d} | Best cost: {self.best_cost:.2f}")

        return self.best_path, self.best_cost

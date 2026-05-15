"""
abc_algo.py

Artificial Bee Colony — the "bee" part of our hybrid.

Honey bees are surprisingly smart at finding good food sources.
Here's how they do it (and how we copy it):

  - Employed Bees: Each one is assigned a "food source" (a candidate path).
    They explore nearby solutions and keep the better one.

  - Onlooker Bees: They hang back, watch the employed bees do their thing,
    and then go help the ones with the best food (fitness-proportional selection).

  - Scout Bees: If an employed bee is stuck (no improvement for too long),
    it gives up and becomes a scout — randomly exploring brand new areas.

This is what keeps ABC from getting stuck. When things stagnate, scouts inject
fresh random solutions. It's like restarting your router — sometimes that's
exactly what you need.
"""

import numpy as np
from src.fitness import evaluate


class ArtificialBeeColony:
    def __init__(self, env, config):
        self.env = env
        self.n_bees = config.get("num_bees", 20)
        self.max_iter = config.get("max_iterations", 100)
        self.limit = config.get("limit", 10)   # how many fails before going scout
        self.phi1 = config.get("phi1", 0.5)    # pull toward random neighbor
        self.phi2 = config.get("phi2", 0.3)    # pull toward global best
        self.n_waypoints = config.get("n_waypoints", 20)

        self.best_path = None
        self.best_cost = float('inf')
        self.convergence_history = []

        # initialize food sources (each bee starts with a random path)
        self.food_sources = []
        self.food_costs = []
        self.trial_counters = []  # how many times has this source failed to improve?

        self._initialize_food_sources()

    def _random_path(self):
        """
        Random candidate path from start to goal with random waypoints in between.
        This is what a food source (solution) looks like in path-planning terms.
        """
        path = [self.env.start]
        for _ in range(self.n_waypoints):
            path.append(self.env.random_free_cell())
        path.append(self.env.goal)
        return path

    def _initialize_food_sources(self):
        """
        Every bee gets a random starting food source.
        We score them and note the best one right away.
        """
        for _ in range(self.n_bees):
            path = self._random_path()
            cost = evaluate(path, self.env)
            self.food_sources.append(path)
            self.food_costs.append(cost)
            self.trial_counters.append(0)

            if cost < self.best_cost:
                self.best_cost = cost
                self.best_path = path

    def _perturb_path(self, path, other_path, best_path):
        """
        Generate a new candidate solution near an existing one.
        The bee doesn't jump to a completely random place —
        it nudges its current path based on:
          - another random bee's path (exploration)
          - the global best path (exploitation)

        This is the core ABC update equation from the paper:
            v_i = x_i + phi1*(x_i - x_k) + phi2*(x_i - x_best)
        """
        new_path = [self.env.start]

        for i in range(1, len(path) - 1):
            xi = np.array(path[i], dtype=float)
            xk = np.array(other_path[i] if i < len(other_path) else path[i], dtype=float)
            xb = np.array(best_path[i] if i < len(best_path) else path[i], dtype=float)

            # nudge the position — small random perturbation in two directions
            phi1 = np.random.uniform(-self.phi1, self.phi1)
            phi2 = np.random.uniform(-self.phi2, self.phi2)

            new_pos = xi + phi1 * (xi - xk) + phi2 * (xi - xb)

            # snap to grid and clamp within bounds
            nx = int(np.clip(round(new_pos[0]), 0, self.env.size - 1))
            ny = int(np.clip(round(new_pos[1]), 0, self.env.size - 1))

            # if we landed on a wall, find a nearby free cell instead
            if not self.env.is_free(nx, ny):
                nx, ny = self.env.random_free_cell()

            new_path.append((nx, ny))

        new_path.append(self.env.goal)
        return new_path

    def _employed_bee_phase(self):
        """
        Every employed bee tries to improve its food source.
        If the new one is better → swap. If not → increment failure counter.
        """
        for i in range(self.n_bees):
            # pick a random other bee's path to compare against
            k = np.random.choice([j for j in range(self.n_bees) if j != i])

            new_path = self._perturb_path(
                self.food_sources[i],
                self.food_sources[k],
                self.best_path
            )
            new_cost = evaluate(new_path, self.env)

            if new_cost < self.food_costs[i]:
                # found something better! take it
                self.food_sources[i] = new_path
                self.food_costs[i] = new_cost
                self.trial_counters[i] = 0

                if new_cost < self.best_cost:
                    self.best_cost = new_cost
                    self.best_path = new_path
            else:
                # nope, worse. note the failure
                self.trial_counters[i] += 1

    def _onlooker_bee_phase(self):
        """
        Onlooker bees pick a food source to exploit based on its quality.
        Better sources get more bees assigned to them (roulette selection).
        Then each onlooker bee does the same thing as employed bees — try to improve it.
        """
        # fitness for selection: lower cost = higher fitness for selection
        # invert cost so that smaller cost → bigger selection probability
        inv_costs = [1.0 / (c + 1e-9) for c in self.food_costs]
        total = sum(inv_costs)
        probs = [ic / total for ic in inv_costs]

        for _ in range(self.n_bees):
            # pick a source probabilistically
            i = np.random.choice(self.n_bees, p=probs)
            k = np.random.choice([j for j in range(self.n_bees) if j != i])

            new_path = self._perturb_path(
                self.food_sources[i],
                self.food_sources[k],
                self.best_path
            )
            new_cost = evaluate(new_path, self.env)

            if new_cost < self.food_costs[i]:
                self.food_sources[i] = new_path
                self.food_costs[i] = new_cost
                self.trial_counters[i] = 0

                if new_cost < self.best_cost:
                    self.best_cost = new_cost
                    self.best_path = new_path
            else:
                self.trial_counters[i] += 1

    def _scout_bee_phase(self):
        """
        If a source has failed to improve too many times, give up on it.
        The bee becomes a scout and randomly generates a fresh path near the best known.
        
        This is what prevents ABC from getting permanently stuck in local optima.
        """
        for i in range(self.n_bees):
            if self.trial_counters[i] >= self.limit:
                # this source is stale — abandon and explore fresh territory
                # (scout near the best, with a small random nudge)
                new_path = self._random_path()
                new_cost = evaluate(new_path, self.env)

                self.food_sources[i] = new_path
                self.food_costs[i] = new_cost
                self.trial_counters[i] = 0  # reset the failure counter

                if new_cost < self.best_cost:
                    self.best_cost = new_cost
                    self.best_path = new_path

    def run(self, verbose=True):
        """
        Main loop. Each iteration runs all three bee phases in order:
          Employed → Onlooker → Scout
        """
        for iteration in range(self.max_iter):
            self._employed_bee_phase()
            self._onlooker_bee_phase()
            self._scout_bee_phase()

            self.convergence_history.append(self.best_cost)

            if verbose and iteration % 10 == 0:
                print(f"  [ABC] Iter {iteration:3d} | Best cost: {self.best_cost:.2f}")

        return self.best_path, self.best_cost

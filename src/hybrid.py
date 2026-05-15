"""
hybrid.py

The Hybrid ACO-ABC Algorithm — this is the whole point of the project.

Here's the idea in plain English:
  - ACO is really good at homing in on promising areas fast (exploitation)
  - ABC is really good at not getting stuck and exploring widely (exploration)
  - Neither one is great at both
  - So... why not use both at the same time?

How the hybrid works:
  1. ACO runs: ants build paths and reinforce good ones with pheromone
  2. ABC runs: bees explore and refine, scouts inject fresh solutions
  3. They SHARE information — ABC's best solutions influence ACO's pheromone map
     and ACO's best paths seed ABC's food sources
  4. Repeat until you hit the iteration limit or it converges

The result: you get fast convergence (thanks ACO) AND diversity (thanks ABC).
This is why the paper shows ~39% improvement over vanilla ACO.
"""

import numpy as np
from src.aco import AntColonyOptimizer
from src.abc_algo import ArtificialBeeColony
from src.fitness import evaluate


class HybridACOABC:
    def __init__(self, env, config):
        self.env = env
        self.config = config
        self.max_iter = config.get("max_iterations", 100)

        # create both algorithms — they share the same environment and config
        self.aco = AntColonyOptimizer(env, config)
        self.abc = ArtificialBeeColony(env, config)

        self.best_path = None
        self.best_cost = float('inf')
        self.convergence_history = []

    def _sync_best_solutions(self):
        """
        Cross-pollinate the two algorithms!
        
        After each iteration:
        - If ACO found something better → give that path to ABC as a top food source
        - If ABC found something better → deposit extra pheromone in ACO on that path
        
        This is the "secret sauce" — the communication between the two.
        Without this you'd just be running them sequentially, which is less interesting.
        """
        # figure out who's winning right now
        aco_best_cost = self.aco.best_cost
        abc_best_cost = self.abc.best_cost

        if aco_best_cost < abc_best_cost:
            # ACO is ahead — push its best path into ABC's food sources
            # replace the worst food source ABC has
            worst_idx = np.argmax(self.abc.food_costs)
            self.abc.food_sources[worst_idx] = self.aco.best_path
            self.abc.food_costs[worst_idx] = aco_best_cost
            self.abc.trial_counters[worst_idx] = 0

        elif abc_best_cost < aco_best_cost:
            # ABC found something ACO doesn't know about yet
            # add pheromone to that path in ACO's memory
            path = self.abc.best_path
            deposit = self.aco.Q / (abc_best_cost + 1e-9)
            for i in range(len(path) - 1):
                key = (path[i], path[i+1])
                self.aco.pheromone[key] = self.aco.pheromone.get(key, 1.0) + deposit

    def run(self, verbose=True):
        """
        Main hybrid loop.
        
        Each iteration:
          1. Let all ACO ants build paths and update pheromone
          2. Let all ABC bees do their employed/onlooker/scout thing
          3. Sync the best solution between them (cross-pollination)
          4. Record the overall best
        """
        print("\n🐜🐝 Running Hybrid ACO-ABC...\n")

        for iteration in range(self.max_iter):

            # --- ACO PHASE ---
            # build paths with ants, update pheromone trails
            aco_paths = []
            aco_costs = []
            for _ in range(self.aco.n_ants):
                path = self.aco._build_path_for_ant()
                cost = evaluate(path, self.env)
                aco_paths.append(path)
                aco_costs.append(cost)

                if cost < self.aco.best_cost:
                    self.aco.best_cost = cost
                    self.aco.best_path = path

            self.aco._update_pheromones(aco_paths, aco_costs)

            # --- ABC PHASE ---
            # bees explore, exploit, and scout
            self.abc._employed_bee_phase()
            self.abc._onlooker_bee_phase()
            self.abc._scout_bee_phase()

            # --- CROSS-POLLINATION ---
            # share what each algorithm knows about good solutions
            self._sync_best_solutions()

            # --- TRACK THE OVERALL WINNER ---
            current_best = min(self.aco.best_cost, self.abc.best_cost)
            if current_best < self.best_cost:
                self.best_cost = current_best
                if self.aco.best_cost <= self.abc.best_cost:
                    self.best_path = self.aco.best_path
                else:
                    self.best_path = self.abc.best_path

            self.convergence_history.append(self.best_cost)

            if verbose and iteration % 10 == 0:
                print(f"  [HYBRID] Iter {iteration:3d} | Best cost: {self.best_cost:.2f} "
                      f"(ACO: {self.aco.best_cost:.2f}, ABC: {self.abc.best_cost:.2f})")

        print(f"\n✅ Done! Final best cost: {self.best_cost:.2f}")
        return self.best_path, self.best_cost

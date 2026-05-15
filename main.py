"""
main.py

The entry point — run this to see everything in action.

It'll:
  1. Build a 50x50 obstacle grid
  2. Run ACO alone, ABC alone, and the Hybrid
  3. Print a comparison table
  4. Show path plots and convergence curves
  5. Save outputs to the /results folder

Just do:  python main.py
"""

import os
from src.environment import GridEnvironment
from src.aco import AntColonyOptimizer
from src.abc_algo import ArtificialBeeColony
from src.hybrid import HybridACOABC
from src.visualizer import plot_comparison, plot_convergence, print_summary_table


# ─────────────────────────────────────────────
# Tweak these however you like!
# ─────────────────────────────────────────────
CONFIG = {
    "grid_size":        50,
    "num_ants":         20,
    "num_bees":         20,
    "max_iterations":   80,    # bump this up if you want better results (slower though)
    "evaporation_rate": 0.5,   # how fast pheromone fades
    "alpha":            1.0,   # pheromone influence
    "beta":             2.0,   # heuristic (distance) influence
    "Q":                100,   # pheromone deposit strength
    "limit":            10,    # ABC scout threshold
    "phi1":             0.5,   # ABC neighbor pull
    "phi2":             0.3,   # ABC global-best pull
    "n_waypoints":      18,    # intermediate path waypoints
}


def main():
    print("=" * 55)
    print("   🤖  Hybrid ACO-ABC Robot Path Planner")
    print("=" * 55)

    # build the world
    env = GridEnvironment(size=CONFIG["grid_size"], obstacle_seed=42)
    print(f"\n📍 Start: {env.start}  →  🎯 Goal: {env.goal}")
    print(f"   Grid: {env.size}×{env.size}, Obstacles: 3 rectangular regions\n")

    os.makedirs("results", exist_ok=True)

    # ── Run ACO ──────────────────────────────────
    print("🐜 Running ACO...")
    aco = AntColonyOptimizer(env, CONFIG)
    aco_path, aco_cost = aco.run(verbose=True)
    print(f"   ✓ ACO finished. Best cost: {aco_cost:.2f}\n")

    # ── Run ABC ──────────────────────────────────
    print("🐝 Running ABC...")
    abc = ArtificialBeeColony(env, CONFIG)
    abc_path, abc_cost = abc.run(verbose=True)
    print(f"   ✓ ABC finished. Best cost: {abc_cost:.2f}\n")

    # ── Run Hybrid ───────────────────────────────
    hybrid = HybridACOABC(env, CONFIG)
    hybrid_path, hybrid_cost = hybrid.run(verbose=True)

    # ── Collect results ──────────────────────────
    results = {
        "ACO":    (aco_path,    aco_cost,    aco.convergence_history),
        "ABC":    (abc_path,    abc_cost,    abc.convergence_history),
        "Hybrid": (hybrid_path, hybrid_cost, hybrid.convergence_history),
    }

    # ── Print text summary ───────────────────────
    print_summary_table(results)

    # ── Visualize ────────────────────────────────
    print("📊 Generating plots...")
    plot_comparison(results, env, save_path="results/path_comparison.png")
    plot_convergence(results,     save_path="results/convergence_curves.png")

    print("\n🎉 All done! Check the /results folder for saved plots.")
    print("   → results/path_comparison.png")
    print("   → results/convergence_curves.png\n")


if __name__ == "__main__":
    main()

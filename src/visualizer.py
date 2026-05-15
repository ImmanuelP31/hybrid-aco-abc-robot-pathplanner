"""
visualizer.py

Draws everything so you can actually see what's going on.

Because looking at a list of numbers is boring.
Looking at a robot navigating around obstacles is way more satisfying.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from scipy.interpolate import splprep, splev


def smooth_path(path, num_points=300):
    """
    Take a jagged list of waypoints and turn it into a smooth curve.
    Uses cubic spline interpolation — basically "connect the dots, but nicely".
    
    Real robots move smoothly; they can't just teleport between grid cells.
    """
    if len(path) < 4:
        return path  # not enough points to smooth — just return as-is

    xs = [p[0] for p in path]
    ys = [p[1] for p in path]

    try:
        # fit a spline through all the waypoints
        tck, u = splprep([xs, ys], s=0, k=min(3, len(path)-1))
        u_fine = np.linspace(0, 1, num_points)
        xs_smooth, ys_smooth = splev(u_fine, tck)
        return list(zip(xs_smooth, ys_smooth))
    except Exception:
        # if spline fails (sometimes happens with weird paths), just use original
        return path


def draw_environment(ax, env):
    """Draw the grid: obstacles, start, goal."""
    for i in range(env.size):
        for j in range(env.size):
            if env.grid[i][j] == 1:
                rect = patches.Rectangle(
                    (i - 0.5, j - 0.5), 1, 1,
                    linewidth=0, facecolor='#c8c8c8', alpha=0.9
                )
                ax.add_patch(rect)

    sx, sy = env.start
    gx, gy = env.goal
    ax.plot(sx, sy, 'go', markersize=12, label='Start', zorder=10)
    ax.plot(gx, gy, 'r*', markersize=16, label='Goal', zorder=10)

    ax.set_xlim(0, env.size)
    ax.set_ylim(0, env.size)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.15)


def plot_path(path, env, title="Path", color='blue', smooth=True, ax=None, show=True):
    """
    Plot a single path on the grid.
    Pass smooth=True to apply spline smoothing before drawing.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(8, 8))

    draw_environment(ax, env)

    if path:
        draw_path = smooth_path(path) if smooth else path
        xs = [p[0] for p in draw_path]
        ys = [p[1] for p in draw_path]
        ax.plot(xs, ys, color=color, linewidth=2.5, label=title, zorder=5)

        # mark waypoints (only original ones, not smoothed)
        orig_xs = [p[0] for p in path]
        orig_ys = [p[1] for p in path]
        ax.scatter(orig_xs[1:-1], orig_ys[1:-1],
                   color=color, s=20, alpha=0.5, zorder=6)

    ax.set_title(title, fontsize=14)
    ax.legend()

    if show:
        plt.tight_layout()
        plt.show()

    return ax


def plot_comparison(results, env, save_path=None):
    """
    Side-by-side comparison of ACO, ABC, and Hybrid paths.
    
    results should be a dict like:
      {
        "ACO":    (path, cost, convergence_history),
        "ABC":    (path, cost, convergence_history),
        "Hybrid": (path, cost, convergence_history),
      }
    """
    colors = {
        "ACO":    "#1f77b4",  # blue
        "ABC":    "#2ca02c",  # green
        "Hybrid": "#e03090",  # hot pink (it's the winner, give it a fun color)
    }

    fig, axes = plt.subplots(1, 3, figsize=(20, 7))
    fig.suptitle("Algorithm Comparison — Robot Path Planning", fontsize=16, fontweight='bold')

    for ax, (name, (path, cost, _)) in zip(axes, results.items()):
        draw_environment(ax, env)

        if path:
            smooth = smooth_path(path)
            xs = [p[0] for p in smooth]
            ys = [p[1] for p in smooth]
            ax.plot(xs, ys, color=colors[name], linewidth=2.5, zorder=5)

        ax.set_title(f"{name}\nCost: {cost:.2f}", fontsize=13)
        ax.legend()

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  Saved path comparison to: {save_path}")

    plt.show()


def plot_convergence(results, save_path=None):
    """
    Convergence curves — shows how fast each algorithm improves over iterations.
    
    A steeper drop early on = faster convergence (good).
    Flatter curve later = converged (also good).
    """
    colors = {
        "ACO":    "#1f77b4",
        "ABC":    "#2ca02c",
        "Hybrid": "#e03090",
    }

    fig, ax = plt.subplots(figsize=(10, 6))

    for name, (_, _, history) in results.items():
        ax.plot(history, color=colors[name], linewidth=2.5, label=name)

    ax.set_xlabel("Iteration", fontsize=12)
    ax.set_ylabel("Best Cost (lower = better)", fontsize=12)
    ax.set_title("Convergence Comparison", fontsize=14, fontweight='bold')
    ax.legend(fontsize=12)
    ax.grid(True, alpha=0.3)

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"  Saved convergence chart to: {save_path}")

    plt.show()


def print_summary_table(results):
    """
    Quick text table printed to console — like Table 5 in the paper.
    """
    print("\n" + "="*65)
    print(f"{'Algorithm':<12} {'Best Cost':>12} {'Convergence History':>20}")
    print("="*65)

    for name, (path, cost, history) in results.items():
        n_iter = len(history)
        # find roughly when it converged (when improvement < 1%)
        converged_at = n_iter
        for i in range(1, n_iter):
            if history[i] > 0 and abs(history[i] - history[i-1]) / (history[i] + 1e-9) < 0.001:
                converged_at = i
                break

        print(f"  {name:<10} {cost:>12.2f}   converged ~iter {converged_at}")

    print("="*65 + "\n")

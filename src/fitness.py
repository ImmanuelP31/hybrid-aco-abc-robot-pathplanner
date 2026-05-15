"""
fitness.py

How do we know if one path is better than another?
This file scores every candidate path. Lower score = better path.

We care about three things:
  1. Total length — shorter is usually better
  2. Obstacle clearance — did we actually avoid the walls?
  3. Smoothness — no crazy zigzags (real robots hate those)
"""

import numpy as np


def path_length(path):
    """
    Add up the Euclidean distance between each step in the path.
    Simple — just how far did we actually travel?
    """
    if len(path) < 2:
        return 0.0

    total = 0.0
    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]
        total += np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

    return total


def smoothness_penalty(path):
    """
    Penalize sharp turns. A robot jerking left and right constantly
    is bad for both the robot and whatever it's carrying.

    We measure the angle at each waypoint — big angle change = penalty.
    """
    if len(path) < 3:
        return 0.0  # can't measure a turn with less than 3 points

    penalty = 0.0
    for i in range(1, len(path) - 1):
        # vectors: backward and forward from current point
        v1 = (path[i][0] - path[i-1][0], path[i][1] - path[i-1][1])
        v2 = (path[i+1][0] - path[i][0], path[i+1][1] - path[i][1])

        # dot product tells us the angle between them
        dot = v1[0]*v2[0] + v1[1]*v2[1]
        mag1 = np.sqrt(v1[0]**2 + v1[1]**2) + 1e-9  # tiny epsilon to avoid /0
        mag2 = np.sqrt(v2[0]**2 + v2[1]**2) + 1e-9

        cos_angle = np.clip(dot / (mag1 * mag2), -1.0, 1.0)
        angle = np.arccos(cos_angle)  # radians

        # bigger angle change = bigger penalty
        penalty += angle

    return penalty


def obstacle_penalty(path, env, penalty_per_hit=1000):
    """
    If the path goes through an obstacle, that's very bad.
    We slap a huge penalty on it so the algorithm learns to avoid it.
    
    (1000 per obstacle hit — basically disqualifies the path)
    """
    hits = sum(1 for (x, y) in path if not env.is_free(int(x), int(y)))
    return hits * penalty_per_hit


def evaluate(path, env, w_length=1.0, w_smooth=0.3, w_obstacle=1.0):
    """
    The combined fitness score for a path.
    
    Lower = better. If you hit an obstacle, you're already losing badly.
    
    You can tweak the weights:
      - w_length: how much we care about total distance
      - w_smooth: how much we care about smooth turns
      - w_obstacle: how much we hate hitting walls (keep this high!)
    """
    length  = path_length(path) * w_length
    smooth  = smoothness_penalty(path) * w_smooth
    walls   = obstacle_penalty(path, env) * w_obstacle

    total = length + smooth + walls
    return total

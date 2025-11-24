import numpy as np
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment
import random

def compute_cost_matrix(src_features: np.ndarray, src_pos: np.ndarray, 
                        tgt_features: np.ndarray, tgt_pos: np.ndarray, 
                        proximity_importance: float) -> np.ndarray:
    """
    Computes the cost matrix between source and target cells.
    src_features: (N, 3) colors
    src_pos: (N, 2) positions
    tgt_features: (N, 3) colors
    tgt_pos: (N, 2) positions
    proximity_importance: float [0, 1]
    
    Returns: (N, N) cost matrix
    """
    # Color cost: squared Euclidean distance in RGB space
    # cdist returns Euclidean distance, so we square it
    color_dist = cdist(src_features, tgt_features, metric='sqeuclidean')
    
    # Spatial cost: squared Euclidean distance in position space
    spatial_dist = cdist(src_pos, tgt_pos, metric='sqeuclidean')
    
    # Normalize costs to be roughly comparable?
    # Colors are in [0, 1], so max sq dist is 3.
    # Positions are in [0, 1], so max sq dist is 2.
    # They are already roughly in the same range.
    
    cost = (1.0 - proximity_importance) * color_dist + proximity_importance * spatial_dist
    return cost

def solve_assignment(src_features: np.ndarray, src_pos: np.ndarray, 
                     tgt_features: np.ndarray, tgt_pos: np.ndarray, 
                     algorithm: str = "optimal",
                     proximity_importance: float = 0.3) -> np.ndarray:
    """
    Solves the assignment problem.
    Returns: (N,) array where index i is the target cell index for source cell i.
    """
    N = src_features.shape[0]
    
    if algorithm == "sort":
        # Sort by luminance + position
        # Luminance = 0.299*R + 0.587*G + 0.114*B
        lum_src = 0.299 * src_features[:, 0] + 0.587 * src_features[:, 1] + 0.114 * src_features[:, 2]
        lum_tgt = 0.299 * tgt_features[:, 0] + 0.587 * tgt_features[:, 1] + 0.114 * tgt_features[:, 2]
        
        # We want to sort primarily by luminance, then by Y, then by X to keep spatial coherence
        # src_pos is (y, x)
        # Construct sort keys
        # We can use lexsort. lexsort sorts by last key first.
        # So keys should be (src_pos[:, 1], src_pos[:, 0], lum_src) for (lum, y, x) order?
        # Actually, let's just normalize and combine or use structured array.
        # Simple way:
        
        # Sort indices
        # We want to match the darkest source to the darkest target, etc.
        # But among similar luminance, we want to match top-left to top-left to minimize movement.
        
        # Let's try sorting by (Luminance, Y, X)
        # But Luminance is float. We might want to bin it or just use it as primary.
        # If we just sort by Luminance, spatial coherence is lost for similar colors.
        # But 'sort' algorithm implies we just match rank-by-rank.
        
        src_keys = np.lexsort((src_pos[:, 1], src_pos[:, 0], lum_src)) # Sorts by lum, then y, then x
        tgt_keys = np.lexsort((tgt_pos[:, 1], tgt_pos[:, 0], lum_tgt))
        
        # Now we have:
        # src_keys[0] is the index of the cell with smallest lum (and top-left-most)
        # tgt_keys[0] is the index of the target cell with smallest lum
        
        # We want assignment[src_keys[k]] = tgt_keys[k]
        assignment = np.zeros(N, dtype=int)
        assignment[src_keys] = tgt_keys
        
        return assignment

    # For other algorithms, we need the cost matrix
    # WARNING: O(N^2) memory!
    if N > 10000 and algorithm == "optimal":
        print(f"WARNING: 'optimal' algorithm with {N} cells will be extremely slow and memory heavy.")
    
    cost_matrix = compute_cost_matrix(src_features, src_pos, tgt_features, tgt_pos, proximity_importance)
    
    rows = cost_matrix.shape[0]
    cols = cost_matrix.shape[1]
    
    if algorithm == "optimal":
        row_ind, col_ind = linear_sum_assignment(cost_matrix)
        assignment = np.zeros(rows, dtype=int)
        assignment[row_ind] = col_ind
        return assignment
        
    elif algorithm == "greedy":
        assignment = np.full(rows, -1, dtype=int)
        taken_targets = set()
        source_indices = list(range(rows))
        random.shuffle(source_indices)
        
        for i in source_indices:
            costs = cost_matrix[i]
            sorted_targets = np.argsort(costs)
            for t in sorted_targets:
                if t not in taken_targets:
                    assignment[i] = t
                    taken_targets.add(t)
                    break
        return assignment
        
    elif algorithm == "approx":
        assignment = np.full(rows, -1, dtype=int)
        taken_targets = set()
        for i in range(rows):
            costs = cost_matrix[i]
            sorted_targets = np.argsort(costs)
            for t in sorted_targets:
                if t not in taken_targets:
                    assignment[i] = t
                    taken_targets.add(t)
                    break
        return assignment
    
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

import unittest
import numpy as np
from py_surrafication.assignment import solve_assignment
from py_surrafication.core import get_cells, extract_features

class TestSanity(unittest.TestCase):
    def test_solve_assignment_optimal(self):
        N = 10
        src_features = np.random.rand(N, 3)
        src_pos = np.random.rand(N, 2)
        tgt_features = np.random.rand(N, 3)
        tgt_pos = np.random.rand(N, 2)
        
        assignment = solve_assignment(src_features, src_pos, tgt_features, tgt_pos, algorithm="optimal")
        
        # Check if assignment is a permutation
        self.assertEqual(len(assignment), N)
        self.assertEqual(len(set(assignment)), N)
        self.assertTrue(np.all(assignment >= 0))
        self.assertTrue(np.all(assignment < N))

    def test_solve_assignment_sort(self):
        N = 100
        src_features = np.random.rand(N, 3)
        src_pos = np.random.rand(N, 2)
        tgt_features = np.random.rand(N, 3)
        tgt_pos = np.random.rand(N, 2)
        
        assignment = solve_assignment(src_features, src_pos, tgt_features, tgt_pos, algorithm="sort")
        
        self.assertEqual(len(assignment), N)
        self.assertEqual(len(set(assignment)), N)
        
    def test_solve_assignment_greedy(self):
        N = 20
        src_features = np.random.rand(N, 3)
        src_pos = np.random.rand(N, 2)
        tgt_features = np.random.rand(N, 3)
        tgt_pos = np.random.rand(N, 2)
        
        assignment = solve_assignment(src_features, src_pos, tgt_features, tgt_pos, algorithm="greedy")
        
        self.assertEqual(len(assignment), N)
        self.assertEqual(len(set(assignment)), N)

if __name__ == '__main__':
    unittest.main()

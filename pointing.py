import numpy as np
from scipy.linalg import solve_continuous_are


class PointingController:
    def __init__(self, Ix=100, Iy= 150, Iz=200, torque_max=0.5):
        # Tighter torque limit - fine pointing mode
        self.torque_max = torque_max
        A = np.zeros((6, 6))
        A[0, 3] = 1.0
        A[1, 4] = 1.0
        A[2, 5] = 1.0


        B = np.zeros((6, 3))
        B[3, 0] = 1.0/Ix
        B[4, 1] = 1.0/Iy
        B[5, 2] = 1.0/Iz


        # High Q for tight pointing accuracy
        Q = np.diag([200.0, 200.0, 200.0, 10.0, 10.0, 10.0])
        R = np.diag([1.0, 1.0, 1.0])


        p = solve_continuous_are(A, B, Q, R)
        self.k = np.linalg.inv(R) @ B.T @ p

    def compute(self, state, target=None):
        if target is None: 
            target = np.zeros(6)
        torque = self.K @ (target - state)
        return np.clip(torque, -self.torque_max, self.torque_max)
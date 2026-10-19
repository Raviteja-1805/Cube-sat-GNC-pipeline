import numpy as np

class BDotDetumbling:
    def __init__(self, k=1e4, m_max=0.02):
        # k = B-dot gain, m_max= max magnetic moment (A.m^2)
        self.k  = k
        self.m_max = m_max
        self.B_prev = None

    def compute(self, B, dt):
        # B = current magnetic field vector 
        if self.B_prev is None:
            self.B_prev = B
            return np.zeros(3)
        # Rate of change of magnetic field
        Bdot = (B - self.B_prev) / dt
        self.B_prev = B.copy()
        # B-dot law : m = -k * Bdot (oppose the change)
        m = -self.k * Bdot
        return np.clip(m, -self.m_max, self.m_max)

    def torque_from_moment(self, m, B):
        # Torque = m * B (cross product)
        return np.cross(m, B)

    def is_detumbled(self, rates, threshold=np.deg2rad(1)):
        # check if angular rate is below 1 deg/s
        return np.all(np.abs(rates) < threshold)
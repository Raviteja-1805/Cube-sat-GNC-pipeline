import numpy as np

class Orbit:
    def __init__(self, altitude_km=500, dt=1.0):
        self.mu = 3.986e14  #earth garvitational param
        self.Re = 6.371e6   #Earth radius (m)
        self.R = self.Re + altitude_km * 1000
        self.dt = dt
        # Orbital period and Rate
        self.T = 2 * np.pi * np.sqrt(self.R**3 / self.mu)
        self.n = 2 * np.pi / self.T #mean motion
        self.t = 0.0
        print(f"Orbit: altitude={altitude_km}km, period={self.T/60:.1f}min" )

    def step(self):
        self.t += self.dt
        # position in orbital plane (circular orbit)
        theta = self.n * self.t
        x = self.R * np.cos(theta)
        y = self.R * np.sin(theta)
        z = 0.0
        return np.array([x, y, z])

    def magnetic_field(self, pos):
        # simplified dipole magnetic field model
        r = np.linalg.norm(pos)
        m = 7.94e22 #earth magnetic dipole model
        B = (m / r**3) * np.array([0, 0, 1.0]) * 1e-9
        return B
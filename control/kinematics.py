import numpy as np

class TrajectoryGenerator:
    def __init__(self):
        self.V_MAX = 0.1 * np.sqrt(2) # m/s
        self.A_MAX = self.V_MAX * 10 # m/s^2 (10 times V_MAX for fast acceleration)
        self.J_MAX = 1
        self._trajectory = []

    def setHome(self, home):
        self.home = home

    # S-Curve trajectory generation
    def generate_s_curve_trajectory(self, start, end, duration, dt): 
        # Generate an S-Curve trajectory from start to end with the given duration and time step
        pass
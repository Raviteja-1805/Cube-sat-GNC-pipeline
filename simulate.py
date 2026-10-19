import numpy as np
import matplotlib.pyplot as plt
from orbit import Orbit
from detumbling import BDotDetumbling
from pointing import PointingController
from spacecraft import Spacecraft

orb = Orbit(altitude_km=500, dt=1.0)
sc = Spacecraft(dt=1.0)
bdot = BDotDetumbling()
lqr = PointingController()

# initial state: tumbling (largr rates)
state = np.array([np.deg2rad(30), np.deg2rad(20),
                  np.deg2rad(10),0.3, -0.2, 0.15])
mode = 'detumbling'
hist_angles, hist_rates, hist_mode = [], [], []
n_steps = 1200 #20 minutes

for i in range (n_steps):
    pos = orb.step()
    B = orb.magnetic_field(pos)

    if mode == 'detumbling' :
        m = bdot.compute(B, dt=1.0)
        torque = bdot.torque_from_moment(m, B)
        if bdot.is_detumbled(state[3 :]):
            mode = 'pointing'
            print(f"Detumbled at t={i}s - switching to fine pointing" )
    else:
        torque = lqr.compute(state)

    state = sc.step(state, torque)
    hist_angles.append(np.rad2deg(state[3 :]))
    hist_rates.append(np.rad2deg(state[3 :]))
    hist_mode.append(0 if mode == 'detumbling' else 1)

hist_angles = np.array(hist_angles)
hist_rates = np.array(hist_rates)
t = np.arange(n_steps)

fig, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
for i, lbl in enumerate([ 'Roll', 'Pitch', 'Yaw' ]):
    axes[0].plot(t, hist_angles[:, i], label=lbl)
axes[0].set_ylabel('Angle (deg)' ); axes[0].legend(); axes[0].grid(True)
axes[0].set_title( 'gnc_pipeline_attitude_orbit_control: detumbling - fine pointing ' )
for i, lbl in enumerate ([ 'p', 'q', 'r']):
    axes[1].plot(t, hist_rates[:, i], label=lbl)
axes[1].set_ylabel( 'Rate (deg/s)' ); axes[1].legend(); axes[1].grid(True)
axes[2].plot(t, hist_mode, 'k-' , lw=2)
axes[2].set_yticks([0, 1]); axes[2].set_yticklabels([ 'Detumbling' , 'Pointing' ])
axes[2].set_xlabel( 'Time (s) '); axes[2].set_ylabel( 'Mode' ); axes[2].grid(True)
plt.tight_layout()
plt.savefig( 'gnc_pipeline_attitude_orbit_control_results.png', dpi=150)
plt.show()
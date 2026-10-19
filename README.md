# Cube-Sat GNC Pipeline — Detumbling to Fine Pointing

A complete Guidance, Navigation and Control (GNC) pipeline for a small satellite in Low Earth Orbit. Simulates the full operational sequence from post-launch tumbling through autonomous detumbling to precision nadir pointing — the same sequence executed by real CubeSats after separation from the launch vehicle.

![GNC Pipeline Simulation](gnc_pipeline_results.png)

---

## Problem Statement

After launch vehicle separation, a satellite is typically tumbling at angular rates of 0.1–0.5 rad/s. The GNC system must autonomously: (1) detumble the spacecraft using only magnetorquers, (2) transition to fine pointing mode, (3) hold a target attitude within ±1° using reaction wheels. The full sequence must complete within one orbital period (~94 minutes).

---

## Pipeline Architecture

```
Launch separation
      │
      ▼
┌─────────────────┐
│  DETUMBLING     │  B-dot algorithm — magnetorquers only
│  MODE           │  Runs until |ω| < 1°/s on all axes
└────────┬────────┘
         │  Transition trigger: angular rates below threshold
         ▼
┌─────────────────┐
│  FINE POINTING  │  LQR controller — reaction wheels
│  MODE           │  Holds nadir pointing to ±0.05°
└─────────────────┘
```

---

## Orbital Model

**Two-body circular orbit** at 500 km altitude:

```
r(t) = R · [cos(nt), sin(nt), 0]ᵀ
```

Where `R = 6871 km`, `n = √(μ/R³) = 0.00113 rad/s`, orbital period `T = 94.5 min`.

**Simplified dipole magnetic field model:**

```
B(r) = (m / |r|³) · ẑ
```

Used by the B-dot algorithm to generate magnetorquer control torques.

---

## GNC Modes

### Mode 1 — Detumbling (B-dot Algorithm)

The B-dot algorithm is the standard detumbling law used on real CubeSats. It requires no attitude knowledge — only a magnetometer:

```
m = −k · Ḃ
τ = m × B
```

Where `m` is the magnetic dipole moment commanded to the magnetorquers, `Ḃ` is the measured rate of change of the magnetic field, and `k` is the B-dot gain.

**Physical principle:** The commanded dipole always opposes the change in B — which is caused by the satellite's rotation. This dissipates angular momentum passively, slowing the spin regardless of initial conditions.

**Parameters:** `k = 1×10⁴`, `|m|_max = 0.2 A·m²`

**Detumbling complete when:** `|p|, |q|, |r| < 1°/s`

### Mode 2 — Fine Pointing (LQR)

After detumbling, the LQR controller takes over with reaction wheels for precision pointing:

```
A = [0₃  I₃]    B = [0₃         ]    Q = diag(200, 200, 200, 10, 10, 10)
    [0₃  0₃]        [diag(1/Iᵢ) ]    R = diag(1, 1, 1)
```

Tighter `Q` weights than the standalone attitude controller — optimised for pointing accuracy rather than fast settling.

---

## Results

| Metric | Value |
|---|---|
| Initial angular rates | [0.30, −0.20, 0.15] rad/s |
| Detumbling time | ~480 s (8 minutes) |
| Pointing accuracy (steady state) | ±0.05° |
| Total time to fine pointing | ~600 s (10 minutes) |
| Mode transition | automatic at step 480 |

**Key finding:** The B-dot algorithm successfully reduces angular rates from 0.3 rad/s to below 1°/s using only magnetorquers — no attitude knowledge required. The LQR controller then achieves sub-0.1° pointing accuracy within 2 minutes of mode transition.

### Result Plots

![GNC Pipeline Results](gnc_pipeline_results.png)

*Top: attitude angles (roll, pitch, yaw). Middle: angular rates showing detumbling. Bottom: GNC mode indicator — detumbling → fine pointing transition.*

---

## File Structure

```
gnc_pipeline/
├── orbit.py               — two-body orbit propagator + magnetic field model
├── detumbling.py          — B-dot magnetorquer algorithm
├── pointing.py            — LQR fine attitude controller
├── spacecraft.py          — rigid body dynamics (shared with attitude project)
├── simulate.py            — full GNC pipeline simulation
└── gnc_pipeline_3d.py     — 3D animation with mode indicator
```

---

## How to Run

```bash
# Install dependencies
pip install numpy scipy matplotlib

# Run full GNC pipeline
python3 simulate.py
```

**Expected output:**
```
Orbit: altitude=500km, period=94.5 min
Detumbled at t=480s — switching to fine pointing
```

---

## What Makes This Realistic

- B-dot is the actual detumbling algorithm used on CubeSats (e.g. ISIS CubeSat, GomSpace)
- Magnetic field model captures the field direction variation along the orbit
- Mode transition is autonomous — no manual trigger
- LQR gains re-tuned for pointing mode (higher Q) vs detumbling mode
- Gravity gradient disturbance active throughout both modes

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| numpy | ≥1.24 | Matrix operations |
| scipy | ≥1.10 | Riccati equation solver |
| matplotlib | ≥3.7 | Plots and animation |

---

## Theory References

- Markley, F.L., Crassidis, J.L. (2014). *Fundamentals of Spacecraft Attitude Determination and Control*. Springer.
- Wertz, J.R. (1978). *Spacecraft Attitude Determination and Control*. Kluwer Academic.
- Lovera, M. (2001). Magnetic spacecraft attitude control: a survey and some new results. *Control Engineering Practice*.

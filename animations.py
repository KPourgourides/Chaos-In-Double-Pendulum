"""
TU Delft Computational Physics - Project 3: Double Pendulum
Authors: Kyproula Mitsidi, Konstantinos Pourgourides
May-June 2026

~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

This module hosts all the functions that are necessary for animations.
"""

from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np
import matplotlib.pyplot as plt
import double_pendulum as dp

def animate_double_pendulum(phi_1, phi_2, dt, save_as = 'double_pendulum'):
    """
    Creates and saves an animation of a double pendulum system.

    Parameters
    ----------
    phi_1 : numpy.ndarray
        Angular displacement of the first pendulum over time in radians.
    phi_2 : numpy.ndarray
        Angular displacement of the second pendulum over time in radians.
    dt : float
        Time step between successive frames in seconds.
    save_as : str, optional
        Filename used to save the animation GIF.
        Default is 'double_pendulum'.

    Returns
    -------
    matplotlib.animation.FuncAnimation
        The animation object representing the simulated double pendulum motion.
    """

    # Convert to Cartesian coordinates
    x1 = dp.L_1 * np.sin(phi_1)
    y1 = -dp.L_1 * np.cos(phi_1)

    x2 = x1 + dp.L_2 * np.sin(phi_2)
    y2 = y1 - dp.L_2 * np.cos(phi_2)

    # Create figure
    fig, ax = plt.subplots(figsize=(5,5))

    max_length = dp.L_1 + dp.L_2

    ax.set_xlim(-max_length - 0.2, max_length + 0.2)
    ax.set_ylim(-max_length - 0.2, max_length + 0.2)

    ax.set_aspect('equal')
    ax.axis('off')

    # Pendulum
    line, = ax.plot([], [], 'o-', lw=2, color='black')

    # Trace of first mass
    trace1, = ax.plot([], [], '-', lw=1,
                      color='gray', alpha=0.5)

    # Trace of second mass
    trace2, = ax.plot([], [], '-', lw=1,
                      color='black', alpha=0.7)

    tail_length = 10000

    def init():

        line.set_data([], [])

        trace1.set_data([], [])
        trace2.set_data([], [])

        return line, trace1, trace2

    def update(frame):

        this_x = [0, x1[frame], x2[frame]]
        this_y = [0, y1[frame], y2[frame]]

        line.set_data(this_x, this_y)

        start = max(0, frame - tail_length)

        # first mass trace
        trace1.set_data(x1[start:frame], y1[start:frame])

        # second mass trace
        trace2.set_data(x2[start:frame], y2[start:frame])

        return line, trace1, trace2

    frames = range(0, len(phi_1), 2)

    ani = FuncAnimation(
        fig,
        update,
        frames=frames,
        init_func=init,
        interval=20,
        blit=True)

    ani.save(f"journal_plots/{save_as}.gif", writer=PillowWriter(fps=30))

    return ani

    
def animate_three_pendulums_with_phi2(phis1, phis2, dt, save_as="triple_pendulum"):
    """
    Animates three double pendulum trajectories while also plotting the
    evolution of the second angle (phi_2) over time.

    Parameters
    ----------
    phis1 : list of numpy.ndarray
        List of angular displacement arrays for the first pendulum angle (phi_1),
        one array per simulation run.
    phis2 : list of numpy.ndarray
        List of angular displacement arrays for the second pendulum angle (phi_2),
        one array per simulation run.
    dt : float
        Time step between successive frames in seconds.
    save_as : str, optional
        Filename used to save the resulting GIF animation.
        Default is "triple_pendulum".

    Returns
    -------
    matplotlib.animation.FuncAnimation
        The animation object representing the multi-trajectory visualization.
    """
    n_runs = len(phis1)
    n_frames = len(phis1[0])

    max_length = dp.L_1 + dp.L_2

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": [1.2, 2]})

    # -------------------------
    # LEFT: pendulums
    # -------------------------
    ax1.set_xlim(-max_length - 0.2, max_length + 0.2)
    ax1.set_ylim(-max_length - 0.2, max_length + 0.2)
    ax1.set_aspect("equal")
    ax1.axis("off")

    colors = ["black", "red", "blue"]

    lines = []
    traces = []

    for i in range(n_runs):
        line, = ax1.plot([], [], "o-", lw=2, color=colors[i])
        trace, = ax1.plot([], [], "-", lw=1, color=colors[i], alpha=0.4)
        lines.append(line)
        traces.append(trace)

    tail_length = 1000

    # -------------------------
    # RIGHT: phi2 vs time
    # -------------------------
    ax2.set_xlabel("Time (S)")
    ax2.set_ylabel(r"$\phi_2$ (rad)")

    t = np.arange(n_frames) * dt

    phi_lines = []
    for i in range(n_runs):
        l, = ax2.plot([], [], color=colors[i])
        phi_lines.append(l)

    ax2.set_xlim(0, t[-1])
    ax2.set_ylim(min(np.min(p) for p in phis2), max(np.max(p) for p in phis2))

    # -------------------------
    # INIT
    # -------------------------
    def init():
        for i in range(n_runs):
            lines[i].set_data([], [])
            traces[i].set_data([], [])
            phi_lines[i].set_data([], [])
        return lines + traces + phi_lines

    # -------------------------
    # UPDATE
    # -------------------------
    def update(frame):

        for i in range(n_runs):

            phi1 = phis1[i]
            phi2 = phis2[i]

            # cartesian
            x1 = dp.L_1 * np.sin(phi1)
            y1 = -dp.L_1 * np.cos(phi1)

            x2 = x1 + dp.L_2 * np.sin(phi2)
            y2 = y1 - dp.L_2 * np.cos(phi2)

            # pendulum line
            lines[i].set_data([0, x1[frame], x2[frame]], [0, y1[frame], y2[frame]])

            start = max(0, frame - tail_length)

            traces[i].set_data(x2[start:frame], y2[start:frame])

            # phi2 plot
            phi_lines[i].set_data(t[:frame], phi2[:frame])

        return lines + traces + phi_lines

    ani = FuncAnimation(
        fig,
        update,
        frames=range(0, n_frames, 2),
        init_func=init,
        interval=20,
        blit=True)

    ani.save(f"journal_plots/{save_as}.gif", writer=PillowWriter(fps=30))

    return ani
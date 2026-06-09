"""
TU Delft Computational Physics - Project 3: Double Pendulum
Authors: Kyproula Mitsidi, Konstantinos Pourgourides
May-June 2026

~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ 

This module hosts all the functions that are necessary for the simulation to run.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

def initialize_first_body(phi_1, omega_1, m_1=1, l_1=1):
    """
    Initializes and assigns the parameters of the first pendulum body.

    Parameters
    ----------
    phi_1 : float
        Initial angular displacement of the first body in radians.
    omega_1 : float
        Initial angular velocity of the first body in radians per second.
    m_1 : float, optional
        Mass of the first body. Default is 1.
    l_1 : float, optional
        Length of the first pendulum arm. Default is 1.

    Returns
    -------
    None
    """
    global M_1, L_1, PHI_1, W_1

    M_1 = m_1
    L_1 = l_1
    PHI_1 = phi_1
    W_1 = omega_1*np.sqrt(L_1 / 9.81)


def initialize_second_body(phi_2, omega_2, m_2=1, l_2=1):
    """
    Initializes and assigns the parameters of the second pendulum body.

    Parameters
    ----------
    phi_2 : float
        Initial angular displacement of the second body in radians.
    omega_2 : float
        Initial angular velocity of the second body in radians per second.
    m_2 : float, optional
        Mass of the second body. Default is 1.
    l_2 : float, optional
        Length of the second pendulum arm. Default is 1.

    Returns
    -------
    None
    """
    global M_2, L_2, PHI_2, W_2

    M_2 = m_2
    L_2 = l_2
    PHI_2 = phi_2
    W_2 = omega_2*np.sqrt(L_1 / 9.81)
    

def angular_acceleration(phi_1, phi_2, omega_1, omega_2):
    """
    Computes the dimensionless angular accelerations of both bodies.

    Parameters
    ----------
    phi_1 : float
        Angular displacement of the first body in radians.
    phi_2 : float
        Angular displacement of the second body in radians.
    omega_1 : float
        Dimensionless angular velocity of the first body.
    omega_2 : float
        Dimensionless angular velocity of the second body.

    Returns
    -------
        - alpha_1 : float
            Dimensionless angular acceleration of the first body.
        - alpha_2 : float
            Dimensionless angular acceleration of the second body.
    """
    mu = M_2 / M_1
    lam = L_2 / L_1

    delta = phi_1 - phi_2
    denominator = 2 + mu - mu*np.cos(2*delta)

    alpha_1 = (-(2 + mu)*np.sin(phi_1) - mu*np.sin(phi_1 - 2*phi_2) - 2*mu*np.sin(delta) * (lam*omega_2**2 + omega_1**2*np.cos(delta))) / denominator
    alpha_2 = (2*np.sin(delta)* ((1+mu)*omega_1**2 + (1+mu)*np.cos(phi_1) + mu*lam*omega_2**2*np.cos(delta))) / (lam*denominator)

    return alpha_1, alpha_2

    
def simulate(dt, t_steps):
    """
    Simulates the motion of a double pendulum using the fourth-order
    Runge-Kutta (RK4) integration method.

    Parameters
    ----------
    dt : float
        Time step of the simulation in seconds.
    t_steps : int
        Number of time steps to simulate.

    Returns
    -------
        - phi_1 : numpy.ndarray
            Angular displacement of the first body at each time step, in radians.
        - phi_2 : numpy.ndarray
            Angular displacement of the second body at each time step, in radians.
        - w_1 : numpy.ndarray
            Dimensionless angular velocity of the first body at each time step.
        - w_2 : numpy.ndarray
            Dimensionless angular velocity of the second body at each time step.
    """
    dtau = dt * np.sqrt(9.81 / L_1)
    
    # Memory allocation
    phi_1 = np.zeros(t_steps)
    phi_2 = np.zeros(t_steps)
    w_1 = np.zeros(t_steps)
    w_2 = np.zeros(t_steps)

    # Initial conditions
    phi_1[0] = PHI_1
    phi_2[0] = PHI_2
    w_1[0] = W_1
    w_2[0] = W_2

    # State derivative function
    def derivatives(state):
        """
        Computes the time derivatives of the double pendulum state vector.

        Parameters
        ----------
        state : numpy.ndarray or list of float
            State vector of the system in the form: [phi_1, phi_2, w_1, w_2], where:
            - phi_1, phi_2 are angular displacements (radians)
            - w_1, w_2 are angular velocities

        Returns
        -------
        numpy.ndarray
        Array containing the derivatives of the state vector in the form:
        [w_1, w_2, a_1, a_2], where:
        - w_1, w_2 are angular velocities
        - a_1, a_2 are angular accelerations
        """
        
        phi_1, phi_2, w_1, w_2 = state
        a_1, a_2 = angular_acceleration(phi_1, phi_2, w_1, w_2)
        return np.array([w_1, w_2, a_1, a_2])

    # RK4 loop
    for i in range(t_steps - 1):

        state = np.array([phi_1[i], phi_2[i], w_1[i], w_2[i]])
        k1 = derivatives(state)
        k2 = derivatives(state + 0.5 * dtau * k1)
        k3 = derivatives(state + 0.5 * dtau * k2)
        k4 = derivatives(state + dtau * k3)

        state_next = state + (dtau / 6.0) * (k1 + 2*k2 + 2*k3 + k4)

        phi_1[i+1] = state_next[0]
        phi_2[i+1] = state_next[1]
        w_1[i+1] = state_next[2]
        w_2[i+1] = state_next[3]

    return phi_1, phi_2, w_1, w_2
    

def get_potential_energy(phi_1, phi_2):
    """
    Computes the dimensionless gravitational potential energy of the
    double pendulum relative to its equilibrium configuration.

    Parameters
    ----------
    phi_1 : float or numpy.ndarray
        Angular displacement of the first body in radians.
    phi_2 : float or numpy.ndarray
        Angular displacement of the second body in radians.

    Returns
    -------
    - pe : float or numpy.ndarray
        Dimensionless potential energy of the system relative to the
        minimum-energy configuration. 
    """
    mu = M_2/M_1
    lam = L_2/L_1

    v = (-(1+mu)*np.cos(phi_1) - mu*lam*np.cos(phi_2))
    v_0 = -(1+mu) - mu*lam
    pe = v - v_0

    return pe

    
def get_kinetic_energy(phi_1, phi_2, omega_1, omega_2):
    """
    Computes the dimensionless kinetic energy of the double pendulum system.

    Parameters
    ----------
    phi_1 : float or numpy.ndarray
        Angular displacement of the first body in radians.
    phi_2 : float or numpy.ndarray
        Angular displacement of the second body in radians.
    omega_1 : float or numpy.ndarray
        Dimensionless angular velocity of the first body.
    omega_2 : float or numpy.ndarray
        Dimensionless angular velocity of the second body.

    Returns
    -------
    ke : float or numpy.ndarray
        Dimensionless kinetic energy of the system.
    """

    mu = M_2/M_1
    lam = L_2/L_1

    ke =  0.5*(1+mu)*omega_1**2 + 0.5*mu*lam**2*omega_2**2 + mu*lam*omega_1*omega_2*np.cos(phi_1-phi_2)
    
    return ke

    
def lyapunov_exponent(init_phi_1, init_phi_2, init_omega_1, init_omega_2, epsilon=1e-8, dt=1e-3, t_steps=int(8e3), cutoff_target=2e-2, show_plot=False):

    """
    Estimates the largest Lyapunov exponent of a double pendulum system
    using the divergence of two nearby trajectories.

    Parameters
    ----------
    init_phi_1 : float
        Initial angular displacement of the first body in radians.
    init_phi_2 : float
        Initial angular displacement of the second body in radians.
    init_omega_1 : float
        Initial angular velocity of the first body in radians per second.
    init_omega_2 : float
        Initial angular velocity of the second body in radians per second.
    epsilon : float, optional
        Small perturbation added to the initial state for the second trajectory.
        Default is 1e-8.
    dt : float, optional
        Time step for the numerical integration in seconds. Default is 1e-3.
    t_steps : int, optional
        Number of simulation steps. Default is 8000.
    cutoff_target : float, optional
        Maximum divergence value used for fitting the exponential growth region.
        Default is 2e-2.
    show_plot : bool, optional
        If True, plots the divergence and exponential fit. Default is False.

    Returns
    -------
    lyapunov_exponent : float
        Estimated largest Lyapunov exponent of the system.
    """
    #state = np.array([init_phi_1, init_omega_1, init_phi_2, init_omega_2], dtype=float)
    state = np.array([init_phi_1, init_phi_2, init_omega_1, init_omega_2])
    #=======
    initialize_first_body(phi_1=state[0], omega_1=state[2]) 
    #=======
    dtau = dt * np.sqrt(9.81 / L_1)
    time_grid = np.arange(0, t_steps*dtau, dtau)
    #=======
    initialize_second_body(phi_2=state[1], omega_2=state[3])
    #-----
    phi_1, phi_2, omega_1, omega_2 = simulate(dt, t_steps)
    #-----
    #=======
    state = state + np.array([epsilon, epsilon, epsilon, epsilon])
    initialize_first_body(phi_1=state[0], omega_1=state[2]) 
    initialize_second_body(phi_2=state[1], omega_2=state[3])
    phi_1_prime, phi_2_prime, omega_1_prime, omega_2_prime = simulate(dt, t_steps)
    #=======
    delta = np.sqrt((phi_1_prime - phi_1)**2 +
                    (omega_1_prime - omega_1)**2 +
                    (phi_2_prime - phi_2)**2 +
                    (omega_2_prime - omega_2)**2)
    #=======
    if show_plot == True:
        plt.figure(figsize=(10,6), dpi = 300)
        #=======
        plt.axhline(cutoff_target, color='grey', label='cutoff target')
        plt.plot(time_grid, delta, color='blue', label = r'$\delta(t) = ||\boldsymbol{x}(t) - \boldsymbol{y}(t)||$')
        plt.xlabel('Time (s)')
        plt.ylabel(r'$\delta(t)$ (rad)')
        plt.legend()
        plt.tight_layout()
        plt.savefig(f'journal_plots/lyapunov_example_1.png', dpi=400, bbox_inches='tight')
        plt.show()
        #=======
    indices = np.where(delta >= cutoff_target)[0]
    if len(indices) == 0:
        cutoff_index = len(delta)
    else:
        cutoff_index = indices[0]
    cutoff_time_grid = time_grid[:cutoff_index]
    cutoff_delta = delta[:cutoff_index]
    slope, b = np.polyfit(cutoff_time_grid, np.log(cutoff_delta), 1)
    #=======
    if show_plot == True:
        plt.figure(figsize=(10,6), dpi=300)
        plt.plot(cutoff_time_grid, slope*cutoff_time_grid + b, color='k', label=r'$\lambda$t + $\beta$')
        plt.plot(cutoff_time_grid, np.log(cutoff_delta), color='red', linewidth=1, label=r'$\log(\delta(t))$')
        plt.xlabel('Time (s)')
        plt.ylabel(r'log($\delta$(t)) log(rad)')
        plt.tight_layout()
        plt.legend()
        plt.savefig(f'journal_plots/lyapunov_example_2.png', dpi=400, bbox_inches='tight')
        plt.show()
    #=======
    lyapunov_exponent = slope
    
    return lyapunov_exponent


def plot_state_vector(phi1, phi2, w1, w2, dt, t_steps, save_plot=False):
    """
    Plots the time evolution of the state vector components of the system.

    This function visualizes the angular positions (phi1, phi2) and angular
    velocities (w1, w2) of the double pendulum system as functions of time.

    Parameters
    ----------
    phi1 : numpy.ndarray
        Angular displacement of the first pendulum in radians.
    phi2 : numpy.ndarray
        Angular displacement of the second pendulum in radians.
    w1 : numpy.ndarray
        Angular velocity of the first pendulum in rad/s.
    w2 : numpy.ndarray
        Angular velocity of the second pendulum in rad/s.
    dt : float
        Time step between consecutive samples in seconds.
    t_steps : int
        Total number of time steps in the simulation.
    save_plot : bool, optional
        If True, saves the figure to "journal_plots/state_vector.png". Default is False.

    Returns
    -------
    None
    """

    time_grid = np.arange(0, t_steps)*dt

    fig, ax = plt.subplots(2, 2, figsize=(15,6), dpi=300)
    
    ax[0,0].plot(time_grid, phi1, color='k')
    ax[0,0].set_ylabel(r'$\phi$(rad)')
    ax[0,0].set_title('Pendulum 1')
    ax[0,1].plot(time_grid, phi2, color='k')
    ax[0,1].set_title('Pendulum 2')

    ax[1,0].plot(time_grid, w1, color='r')
    ax[1,0].set_xlabel('Time (s)')
    ax[1,0].set_ylabel(r'$\omega$(rad/s)')

    ax[1,1].plot(time_grid, w2, color='r')
    ax[1,1].set_xlabel('Time (s)')

    plt.tight_layout()
    
    if save_plot:
        plt.savefig("journal_plots/state_vector.png", dpi=400, bbox_inches='tight')
    plt.show()


def plot_energies(phi1, phi2, w1, w2, dt, t_steps, save_plot=False):
    """
    Plots the kinetic, potential, and total energy of the system over time.

    This function computes the kinetic energy, potential energy, and total
    energy of the double pendulum system and visualizes their time evolution.

    Parameters
    ----------
    phi1 : numpy.ndarray
        Angular displacement of the first pendulum in radians.
    phi2 : numpy.ndarray
        Angular displacement of the second pendulum in radians.
    w1 : numpy.ndarray
        Angular velocity of the first pendulum in rad/s.
    w2 : numpy.ndarray
        Angular velocity of the second pendulum in rad/s.
    dt : float
        Time step between consecutive samples in seconds.
    t_steps : int
        Total number of time steps in the simulation.
    save_plot : bool, optional
        If True, saves the figure to "journal_plots/energies.png". Default is False.

    Returns
    -------
    None
    """

    time_grid = np.arange(0, t_steps)*dt
    
    ke = get_kinetic_energy(phi1, phi2, w1, w2)
    pe = get_potential_energy(phi1, phi2)
    te = ke+pe

    plt.figure(figsize=(15,6), dpi=300)

    plt.plot(time_grid, ke, color='r', label='Kinetic Energy')
    plt.plot(time_grid, pe, color='b', label='Potential Energy')
    plt.plot(time_grid, te, color='k', label='Total Energy')

    plt.xlabel('Time (s)')
    plt.ylabel(r'Energy ($E_0$)')

    plt.legend(loc='best')
    plt.tight_layout()

    if save_plot:
        plt.savefig("journal_plots/energies.png", dpi=400, bbox_inches='tight')
    plt.show()


def plot_phasespace_projections(phi1, phi2, w1, w2, save_plot=False):
    """
    Plots phase space projections of the double pendulum system.

    This function generates multiple 2D projections of the phase space,
    showing correlations between angular positions (phi1, phi2) and
    angular velocities (w1, w2).

    Parameters
    ----------
    phi1 : numpy.ndarray
        Angular displacement of the first pendulum in radians.
    phi2 : numpy.ndarray
        Angular displacement of the second pendulum in radians.
    w1 : numpy.ndarray
        Angular velocity of the first pendulum in rad/s.
    w2 : numpy.ndarray
        Angular velocity of the second pendulum in rad/s.
    save_plot : bool, optional
        If True, saves the figure to "journal_plots/phasespace_projections.png".
        Default is False.

    Returns
    -------
    None
    """

    fig, ax = plt.subplots(2, 3, figsize=(15,6), dpi=300)
    
    ax[0,0].scatter(phi1, phi2, s=1, color='blue')
    ax[0,0].set_title(r'($\phi_1, \phi_2$)')
    
    ax[0,1].scatter(phi1, w1, s=1, color='red')
    ax[0,1].set_title(r'($\phi_1, \omega_1$)')
    
    ax[0,2].scatter(phi1, w2, s=1, color='green')
    ax[0,2].set_title(r'($\phi_1, \omega_2$)')
    
    ax[1,0].scatter(phi2, w1, s=1, color='orange')
    ax[1,0].set_title(r'($\phi_2, \omega_1$)')
    
    ax[1,1].scatter(phi2, w2, s=1, color='magenta')
    ax[1,1].set_title(r'($\phi_2, \omega_2$)')
    
    ax[1,2].scatter(w1, w2, s=1, color='gold')
    ax[1,2].set_title(r'($\omega_1, \omega_2$)')
    
    for axs in ax.flat:
        axs.set_xticks([])
        axs.set_yticks([])
    
    plt.tight_layout()
    if save_plot:
        plt.savefig("journal_plots/phasespace_projections.png", dpi=400, bbox_inches='tight')
    plt.show()
#!/usr/bin/env python
#
# code to find the ABCD matrix given some input and output beam parameters
#
# written by ChatGPT-4o + RXA
# Aug 2024

import numpy as np
from scipy.optimize import differential_evolution
import argparse

def calculate_q(z, w, wavelength):
    """
    Calculate the complex beam parameter q(z) for a Gaussian beam.

    Parameters:
    z (float): Position along the beam axis (meters).
    w (float): Beam waist size at position z (meters).
    wavelength (float): Wavelength of the beam (meters).

    Returns:
    complex: The complex beam parameter q(z).
    """
    return z + 1j * (np.pi * w**2) / wavelength

def objective(x, q_in, q_out):
    """
    Objective function to minimize the difference between calculated and actual q_out,
    with the constraint AD - BC = 1 enforced by substituting D = (1 + BC) / A.

    Parameters:
    x (list): List of ABCD matrix elements [A, B, C].
    q_in (complex): Complex beam parameter at the input.
    q_out (complex): Complex beam parameter at the output.

    Returns:
    float: The absolute difference between calculated and actual q_out.
    """
    A, B, C = x
    D = (1 + B * C) / A  # Solve for D using the determinant constraint

    q_out_calc = (A * q_in + B) / (C * q_in + D)
    return np.abs(q_out_calc - q_out)

def main(args):
    """
    Main function to calculate the ABCD matrix and decompose it into optical elements.

    Parameters:
    args (argparse.Namespace): Command-line arguments containing beam parameters.
    """

    # Calculate q_in and q_out based on provided beam parameters
    q_in = calculate_q(args.z0_in, args.w_in, args.wavelength)
    q_out = calculate_q(args.z_out, args.w_out, args.wavelength)

    # Set bounds reflecting a 40x microscope objective
    bounds = [
        (0.1, 12),      # A close to 1, allowing for some variation
        (-3, 3),   # B around 0, reflecting no free space in the lens
        (-1000, -200)  # C related to the short focal length of the objective
    ]

    # Perform Differential Evolution with reduced number of variables
    result = differential_evolution(objective, bounds,
                                    args=(q_in, q_out),  # Pass q_in and q_out to the objective function
                                    strategy = 'best1bin',
                                    maxiter = 1000,
                                    init='random',
                                    disp = True,
                                    popsize = 150)

    # Extract the optimal A, B, C
    A_opt, B_opt, C_opt = result.x
    D_opt = (1 + B_opt * C_opt) / A_opt  # Calculate D using the constraint

    # Print the results
    print(f"Optimal A: {A_opt:.4f}, B: {B_opt:.4f}, C: {C_opt:.4f}, D: {D_opt:.4f}")
    print(f"Final Objective Error: {result.fun:.4e}")

    # Decompose the ABCD matrix into distances and lens focal length
    f_opt = -1 / C_opt
    d1_opt = B_opt - D_opt * B_opt / A_opt
    d2_opt = D_opt - 1

    print(f"Focal Length (f): {f_opt:.4f} meters")
    print(f"Distance before lens (d1): {d1_opt:.4f} meters")
    print(f"Distance after lens (d2): {d2_opt:.4f} meters")



if __name__ == "__main__":
    """
    This script calculates the ABCD matrix for a Gaussian beam transformation and
    decomposes it into equivalent optical elements: free space propagation distances
    and a lens with a specific focal length.

    The script uses differential evolution to optimize the ABCD matrix elements while
    satisfying the determinant constraint AD - BC = 1 by explicitly solving for D.
    It then interprets the resulting matrix in terms of distances and focal lengths that
    describe an equivalent optical system.

    Parameters can be provided via command-line arguments:
    - w_in: Beam waist size at input (meters), default: 300 microns
    - z0_in: Position of input beam waist (meters), default: -10 cm
    - w_out: Beam waist size at output (meters), default: 5 microns
    - z_out: Position at output (meters), default: -1 mm
    - wavelength: Wavelength of the beam (meters), default: 1064 nm

    Example usage:
    python script_name.py --w_in 350e-6 --z0_in -0.2 --w_out 6e-6 --z_out -0.002 --wavelength 800e-9
    """

    parser = argparse.ArgumentParser(description="Calculate the ABCD matrix for a Gaussian beam and decompose it into optical elements.")
    parser.add_argument("--w_in", type=float, default=300e-6, help="Beam waist size at input (meters), default: 300 microns")
    parser.add_argument("--z0_in", type=float, default=-0.1, help="Position of input beam waist (meters), default: -10 cm")
    parser.add_argument("--w_out", type=float, default=5e-6, help="Beam waist size at output (meters), default: 5 microns")
    parser.add_argument("--z_out", type=float, default=-0.001, help="Position at output (meters), default: -1 mm")
    parser.add_argument("--wavelength", type=float, default=1064e-9, help="Wavelength of the beam (meters), default: 1064 nm")

    args = parser.parse_args()
    main(args)

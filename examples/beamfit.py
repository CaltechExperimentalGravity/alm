import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import curve_fit
import os

# Set Seaborn theme
sns.set_theme(style="whitegrid")

# LaTeX text rendering for consistency in publication
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "serif",
    "font.size": 10,
    "axes.labelsize": 10,
    "axes.titlesize": 11,
    "legend.fontsize": 8,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "lines.linewidth": 2,
    "lines.markersize": 6,
    "figure.figsize": (7.2, 4.45),  # Aspect ratio for double column figures
    "figure.autolayout": True,
    "axes.grid": True,
    "grid.alpha": 0.5
})

# Set XKCD color palette
colors = sns.xkcd_palette(["red", "denim blue", "green", "orange"])

# Laser wavelength in meters (1064 nm = 1.064e-6 meters)
lambda_laser = 1.064e-6

# Gaussian beam diameter function
def beam_diameter(z, z0, w0):
    """Calculate the beam diameter at distance z.

    Parameters:
    z (array): Array of z distances (meters).
    z0 (float): Waist position (meters).
    w0 (float): Waist radius (meters).

    Returns:
    array: Calculated beam diameters at each z (meters).
    """
    z_R = np.pi * w0**2 / lambda_laser
    return 2 * w0 * np.sqrt(1 + ((z - z0) / z_R)**2)

# Convert values to millimeters
def to_mm(value):
    """Convert meters to millimeters."""
    return value * 1000

# Define directory paths
data_dir = 'data'
figures_dir = 'figures'
filename = os.path.join(data_dir, 'beam_data.csv')

# Create directories if they don't exist
os.makedirs(data_dir, exist_ok=True)
os.makedirs(figures_dir, exist_ok=True)

# Load data from a file or use example data if the file doesn't exist
if os.path.exists(filename):
    # Load data assuming two columns: z (meters), D (meters)
    data = np.loadtxt(filename, delimiter=',')
    z_data, D_data = data[:, 0], data[:, 1]
else:
    print(f"File '{filename}' not found. Using example data.")
    # Example data: z (meters), D (meters) for a 300-micron waist laser beam
    z_data = np.linspace(-0.5, 0.5, 11)  # 1 meter range around the waist
    D_data = beam_diameter(z_data, z0=0, w0=300e-6)  # w0 = 300 microns

# Add Gaussian noise to the data for realistic fitting
np.random.seed(42)  # For reproducibility
z_noise = z_data + np.random.normal(0, 0.001, size=z_data.shape)  # Small noise in z (meters)
D_noise = D_data + np.random.normal(0, 0.00001, size=D_data.shape)  # Small noise in D (meters)

# Fit the noisy data to extract z0 and w0
popt, pcov = curve_fit(beam_diameter, z_noise, D_noise, p0=[np.mean(z_noise), np.min(D_noise)/2])
z0_fit, w0_fit = popt
perr = np.sqrt(np.diag(pcov))  # Standard deviations of the parameters

# Convert fitted parameters and uncertainties to millimeters
z0_fit_mm = to_mm(z0_fit)
w0_fit_mm = to_mm(w0_fit)
perr_mm = to_mm(perr)

# Generate data for plotting the fitted curve and confidence intervals
z_fit = np.linspace(np.min(z_noise), np.max(z_noise), 1000)
D_fit = beam_diameter(z_fit, z0_fit, w0_fit)

# Confidence interval calculation (75% confidence interval)
alpha = 0.25
nstd = 1.15  # 75% confidence interval for normal distribution
D_fit_upper = D_fit + nstd * np.sqrt(np.diag(pcov)[1])
D_fit_lower = D_fit - nstd * np.sqrt(np.diag(pcov)[1])

# Convert fitted curve and confidence interval to millimeters
z_fit_mm = to_mm(z_fit)
D_fit_mm = to_mm(D_fit)
D_fit_upper_mm = to_mm(D_fit_upper)
D_fit_lower_mm = to_mm(D_fit_lower)

# Plot the data, the fit, and the confidence interval using Seaborn
fig, ax = plt.subplots()
sns.scatterplot(x=to_mm(z_noise), y=to_mm(D_noise), ax=ax, color=colors[0], marker='o', label='Noisy Data')
sns.lineplot(x=z_fit_mm, y=D_fit_mm, ax=ax, color=colors[1], label=fr'Fit: $z_0 = {z0_fit_mm:.3f} \pm {perr_mm[0]:.3f}$ mm, $w_0 = {w0_fit_mm:.3f} \pm {perr_mm[1]:.3f}$ mm')

# Fill between for confidence interval
ax.fill_between(z_fit_mm, D_fit_lower_mm, D_fit_upper_mm, color=colors[1], alpha=0.3, label='75% Confidence Interval')

# Customize plot appearance
ax.set_xlabel(r'Distance $z$ (mm)')
ax.set_ylabel(r'Beam Diameter $D(z)$ (mm)')
ax.legend()
ax.set_title(r'Gaussian Beam Fit with Noise and Confidence Interval')
sns.despine()

# Save the plot as a PDF in the figures directory
output_filename = os.path.join(figures_dir, 'beam_fit.pdf')
plt.savefig(output_filename, format='pdf', dpi=300)

# plt.show()  # Commented out as per original code

# Print fitted parameters with uncertainties
print(f"Fitted z0: {z0_fit_mm:.3f} ± {perr_mm[0]:.3f} mm")
print(f"Fitted w0: {w0_fit_mm:.3f} ± {perr_mm[1]:.3f} mm")

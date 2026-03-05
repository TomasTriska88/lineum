import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D
import scipy.special as sp

# Generate a 3D vibrating spherical harmonic (e.g., Hydrogen/Helium orbital analog)
theta = np.linspace(0, np.pi, 60)
phi = np.linspace(0, 2 * np.pi, 60)
theta, phi = np.meshgrid(theta, phi)

# l=2, m=0 spherical harmonic
r0 = np.abs(sp.sph_harm(0, 2, phi, theta).real) 

fig = plt.figure(figsize=(6, 6))
fig.patch.set_facecolor('black')
ax = fig.add_subplot(111, projection='3d')
ax.set_facecolor('black')

# Hide axes
ax.set_axis_off()

plot = [ax.plot_surface(
    r0 * np.sin(theta) * np.cos(phi), 
    r0 * np.sin(theta) * np.sin(phi), 
    r0 * np.cos(theta), 
    color='cyan', alpha=0.6, rstride=1, cstride=1, edgecolor='none'
)]

def update(frame):
    ax.clear()
    ax.set_axis_off()
    ax.set_xlim([-0.5, 0.5])
    ax.set_ylim([-0.5, 0.5])
    ax.set_zlim([-0.5, 0.5])
    
    # Pulse the radius based on frame (cymatic vibration)
    scale = 1.0 + 0.1 * np.sin(frame * 2 * np.pi / 30)
    r = r0 * scale
    
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)
    
    surf = ax.plot_surface(x, y, z, cmap='ocean', alpha=0.8, rstride=1, cstride=1, edgecolor='cyan', linewidth=0.1)
    return surf,

ani = animation.FuncAnimation(fig, update, frames=30, blit=False)
ani.save('cymatic_math_variant.gif', writer='pillow', fps=15)
print("Saved cymatic_math_variant.gif")

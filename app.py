from flask import Flask, send_file, requests
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import random
import string
import datetime
import os
import io

app = Flask(__name__)

# Diamond-Square Algorithm
def diamond_square(size, roughness):
    grid_size = 2 ** size + 1
    grid = np.zeros((grid_size, grid_size))

    # Initialize the corners
    grid[0, 0] = np.random.rand()
    grid[0, grid_size - 1] = np.random.rand()
    grid[grid_size - 1, 0] = np.random.rand()
    grid[grid_size - 1, grid_size - 1] = np.random.rand()

    step_size = grid_size - 1
    while step_size > 1:
        half_step = step_size // 2

        # Diamond step
        for x in range(0, grid_size - 1, step_size):
            for y in range(0, grid_size - 1, step_size):
                avg = (grid[x, y] + grid[x + step_size, y] +
                       grid[x, y + step_size] + grid[x + step_size, y + step_size]) / 4.0
                grid[x + half_step, y + half_step] = avg + (np.random.rand() - 0.5) * roughness * step_size

        # Square step
        for x in range(0, grid_size, half_step):
            for y in range((x + half_step) % step_size, grid_size, step_size):
                sum_val, count = 0, 0
                if x - half_step >= 0:
                    sum_val += grid[x - half_step, y]
                    count += 1
                if x + half_step < grid_size:
                    sum_val += grid[x + half_step, y]
                    count += 1
                if y - half_step >= 0:
                    sum_val += grid[x, y - half_step]
                    count += 1
                if y + half_step < grid_size:
                    sum_val += grid[x, y + half_step]
                    count += 1
                grid[x, y] = sum_val / count + (np.random.rand() - 0.5) * roughness * step_size

        step_size //= 2
        roughness /= 2

    return grid

# Function to create a custom color map
def create_custom_colormap(base_color):
    colors = [
        (1, 1, 1),       # White for low elevation
        base_color,      # Mid-tone for medium elevation
        (0, 0, 0)        # Black for high elevation
    ]
    return LinearSegmentedColormap.from_list("custom_topography", colors, N=256)

@app.route('/')
def generate_image():
    # Get width and height from query parameters, with defaults if not provided
    width = int(request.args.get('width', 1920))
    height = int(request.args.get('height', 1080))
    
    # Define roughness, contour levels, and size for topography generation (adjust as needed)
    roughness = random.uniform(0.5, 1.5)
    contour_levels = random.randint(10, 50)
    size = int(np.log2(max(width, height))) - 1

    # Generate the topography
    topography = diamond_square(size, roughness)
    base_color = (random.uniform(0, 1), random.uniform(0, 1), random.uniform(0, 1))
    custom_cmap = create_custom_colormap(base_color)

    # Plot the topography with the custom color map
    fig, ax = plt.subplots(figsize=(width / 100, height / 100), dpi=100)
    ax.contourf(topography, levels=contour_levels, cmap=custom_cmap)
    ax.axis('off')

    # Save the plot to a BytesIO object instead of a file
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png', bbox_inches='tight', pad_inches=0)
    img_io.seek(0)
    plt.close(fig)

    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
